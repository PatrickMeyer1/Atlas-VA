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
import torch
import whisper

_SAMPLE_RATE = 16000
_MODEL_NAME = "tiny.en"
_MODEL_LOCK = Lock()
_SESSION_LOCK = Lock()
_ASR_MODEL = None
_MODEL_CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache" / "whisper"
_SESSIONS: dict[str, "AsrSession"] = {}

_SESSION_TTL_SECONDS = 120.0
_MIN_SPEECH_SECONDS = 1.2
_MAX_BUFFER_SECONDS = 6.0
_SILENCE_RMS_THRESHOLD = 0.01


@dataclass
class AsrSession:
    transcript_text: str = ""
    pending_audio: list[np.ndarray] = field(default_factory=list)
    queued_chunks: dict[int, tuple[float, np.ndarray, float, bool]] = field(default_factory=dict)
    pending_seconds: float = 0.0
    next_chunk_index: int = 0
    last_applied_chunk_index: int = -1
    last_seen: float = field(default_factory=time.monotonic)
    lock: Lock = field(default_factory=Lock, repr=False)


def _clean_text(text: Optional[str]) -> str:
    return " ".join((text or "").strip().split())


def _response(
    session: AsrSession,
    *,
    delta: str = "",
    speech_detected: bool = False,
    duration_seconds: float = 0.0,
    received_chunk_index: Optional[int] = None,
    ignored: bool = False,
    error: Optional[str] = None,
    updated: Optional[bool] = None,
) -> dict[str, object]:
    if updated is None:
        updated = bool(delta)

    return {
        "text": session.transcript_text,
        "delta": delta,
        "updated": updated,
        "has_text": bool(session.transcript_text),
        "speech_detected": speech_detected,
        "duration_seconds": round(duration_seconds, 2),
        "buffered_seconds": round(session.pending_seconds, 2),
        "applied_through_index": session.last_applied_chunk_index,
        "received_chunk_index": received_chunk_index,
        "ignored": ignored,
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


def _load_asr_model():
    global _ASR_MODEL
    if _ASR_MODEL is not None:
        return _ASR_MODEL

    with _MODEL_LOCK:
        if _ASR_MODEL is None:
            _MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            _ASR_MODEL = whisper.load_model(_MODEL_NAME, download_root=str(_MODEL_CACHE_DIR))

    return _ASR_MODEL


def ensure_asr_ready():
    return _load_asr_model()


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


def _get_session(session_id: str) -> AsrSession:
    now = time.monotonic()
    with _SESSION_LOCK:
        _prune_sessions(now)
        session = _SESSIONS.get(session_id)
        if session is None:
            session = AsrSession()
            _SESSIONS[session_id] = session
        session.last_seen = now
        return session


def _merge_text(existing_text: str, new_text: str) -> str:
    existing = _clean_text(existing_text)
    incoming = _clean_text(new_text)

    if not incoming:
        return existing
    if not existing:
        return incoming
    if existing.lower().endswith(incoming.lower()):
        return existing

    existing_words = existing.split()
    incoming_words = incoming.split()
    max_overlap = min(len(existing_words), len(incoming_words), 8)

    for overlap in range(max_overlap, 0, -1):
        existing_tail = " ".join(existing_words[-overlap:]).lower()
        incoming_head = " ".join(incoming_words[:overlap]).lower()
        if existing_tail == incoming_head:
            merged_tail = " ".join(incoming_words[overlap:])
            return _clean_text(f"{existing} {merged_tail}")

    return _clean_text(f"{existing} {incoming}")


def _speech_rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio))))


def _transcribe_audio(audio: np.ndarray) -> str:
    model = _load_asr_model()
    result = model.transcribe(
        audio,
        fp16=torch.cuda.is_available(),
        language="en",
        task="transcribe",
        condition_on_previous_text=False,
        temperature=0.0,
        verbose=False,
        word_timestamps=False,
        without_timestamps=True,
        beam_size=1,
        best_of=1,
    )
    return _clean_text(result.get("text"))


