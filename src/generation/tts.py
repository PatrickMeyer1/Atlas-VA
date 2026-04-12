from __future__ import annotations

import asyncio
from dataclasses import dataclass
import re
from typing import Any, Dict, Iterator, Optional

try:
    import edge_tts
except ImportError:
    edge_tts = None


@dataclass(frozen=True)
class TtsStyle:
    voice: str = "en-CA-ClaraNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"
    browser_rate: float = 1.0
    browser_pitch: float = 1.0
    browser_volume: float = 1.0


_PROSODY_TEMPLATES: Dict[str, TtsStyle] = {
    "neutral_response": TtsStyle(
        voice="en-CA-ClaraNeural",
        rate="+0%",
        pitch="+0Hz",
        volume="+0%",
        browser_rate=1.0,
        browser_pitch=1.0,
        browser_volume=1.0,
    ),
    "informative": TtsStyle(
        voice="en-CA-ClaraNeural",
        rate="-5%",
        pitch="+0Hz",
        volume="+5%",
        browser_rate=0.98,
        browser_pitch=1.0,
        browser_volume=1.0,
    ),
    "reinforce_positive": TtsStyle(
        voice="en-CA-ClaraNeural",
        rate="+10%",
        pitch="+10Hz",
        volume="+5%",
        browser_rate=1.08,
        browser_pitch=1.18,
        browser_volume=1.0,
    ),
    "reassuring": TtsStyle(
        voice="en-CA-ClaraNeural",
        rate="-20%",
        pitch="-5Hz",
        volume="-10%",
        browser_rate=0.95,
        browser_pitch=0.95,
        browser_volume=0.92,
    ),
    "gentle_check_in": TtsStyle(
        voice="en-CA-ClaraNeural",
        rate="-20%",
        pitch="-10Hz",
        volume="-15%",
        browser_rate=0.9,
        browser_pitch=0.88,
        browser_volume=0.9,
    ),
    "clarify_intent": TtsStyle(
        voice="en-CA-ClaraNeural",
        rate="-10%",
        pitch="+0Hz",
        volume="+0%",
        browser_rate=0.95,
        browser_pitch=1.0,
        browser_volume=1.0,
    ),
}

_INTENT_STYLE_NAMES: Dict[str, str] = {
    "oos": "reassuring",
    "greetings": "reinforce_positive",
    "goodbye": "reassuring",
    "timer": "informative",
    "weather": "informative",
    "get_plant_sunlight": "informative",
    "get_plant_watering_care": "informative",
    "get_plant_cycle": "informative",
    "get_plant_edibility": "informative",
    "search_plants_by_environment": "informative",
    "move": "informative",
    "plant": "reinforce_positive",
    "water": "informative",
    "till": "informative",
    "pickup_tool": "informative",
    "pickup_seed": "reinforce_positive",
    "fill_water": "informative",
    "restart": "reassuring",
    "game_help": "reinforce_positive",
}


def sanitize_for_speech(text: Any) -> str:
    value = "" if text is None else str(text)
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def style_for_intent(intent: Optional[str]) -> TtsStyle:
    if not intent:
        return _PROSODY_TEMPLATES["neutral_response"]
    key = str(intent).strip().lower()
    style_name = _INTENT_STYLE_NAMES.get(key, "neutral_response")
    return _PROSODY_TEMPLATES[style_name]


def build_tts_payload(text: Any, intent: Optional[str] = None) -> Dict[str, Any]:
    cleaned = sanitize_for_speech(text)
    style = style_for_intent(intent)
    intent_key = str(intent).strip().lower() if intent else ""
    return {
        "text": cleaned,
        "intent": intent_key,
        "voice": style.voice,
        "rate": style.rate,
        "pitch": style.pitch,
        "volume": style.volume,
        "browser_rate": style.browser_rate, # Fallbacks if edge-tts is not available
        "browser_pitch": style.browser_pitch,
        "browser_volume": style.browser_volume,
        "apologetic": intent_key == "oos",
    }


def server_tts_available() -> bool:
    return edge_tts is not None


def stream_tts_audio(payload: Dict[str, Any]) -> Iterator[bytes]:
    if edge_tts is None:
        raise RuntimeError("Server-side TTS is unavailable because edge-tts is not installed.")

    text = sanitize_for_speech(payload.get("text"))
    if not text:
        raise ValueError("Cannot synthesize empty speech text.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    communicate = edge_tts.Communicate(
        text=text,
        voice=str(payload.get("voice") or _PROSODY_TEMPLATES["neutral_response"].voice),
        rate=str(payload.get("rate") or _PROSODY_TEMPLATES["neutral_response"].rate),
        pitch=str(payload.get("pitch") or _PROSODY_TEMPLATES["neutral_response"].pitch),
        volume=str(payload.get("volume") or _PROSODY_TEMPLATES["neutral_response"].volume),
    )

    stream = communicate.stream()

    try:
        while True:
            try:
                chunk = loop.run_until_complete(stream.__anext__())
            except StopAsyncIteration:
                break

            if chunk.get("type") == "audio":
                data = chunk.get("data")
                if data:
                    yield data
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()
