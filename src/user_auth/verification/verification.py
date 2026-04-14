from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import NamedTemporaryFile
from threading import Lock
import time
from typing import Optional
from speechbrain.inference.speaker import EncoderClassifier

import imageio_ffmpeg
import numpy as np
from numpy.linalg import norm
import torch
import json

_SAMPLE_RATE = 16000
_MODEL_LOCK = Lock()
_SESSION_LOCK = Lock()
_VERIFICATION_MODEL = None
_SESSIONS: dict[str, "VerificationSession"] = {}

_SESSION_TTL_SECONDS = 120.0

@dataclass
class VerificationSession:
    pending_audio: list[np.ndarray] = field(default_factory=list)
    queued_chunks: dict[int, tuple[float, np.ndarray]] = field(default_factory=dict)
    next_chunk_index: int = 0
    last_seen: float = field(default_factory=time.monotonic)
    lock: Lock = field(default_factory=Lock, repr=False)


def _response(
    received_chunk_index: Optional[int] = None,
    score: Optional[float] = None,
    error: Optional[str] = None,
    verified: Optional[bool] = None,
    name: Optional[str] = None,
) -> dict[str, object]:
    return {
        "verified": verified,
        "received_chunk_index": received_chunk_index,
        "score": score,
        "error": error,
        "name": name,
    }


def _suffix_for_mimetype(mimetype: Optional[str]) -> str:
    value = (mimetype or "").lower()
    if "webm" in value:
        return ".webm"
    if "ogg" in value or "opus" in value:
        return ".ogg"
    if "wav" in value:
        return ".wav"
    if "mpeg" in value or "mp3" in value:
        return ".mp3"
    if "mp4" in value or "m4a" in value:
        return ".m4a"
    return ".bin"


def _load_verification_model():
    global _VERIFICATION_MODEL
    if _VERIFICATION_MODEL is not None:
        return _VERIFICATION_MODEL

    with _MODEL_LOCK:
        if _VERIFICATION_MODEL is None:
            _VERIFICATION_MODEL = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
            
    return _VERIFICATION_MODEL


def ensure_verification_ready():
    return _load_verification_model()


def _decode_audio_file(audio_path: str, sample_rate: int = _SAMPLE_RATE) -> np.ndarray:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        "-nostdin",
        "-threads",
        "0",
        "-i",
        audio_path,
        "-f",
        "s16le",
        "-ac",
        "1",
        "-acodec",
        "pcm_s16le",
        "-ar",
        str(sample_rate),
        "-",
    ]

    try:
        out = run(cmd, capture_output=True, check=True).stdout
    except CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"Failed to decode audio chunk: {stderr}") from exc

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


def _decode_audio_bytes(
    chunk_bytes: bytes,
    mimetype: Optional[str] = None,
    sample_rate: int = _SAMPLE_RATE,
) -> np.ndarray:
    suffix = _suffix_for_mimetype(mimetype)
    temp_path = None

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(chunk_bytes)
            temp_path = temp_file.name

        return _decode_audio_file(temp_path, sample_rate=sample_rate)
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass


def _prune_sessions(now: float) -> None:
    expired = [
        session_id
        for session_id, session in _SESSIONS.items()
        if now - session.last_seen > _SESSION_TTL_SECONDS
    ]
    for session_id in expired:
        _SESSIONS.pop(session_id, None)


def _get_session(session_id: str) -> VerificationSession:
    now = time.monotonic()
    with _SESSION_LOCK:
        _prune_sessions(now)
        session = _SESSIONS.get(session_id)
        if session is None:
            session = VerificationSession()
            _SESSIONS[session_id] = session
        session.last_seen = now
        return session

   
def _preprocess_audio(audio: np.ndarray) -> torch.Tensor:
    # Normalize to [-1, 1]
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
    
    return torch.from_numpy(audio).float().unsqueeze(0)


def _cosine_similarity(A: np.ndarray, B: np.ndarray) -> float:
    denom = (norm(A) * norm(B))
    if denom == 0:
        return 0.0
    return float(np.dot(A, B) / denom)


