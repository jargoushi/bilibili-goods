"""CosyVoice 引擎占位实现。"""

from __future__ import annotations

from app.config import settings


def synthesize_with_cosyvoice(text: str, voice: str = "female_default") -> dict:
    """生成 TTS 结果（占位）。"""
    out = settings.output_dir / "audio"
    out.mkdir(parents=True, exist_ok=True)
    fake_audio = out / "cosyvoice_output.wav"
    fake_audio.write_text(f"TODO: CosyVoice -> {voice}\n{text}", encoding="utf-8")
    return {"engine": "cosyvoice", "audio_path": str(fake_audio), "duration_sec": 0}
