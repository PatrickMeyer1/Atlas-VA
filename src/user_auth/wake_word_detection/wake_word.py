from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import NamedTemporaryFile
from threading import Lock
import time
from typing import Optional

import imageio_ffmpeg
import numpy as np
from tensorflow import keras
import librosa

_SAMPLE_RATE = 16000
_DURATION = 2.5
_NUM_SAMPLES = int(_SAMPLE_RATE * _DURATION)
_MODEL_NAME = "model.keras"
_MODEL_LOCK = Lock()
_SESSION_LOCK = Lock()
_WWD_MODEL = None
_MODEL_CACHE_DIR = Path(__file__).parent / "models"
_SESSIONS: dict[str, "WwdSession"] = {}

_SESSION_TTL_SECONDS = 120.0

@dataclass
class WwdSession:
    pending_audio: list[np.ndarray] = field(default_factory=list)
    queued_chunks: dict[int, tuple[float, np.ndarray]] = field(default_factory=dict)
    next_chunk_index: int = 0
    last_seen: float = field(default_factory=time.monotonic)
    lock: Lock = field(default_factory=Lock, repr=False)


def _response(
    received_chunk_index: Optional[int] = None,
    score: Optional[float] = None,
    error: Optional[str] = None,
    ww_detected: Optional[bool] = None,
) -> dict[str, object]:
    return {
        "ww_detected": ww_detected,
        "received_chunk_index": received_chunk_index,
        "score": score,
        "error": error,
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


def _load_wwd_model():
    global _WWD_MODEL
    if _WWD_MODEL is not None:
        return _WWD_MODEL

    with _MODEL_LOCK:
        if _WWD_MODEL is None:
            run_dirs = sorted([d for d in _MODEL_CACHE_DIR.iterdir() if d.is_dir()], reverse=True)
            
            if not run_dirs:
                raise FileNotFoundError("No trained models found.")
            
            latest_run = run_dirs[0]
            model_path = latest_run / _MODEL_NAME
            
            print(f"Loading WWD model weights from {model_path}...")
            _WWD_MODEL = keras.models.load_model(model_path)
            
    return _WWD_MODEL


def ensure_wwd_ready():
    return _load_wwd_model()


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


def _get_session(session_id: str) -> WwdSession:
    now = time.monotonic()
    with _SESSION_LOCK:
        _prune_sessions(now)
        session = _SESSIONS.get(session_id)
        if session is None:
            session = WwdSession()
            _SESSIONS[session_id] = session
        session.last_seen = now
        return session

   
def preprocess_audio(audio: np.ndarray) -> np.ndarray:
    # Normalize to [-1, 1]
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    # Pad or truncate
    if len(audio) < _NUM_SAMPLES:
        audio = np.pad(audio, (0, _NUM_SAMPLES - len(audio)))
    else:
        audio = audio[:_NUM_SAMPLES]
    
    return audio


# Define the extract_mfcc with default parameters
def extract_mfcc(audio: np.ndarray, sr: int = 16000, window_sec: float = 0.025, hop_sec: float = 0.010, n_mfcc: int = 13) -> np.ndarray:

    n_fft = int(window_sec * sr)       # window length in samples
    hop_length = int(hop_sec * sr)     # hop length in samples

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length
    )
    return mfcc


def _detect_wake_word(audio: np.ndarray) -> tuple[bool, float]:
    model = _load_wwd_model()
    audio = preprocess_audio(audio)
    mfcc = extract_mfcc(audio)
    x = mfcc[..., np.newaxis]
    x = np.expand_dims(x, axis=0)

    prob = float(model.predict(x, verbose=0).ravel()[0])
    detected = (prob > 0.5)

    return detected, prob


def _flush_session(session: WwdSession) -> tuple[bool, float]:
    if len(session.pending_audio) < 5:
        return False, 0.0

    combined_audio = np.concatenate(session.pending_audio[:5])
    detected, score = _detect_wake_word(combined_audio)

    session.pending_audio.pop(0)
    
    return detected, score


def _flush_and_detect(session: WwdSession) -> tuple[bool, float, Optional[str]]:
    try:
        detected, score = _flush_session(session)
        return detected, score, None
    except Exception as exc:
        session.pending_audio.clear()
        return False, 0.0, f"Wake word inference failed: {exc}"


def _consume_ready_chunks(session: WwdSession) -> tuple[bool, float, Optional[str]]:
    detected = False
    score = 0.0
    error_text = None

    while session.next_chunk_index in session.queued_chunks:
        _, audio = session.queued_chunks.pop(session.next_chunk_index)

        session.pending_audio.append(audio)

        if len(session.pending_audio) >= 5:
            detected, score, flush_error = _flush_and_detect(session)
            if flush_error:
                error_text = flush_error

        session.next_chunk_index += 1

    return detected, score, error_text


def detect_ww_in_audio_bytes(
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
            return _response(error=f"Failed to decode WWD audio chunk: {exc}")

    if audio.size == 0:
        with session.lock:
            return _response(error="Decoded WWD audio chunk was empty.")

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

        detected, score, error_text = _consume_ready_chunks(session)

        if detected:
            session.pending_audio.clear()
            session.queued_chunks.clear()

        return _response(
            received_chunk_index=index_value,
            score=score,
            error=error_text,
            ww_detected=detected
        )


ingest_audio_chunk = detect_ww_in_audio_bytes