def _flush_session(session: AsrSession) -> str:
    if not session.pending_audio:
        return ""

    combined_audio = np.concatenate(session.pending_audio)
    session.pending_audio.clear()
    session.pending_seconds = 0.0

    return _transcribe_audio(combined_audio)


def _flush_and_merge(session: AsrSession) -> tuple[str, Optional[str]]:
    try:
        flushed_text = _flush_session(session)
    except Exception as exc:
        session.pending_audio.clear()
        session.pending_seconds = 0.0
        return "", str(exc)

    if flushed_text:
        session.transcript_text = _merge_text(session.transcript_text, flushed_text)

    return flushed_text, None


def _consume_ready_chunks(session: AsrSession) -> tuple[str, Optional[str]]:
    new_text = ""
    error_text = None

    while session.next_chunk_index in session.queued_chunks:
        _, audio, duration_seconds, speech_detected = session.queued_chunks.pop(session.next_chunk_index)

        if speech_detected:
            session.pending_audio.append(audio)
            session.pending_seconds += duration_seconds

        should_flush = session.pending_seconds >= _MAX_BUFFER_SECONDS or (
            not speech_detected and session.pending_seconds >= _MIN_SPEECH_SECONDS
        )

        if should_flush:
            flushed_text, flush_error = _flush_and_merge(session)
            if flush_error:
                error_text = flush_error
            if flushed_text:
                new_text = flushed_text

        session.last_applied_chunk_index = session.next_chunk_index
        session.next_chunk_index += 1

    return new_text, error_text


def transcribe_audio_bytes(
    chunk_bytes: bytes,
    mimetype: Optional[str] = None,
    session_id: str = "default",
    chunk_index: Optional[int] = None,
    chunk_started_at_ms: Optional[float] = None,
) -> dict[str, object]:
    session = _get_session(session_id)

    if not chunk_bytes:
        with session.lock:
            return _response(session)

    try:
        audio = _decode_audio_bytes(chunk_bytes, mimetype=mimetype)
    except RuntimeError as exc:
        with session.lock:
            return _response(session, error=str(exc))

    duration_seconds = float(audio.shape[0]) / float(_SAMPLE_RATE)
    if audio.size == 0 or duration_seconds < 0.15:
        with session.lock:
            return _response(session, duration_seconds=duration_seconds)

    speech_detected = _speech_rms(audio) >= _SILENCE_RMS_THRESHOLD

    with session.lock:
        index_value = session.next_chunk_index if chunk_index is None else int(chunk_index)
        started_at_ms = 0.0 if chunk_started_at_ms is None else float(chunk_started_at_ms)

        if index_value < session.next_chunk_index:
            return _response(
                session,
                speech_detected=speech_detected,
                duration_seconds=duration_seconds,
                received_chunk_index=index_value,
                ignored=True,
            )

        existing_chunk = session.queued_chunks.get(index_value)
        if existing_chunk is not None and existing_chunk[0] <= started_at_ms:
            return _response(
                session,
                speech_detected=speech_detected,
                duration_seconds=duration_seconds,
                received_chunk_index=index_value,
                ignored=True,
            )

        session.queued_chunks[index_value] = (
            started_at_ms,
            audio,
            duration_seconds,
            speech_detected,
        )

        new_text, error_text = _consume_ready_chunks(session)

        return _response(
            session,
            delta=new_text,
            speech_detected=speech_detected,
            duration_seconds=duration_seconds,
            received_chunk_index=index_value,
            error=error_text,
        )


ingest_audio_chunk = transcribe_audio_bytes


def finalize_session(session_id: str = "default") -> dict[str, object]:
    session = _get_session(session_id)
    with session.lock:
        new_text, error_text = _consume_ready_chunks(session)

        if session.pending_audio:
            flushed_text, flush_error = _flush_and_merge(session)
            if flush_error:
                error_text = flush_error
            if flushed_text:
                new_text = _clean_text(f"{new_text} {flushed_text}")

        return _response(session, delta=new_text, error=error_text)