def compute_embedding_ecapa(signal: torch.Tensor) -> np.ndarray:
    # Compute embedding
    classifier = _load_verification_model()
    with torch.no_grad():
        embedding = classifier.encode_batch(signal)
    return np.array(embedding.squeeze().cpu().tolist())


def _verify(audio: np.ndarray) -> tuple[bool, float, str | None]:
    signal = _preprocess_audio(audio)
    current_embedding = compute_embedding_ecapa(signal)

    with open(Path(__file__).with_name("enrolment_embeddings.json"), "r", encoding="utf-8") as f:
        enrolments = json.load(f)
    
    best_name = None
    best_score = -1
    for name, embedding in enrolments.items():
        enrolled_embedding = np.array(embedding)
        score = _cosine_similarity(current_embedding, enrolled_embedding)

        if score > best_score:
            best_score = score
            best_name = name

    verified = best_score > 0.34
    return verified, best_score, best_name


def _flush_session(session: VerificationSession) -> tuple[bool, float, str | None]:
    if len(session.pending_audio) < 5:
        return False, 0.0, None

    combined_audio = np.concatenate(session.pending_audio[:5])
    verified, best_score, best_name = _verify(combined_audio)

    session.pending_audio.pop(0)
    
    return verified, best_score, best_name


def _flush_and_detect(session: VerificationSession) -> tuple[bool, float, str | None, Optional[str]]:
    try:
        verified, best_score, best_name = _flush_session(session)
        return verified, best_score, best_name, None
    except Exception as exc:
        session.pending_audio.clear()
        return False, 0.0, None, f"Verification failed: {exc}"


def _consume_ready_chunks(session: VerificationSession) -> tuple[bool, float, str | None, Optional[str]]:
    verified = False
    best_score = 0.0
    best_name = None
    error_text = None

    while session.next_chunk_index in session.queued_chunks:
        _, audio = session.queued_chunks.pop(session.next_chunk_index)

        session.pending_audio.append(audio)

        if len(session.pending_audio) >= 5:
            verified, best_score, best_name, flush_error = _flush_and_detect(session)
            if flush_error:
                error_text = flush_error
    
        session.next_chunk_index += 1

        if verified:
                return verified, best_score, best_name, error_text

    return verified, best_score, best_name, error_text


def verify_audio_bytes(
    chunk_bytes: bytes,
    mimetype: Optional[str] = None,
    session_id: str = "default",
    chunk_index: Optional[int] = None,
    chunk_started_at_ms: Optional[float] = None,
) -> dict[str, object]:
    session = _get_session(session_id)

    if not chunk_bytes:
        with session.lock:
            return _response(error="Audio chunk was empty.")

    try:
        audio = _decode_audio_bytes(chunk_bytes, mimetype=mimetype)
    except RuntimeError as exc:
        with session.lock:
            return _response(error=f"Failed to decode verification audio chunk: {exc}")

    if audio.size == 0:
        with session.lock:
            return _response(error="Decoded verification audio chunk was empty.")

    with session.lock:
        index_value = session.next_chunk_index if chunk_index is None else int(chunk_index)
        started_at_ms = 0.0 if chunk_started_at_ms is None else float(chunk_started_at_ms)

        if index_value < session.next_chunk_index:
            return _response(received_chunk_index=index_value)

        existing_chunk = session.queued_chunks.get(index_value)
        if existing_chunk is not None and existing_chunk[0] <= started_at_ms:
            return _response(received_chunk_index=index_value)

        session.queued_chunks[index_value] = (
            started_at_ms,
            audio
        )

        verified, best_score, best_name, error_text = _consume_ready_chunks(session)

        if verified:
            session.pending_audio.clear()
            session.queued_chunks.clear()

        return _response(
            received_chunk_index=index_value,
            score=best_score,
            error=error_text,
            name=best_name,
            verified=verified
        )


ingest_audio_chunk = verify_audio_bytes