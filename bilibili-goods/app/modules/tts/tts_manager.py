"""TTS 统一调度器。"""

from __future__ import annotations

from app.modules.tts.chattts_engine import synthesize_with_chattts
from app.modules.tts.cosyvoice_engine import synthesize_with_cosyvoice


def synthesize(text: str, engine: str = "chattts", voice: str = "female_a") -> dict:
    """按引擎名调度 TTS。"""
    if engine == "cosyvoice":
        return synthesize_with_cosyvoice(text=text, voice=voice)
    return synthesize_with_chattts(text=text, voice=voice)
