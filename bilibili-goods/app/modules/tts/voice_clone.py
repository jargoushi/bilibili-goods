"""声音克隆占位模块。"""

from __future__ import annotations


def train_voice_clone(sample_audio_paths: list[str], speaker_name: str) -> dict:
    """训练专属音色（占位）。"""
    # TODO: 接入 GPT-SoVITS 训练流程。
    return {
        "speaker_name": speaker_name,
        "sample_count": len(sample_audio_paths),
        "status": "TODO",
        "message": "当前为占位实现，后续接入 GPT-SoVITS。",
    }
