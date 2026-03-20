"""SRT 字幕生成。"""

from __future__ import annotations

from pathlib import Path


def generate_srt_from_lines(lines: list[str], target_path: Path, segment_sec: int = 3) -> Path:
    """根据文本行生成简单 SRT。"""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[str] = []
    current = 0
    for idx, text in enumerate(lines, start=1):
        start = _fmt_srt_time(current)
        end = _fmt_srt_time(current + segment_sec)
        rows.extend([str(idx), f"{start} --> {end}", text, ""])
        current += segment_sec
    target_path.write_text("\n".join(rows), encoding="utf-8")
    return target_path


def _fmt_srt_time(total_sec: int) -> str:
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d},000"
