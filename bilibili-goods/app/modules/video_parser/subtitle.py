"""字幕提取模块。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx


def fetch_subtitle_text(bvid: str, cid: int) -> str:
    """抓取字幕并返回纯文本（带时间戳）。"""
    try:
        return asyncio.run(_fetch_subtitle_text_async(bvid=bvid, cid=cid))
    except Exception:
        # TODO: 接入日志系统后替换为结构化错误输出。
        return ""


def save_subtitle_text(text: str, target_path: Path) -> Path:
    """保存字幕文本到文件。"""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(text, encoding="utf-8")
    return target_path


async def _fetch_subtitle_text_async(bvid: str, cid: int) -> str:
    from bilibili_api import video

    v = video.Video(bvid=bvid, credential=None)
    subtitle_info = await v.get_subtitle(cid=cid)
    subtitles = subtitle_info.get("subtitles", [])
    if not subtitles:
        return ""

    # 优先中文字幕。
    target = subtitles[0]
    for sub in subtitles:
        if "zh" in str(sub.get("lan", "")):
            target = sub
            break

    sub_url = str(target.get("subtitle_url") or "")
    if not sub_url:
        return ""
    if sub_url.startswith("//"):
        sub_url = "https:" + sub_url

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(sub_url)
        resp.raise_for_status()
        data = resp.json()

    lines: list[str] = []
    for row in data.get("body") or []:
        start = _fmt_seconds(float(row.get("from", 0)))
        content = str(row.get("content") or "").strip()
        if content:
            lines.append(f"[{start}] {content}")
    return "\n".join(lines)


def subtitle_to_json(text: str) -> str:
    """字幕纯文本转 JSON 字符串，便于后续结构化处理。"""
    rows = []
    for line in text.splitlines():
        rows.append({"line": line})
    return json.dumps({"rows": rows}, ensure_ascii=False)


def _fmt_seconds(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"
