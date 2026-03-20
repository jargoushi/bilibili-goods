"""对标视频解析器（元信息、封面、字幕、可选视频下载）。"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
import re
import subprocess
from typing import Any

import httpx

from app.config import settings
from app.modules.data_store.models import VideoRecord
from app.modules.video_parser.subtitle import fetch_subtitle_text, save_subtitle_text
from app.services.crawler_engine import crawler_engine


BV_PATTERN = re.compile(r"(BV[a-zA-Z0-9]{10})")


def parse_video_url(video_url: str, download_video: bool = False) -> VideoRecord:
    """解析单个 B 站视频链接。

    返回 VideoRecord，包含后续链路需要的核心字段。
    """
    bvid = resolve_bvid(video_url)
    info = fetch_video_info(bvid)

    title = str(info.get("title") or "")
    safe_title = sanitize_filename(title)
    video_dir = settings.video_output_dir / f"{bvid}_{safe_title}"
    video_dir.mkdir(parents=True, exist_ok=True)

    # 下载封面（失败不阻断主流程）。
    cover_url = str(info.get("pic") or "")
    cover_path = None
    if cover_url:
        cover_path = str(video_dir / "cover.jpg")
        try:
            crawler_engine.download_file(cover_url, Path(cover_path))
        except Exception:
            cover_path = None

    # 抓字幕文本。
    subtitle_text = ""
    subtitle_path = None
    cid = int(info.get("cid") or 0)
    if cid:
        subtitle_text = fetch_subtitle_text(bvid=bvid, cid=cid)
        if subtitle_text:
            subtitle_path = str(save_subtitle_text(subtitle_text, video_dir / "subtitle.txt"))

    # 可选下载视频文件（依赖 yutto）。
    video_path = None
    if download_video:
        video_path = try_download_video(video_url=video_url, output_dir=video_dir)

    owner = info.get("owner") or {}
    record = VideoRecord(
        source_url=video_url,
        title=title,
        bvid=bvid,
        aid=int(info.get("aid") or 0) or None,
        cover_url=cover_url or None,
        cover_path=cover_path,
        video_path=video_path,
        subtitle_text=subtitle_text,
        subtitle_path=subtitle_path,
        up_name=str(owner.get("name") or "") or None,
        up_mid=int(owner.get("mid") or 0) or None,
        published_at=str(info.get("pubdate") or "") or None,
    )
    return record


def resolve_bvid(raw_input: str) -> str:
    """从 URL/BV 号中解析标准 BVID。"""
    text = raw_input.strip()
    match = BV_PATTERN.search(text)
    if match:
        return match.group(1)

    # 尝试跟随跳转获取最终链接。
    if text.startswith(("http://", "https://")):
        try:
            with httpx.Client(follow_redirects=True, timeout=20) as client:
                final_url = str(client.get(text).url)
            match = BV_PATTERN.search(final_url)
            if match:
                return match.group(1)
        except Exception:
            pass
    raise ValueError(f"无法解析 BV 号: {raw_input}")


def fetch_video_info(bvid: str) -> dict[str, Any]:
    """拉取 B 站视频元信息。"""
    try:
        return asyncio.run(_fetch_video_info_async(bvid))
    except Exception as exc:
        raise RuntimeError(f"获取视频信息失败: {bvid}") from exc


async def _fetch_video_info_async(bvid: str) -> dict[str, Any]:
    from bilibili_api import video

    v = video.Video(bvid=bvid, credential=None)
    info = await v.get_info()
    return info


def try_download_video(video_url: str, output_dir: Path) -> str | None:
    """调用 yutto 下载视频文件（可选能力）。"""
    # TODO: 后续可切换到统一任务队列异步下载。
    cmd = [
        "yutto",
        "download",
        video_url,
        "-d",
        str(output_dir),
        "--no-danmaku",
        "--no-progress",
        "--no-color",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        return None

    if proc.returncode != 0:
        return None

    files = sorted(output_dir.rglob("*.mp4"))
    return str(files[0]) if files else None


def sanitize_filename(name: str) -> str:
    """清理文件名非法字符。"""
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", name).strip()
    return clean[:80] or "untitled"


def record_to_dict(record: VideoRecord) -> dict[str, Any]:
    """dataclass 转 dict，便于 API 返回。"""
    return asdict(record)
