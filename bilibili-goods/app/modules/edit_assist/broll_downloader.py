"""Broll 下载器。"""

from __future__ import annotations

from pathlib import Path

from app.services.crawler_engine import crawler_engine


def download_broll(urls: list[str], output_dir: Path) -> list[str]:
    """下载 Broll 素材（基础版）。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for idx, url in enumerate(urls, start=1):
        dest = output_dir / f"broll_{idx:03d}.mp4"
        try:
            crawler_engine.download_file(url, dest)
            paths.append(str(dest))
        except Exception:
            # TODO: 增加失败重试和断点续传。
            continue
    return paths
