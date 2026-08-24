"""Voice transcription helpers.

Two transcription backends are supported, tried in order:
1. Groq-hosted Whisper (`whisper-large-v3-turbo`)
2. SpeechRecognition's free Google Web Speech recognizer fallback
"""
from __future__ import annotations

import io
import os
import re

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    from groq import Groq
except Exception:
    Groq = None


LANGUAGE_CODES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Hinglish": "en-IN",
}

WHISPER_LANGUAGE_HINTS = {
    "English": "en",
    "Hindi": "hi",
    "Hinglish": None,
}

HINGLISH_MAP = {
    "doodh": "milk",
    "dudh": "milk",
    "kele": "bananas",
    "kela": "banana",
    "seb": "apples",
    "sebhi": "apples",
    "anda": "eggs",
    "ande": "eggs",
    "roti": "bread",
    "paani": "water",
    "pani": "water",
    "shahad": "honey",
    "chai": "tea",
    "coffee": "coffee",
    "jodo": "add",
    "jod do": "add",
    "add karo": "add",
    "hatao": "remove",
    "nikal do": "remove",
    "badal do": "update",
    "bana do": "prepare",
}


def _groq_api_key() -> str | None:
    """Fetch GROQ_API_KEY checking Streamlit secrets first, then OS env."""
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")


def normalize_hinglish(text: str) -> str:
    """Safely convert Hinglish keywords to English using regex word boundaries."""
    if not text:
        return ""
    result = text
    for source, target in sorted(HINGLISH_MAP.items(), key=lambda x: -len(x[0])):
        pattern = rf"\b{re.escape(source)}\b"
        result = re.sub(pattern, target, result, flags=re.IGNORECASE)
    return result


def _transcribe_with_groq(raw_bytes: bytes, language: str) -> tuple[str | None, str | None]:
    if Groq is None:
        return None, "groq package not installed"
    api_key = _groq_api_key()
    if not api_key:
        return None, "no GROQ_API_KEY configured"
    try:
        client = Groq(api_key=api_key)
        kwargs = {"file": ("command.wav", raw_bytes), "model": "whisper-large-v3-turbo"}
        hint = WHISPER_LANGUAGE_HINTS.get(language)
        if hint:
            kwargs["language"] = hint
        result = client.audio.transcriptions.create(**kwargs)
        text = (getattr(result, "text", None) or "").strip()
        return (text, None) if text else (None, "empty transcript")
    except Exception as exc:
        return None, str(exc)


def _transcribe_with_google(raw_bytes: bytes, language: str) -> tuple[str | None, str | None]:
    if sr is None:
        return None, "Voice recognition dependency is not installed."
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(raw_bytes)) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(
            audio,
            language=LANGUAGE_CODES.get(language, "en-IN"),
        )
        return text, None
    except sr.UnknownValueError:
        return None, "I couldn't understand the recording. Try speaking a little more slowly."
    except sr.RequestError:
        return None, "Speech recognition is temporarily unavailable."
    except Exception as exc:
        return None, f"Voice input failed: {exc}"


def transcribe_audio(audio_file, language: str = "English") -> tuple[str | None, str | None]:
    if not audio_file:
        return None, None

    # Handle UploadedFile objects or raw bytes
    if hasattr(audio_file, "getvalue"):
        raw = audio_file.getvalue()
    elif isinstance(audio_file, bytes):
        raw = audio_file
    else:
        return None, "Invalid audio input format"

    # 1. Try Groq Whisper
    text, groq_error = _transcribe_with_groq(raw, language)
    if text:
        return normalize_hinglish(text), None

    # 2. Try Google Speech Recognition fallback
    text, fallback_error = _transcribe_with_google(raw, language)
    if text:
        return normalize_hinglish(text), None

    return None, fallback_error or groq_error