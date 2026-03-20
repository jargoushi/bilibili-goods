"""ChatTTS 引擎占位实现。"""

from __future__ import annotations

from pathlib import Path

from app.config import settings


def synthesize_with_chattts(text: str, voice: str = "female_a") -> dict:
    """生成 TTS 结果（占位）。

    TODO: 接入真实 ChatTTS 推理。
    """
    out = settings.output_dir / "audio"
    out.mkdir(parents=True, exist_ok=True)
    fake_audio = out / "chattts_output.wav"
    # 占位写入文本文件，避免流程断开。
    fake_audio.write_text(f"TODO: ChatTTS -> {voice}\n{text}", encoding="utf-8")
    return {"engine": "chattts", "audio_path": str(fake_audio), "duration_sec": 0}
