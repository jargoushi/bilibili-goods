#!/usr/bin/env python3
"""
下载单个 B 站视频，并导出字幕与 UP 主置顶评论楼（一级+二级）中的评论内容。

依赖：
  - yutto
  - ffmpeg（需在 PATH 中可用）
  - bilibili-api-python

示例：
  python bili_fetch.py --url "https://www.bilibili.com/video/BV1xx411c7mD" --out-dir ./output --cookie-file ./cookie.txt --subtitle-format srt
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bilibili_api import Credential, comment, video


BV_PATTERN = re.compile(r"(BV[a-zA-Z0-9]{10})")
AV_PATTERN = re.compile(r"\bav(\d+)\b", re.IGNORECASE)


@dataclass
class VideoIdentity:
    bvid: str | None
    aid: int | None
    source_url: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="下载 B 站视频与字幕，并导出 UP 主置顶评论楼（一级+二级）评论为 JSON。"
    )
    parser.add_argument("--url", required=True, help="B 站视频链接，或直接传 BV/av 号。")
    parser.add_argument(
        "--out-dir",
        default="./output",
        help="输出目录，默认：./output",
    )
    parser.add_argument(
        "--cookie-file",
        default=None,
        help="Cookie 文件路径（支持 Netscape 格式，或包含 SESSDATA 的 JSON/文本）。",
    )
    parser.add_argument(
        "--subtitle-format",
        default="srt",
        choices=["srt", "vtt", "lrc", "json"],
        help="字幕输出格式，默认：srt",
    )
    return parser.parse_args()


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[<>:\"/\\|?*\x00-\x1F]", "_", name).strip()
    return name[:80] or "未命名"


def normalize_url(raw: str) -> str:
    if raw.startswith(("http://", "https://")):
        return raw
    if BV_PATTERN.search(raw) or AV_PATTERN.search(raw):
        return f"https://www.bilibili.com/video/{raw.strip()}"
    return raw.strip()


def resolve_video_identity(raw_input: str) -> VideoIdentity:
    text = raw_input.strip()
    match_bv = BV_PATTERN.search(text)
    if match_bv:
        return VideoIdentity(bvid=match_bv.group(1), aid=None, source_url=normalize_url(text))

    match_av = AV_PATTERN.search(text)
    if match_av:
        return VideoIdentity(bvid=None, aid=int(match_av.group(1)), source_url=normalize_url(text))

    if text.startswith(("http://", "https://")):
        try:
            import httpx

            with httpx.Client(follow_redirects=True, timeout=20.0) as client:
                resp = client.get(text)
                final_url = str(resp.url)
        except Exception:
            final_url = text

        match_bv = BV_PATTERN.search(final_url)
        if match_bv:
            return VideoIdentity(bvid=match_bv.group(1), aid=None, source_url=final_url)

        match_av = AV_PATTERN.search(final_url)
        if match_av:
            return VideoIdentity(bvid=None, aid=int(match_av.group(1)), source_url=final_url)

    raise ValueError("无法从输入内容中解析出 BV/av 号。")


def extract_sessdata(cookie_file: Path) -> str | None:
    if not cookie_file.exists():
        raise FileNotFoundError(f"未找到 Cookie 文件：{cookie_file}")

    text = cookie_file.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return None

    # 纯文本格式：SESSDATA=xxxx
    m = re.search(r"SESSDATA\s*=\s*([^;\s]+)", text)
    if m:
        return m.group(1).strip()

    # Netscape cookies.txt 格式
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 7 and parts[5] == "SESSDATA":
            return parts[6].strip()

    # JSON 格式
    try:
        obj = json.loads(text)
    except Exception:
        obj = None

    if isinstance(obj, dict):
        direct = obj.get("SESSDATA") or obj.get("sessdata")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()

        if isinstance(obj.get("cookie_info"), dict):
            cookies = obj["cookie_info"].get("cookies", [])
            if isinstance(cookies, list):
                for item in cookies:
                    if not isinstance(item, dict):
                        continue
                    if item.get("name") == "SESSDATA":
                        value = item.get("value")
                        if isinstance(value, str) and value.strip():
                            return value.strip()

        cookies = obj.get("cookies")
        if isinstance(cookies, list):
            for item in cookies:
                if not isinstance(item, dict):
                    continue
                if item.get("name") == "SESSDATA":
                    value = item.get("value")
                    if isinstance(value, str) and value.strip():
                        return value.strip()

    return None


def ensure_tooling() -> None:
    import shutil

    if shutil.which("yutto") is None:
        raise RuntimeError("未在 PATH 中找到 `yutto`，请先安装：pip install yutto")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("未在 PATH 中找到 `ffmpeg`，请先安装 ffmpeg。")


def run_yutto_download(url: str, out_dir: Path, sessdata: str | None) -> None:
    cmd = [
        "yutto",
        "download",
        url,
        "-d",
        str(out_dir),
        "--no-danmaku",
        "--no-cover",
        "--no-progress",
        "--no-color",
    ]
    if sessdata:
        cmd += ["--sessdata", sessdata]

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=env,
    )
    if process.returncode != 0:
        print(process.stdout)
        print(process.stderr, file=sys.stderr)
        raise RuntimeError(f"yutto 下载失败，退出码：{process.returncode}")


def parse_srt_timestamp(ts: str) -> float:
    # 时间格式：HH:MM:SS,mmm
    hms, ms = ts.replace(".", ",").split(",")
    h, m, s = hms.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def split_time(seconds: float) -> tuple[int, int, int, int]:
    sec_int = int(seconds)
    ms = int(round((seconds - sec_int) * 1000))
    if ms >= 1000:
        sec_int += 1
        ms -= 1000
    h = sec_int // 3600
    m = (sec_int % 3600) // 60
    s = sec_int % 60
    return h, m, s, ms


def format_srt_time(seconds: float) -> str:
    h, m, s, ms = split_time(seconds)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_vtt_time(seconds: float) -> str:
    h, m, s, ms = split_time(seconds)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def format_lrc_time(seconds: float) -> str:
    total_hundredths = int(round(seconds * 100))
    total_seconds = total_hundredths // 100
    hundredths = total_hundredths % 100
    minutes = total_seconds // 60
    sec = total_seconds % 60
    return f"{minutes:02d}:{sec:02d}.{hundredths:02d}"


def parse_srt_file(srt_path: Path) -> list[dict[str, Any]]:
    text = srt_path.read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    rows: list[dict[str, Any]] = []

    for block in blocks:
        lines = [line for line in block.split("\n") if line.strip()]
        if len(lines) < 2:
            continue
        if "-->" not in lines[1] and "-->" in lines[0]:
            time_line = lines[0]
            content_lines = lines[1:]
        elif len(lines) >= 3 and "-->" in lines[1]:
            time_line = lines[1]
            content_lines = lines[2:]
        else:
            continue

        left, right = [part.strip() for part in time_line.split("-->", 1)]
        try:
            start = parse_srt_timestamp(left)
            end = parse_srt_timestamp(right)
        except Exception:
            continue
        rows.append({"from": start, "to": end, "content": "\n".join(content_lines).strip()})

    return rows


def write_subtitle(rows: list[dict[str, Any]], target_path: Path, fmt: str) -> None:
    if fmt == "json":
        target_path.write_text(
            json.dumps({"body": rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return

    if fmt == "vtt":
        lines = ["WEBVTT", ""]
        for row in rows:
            lines.append(f"{format_vtt_time(row['from'])} --> {format_vtt_time(row['to'])}")
            lines.append(row["content"])
            lines.append("")
        target_path.write_text("\n".join(lines), encoding="utf-8")
        return

    if fmt == "lrc":
        lines = []
        for row in rows:
            for content_line in str(row["content"]).splitlines() or [""]:
                lines.append(f"[{format_lrc_time(row['from'])}] {content_line}".rstrip())
        target_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    if fmt == "srt":
        lines = []
        for idx, row in enumerate(rows, start=1):
            lines.append(str(idx))
            lines.append(f"{format_srt_time(row['from'])} --> {format_srt_time(row['to'])}")
            lines.append(row["content"])
            lines.append("")
        target_path.write_text("\n".join(lines), encoding="utf-8")
        return

    raise ValueError(f"不支持的字幕格式：{fmt}")


def convert_or_prepare_subtitle(video_dir: Path, subtitle_format: str) -> Path | None:
    srt_files = sorted(video_dir.rglob("*.srt"))
    if not srt_files:
        return None

    source_srt = srt_files[0]
    rows = parse_srt_file(source_srt)
    if not rows:
        return None

    target_path = video_dir / f"subtitle.{subtitle_format}"
    write_subtitle(rows, target_path, subtitle_format)

    # 避免播放器叠加双层字幕：
    # 仅保留规范化后的目标字幕文件，其余 .srt 清理掉。
    keep_srt = {target_path.resolve()} if target_path.suffix.lower() == ".srt" else set()
    for srt_path in video_dir.rglob("*.srt"):
        try:
            if srt_path.resolve() not in keep_srt:
                srt_path.unlink(missing_ok=True)
        except Exception:
            # 清理失败时忽略，不影响主流程。
            pass

    return target_path


def build_comment_record(reply: dict[str, Any]) -> dict[str, Any]:
    content = reply.get("content")
    if isinstance(content, dict):
        # 保留完整 content 对象，例如 message/members/jump_url/max_line。
        return content
    return {}


def get_reply_mid(reply: dict[str, Any]) -> int | None:
    mid = reply.get("mid")
    if mid is not None:
        try:
            return int(mid)
        except Exception:
            pass
    member = reply.get("member") or {}
    mid = member.get("mid")
    if mid is not None:
        try:
            return int(mid)
        except Exception:
            return None
    return None


async def get_sub_replies_for_root(
    aid: int,
    root_rpid: int,
    credential: Credential | None,
) -> list[dict[str, Any]]:
    root_comment = comment.Comment(
        oid=aid,
        type_=comment.CommentResourceType.VIDEO,
        rpid=root_rpid,
        credential=credential,
    )
    page_index = 1
    page_size = 20
    sub_replies: list[dict[str, Any]] = []

    while True:
        page_data = await root_comment.get_sub_comments(page_index=page_index, page_size=page_size)
        current = [item for item in (page_data.get("replies") or []) if isinstance(item, dict)]
        if not current:
            break
        sub_replies.extend(current)

        page = page_data.get("page") or {}
        total_count = int(page.get("count") or 0)
        current_size = int(page.get("size") or page_size) or page_size
        if page_index * current_size >= total_count:
            break
        page_index += 1

    return sub_replies


async def fetch_video_info_and_comments(
    identity: VideoIdentity,
    credential: Credential | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if identity.bvid:
        v = video.Video(bvid=identity.bvid, credential=credential)
    elif identity.aid is not None:
        v = video.Video(aid=identity.aid, credential=credential)
    else:
        raise ValueError("无效的视频标识。")

    info = await v.get_info()
    aid = int(info["aid"])
    bvid = info.get("bvid")
    up_mid = int((info.get("owner") or {}).get("mid"))
    video_id = bvid or f"av{aid}"
    canonical_url = f"https://www.bilibili.com/video/{video_id}"

    result = await comment.get_comments(
        oid=aid,
        type_=comment.CommentResourceType.VIDEO,
        page_index=1,
        order=comment.OrderType.LIKE,
        credential=credential,
    )

    records: list[dict[str, Any]] = []
    seen_rpids: set[int] = set()

    top_candidates = []
    upper = result.get("upper") or {}
    if isinstance(upper.get("top"), dict):
        top_candidates.append(upper["top"])
    if isinstance(result.get("top"), dict):
        top_candidates.append(result["top"])

    # 仅处理置顶评论楼：置顶一级 + 该楼二级回复。
    top_roots: list[dict[str, Any]] = []
    seen_top_rpids: set[int] = set()
    for item in top_candidates:
        rpid = item.get("rpid")
        if isinstance(rpid, int):
            if rpid in seen_top_rpids:
                continue
            seen_top_rpids.add(rpid)
        top_roots.append(item)

    for top_reply in top_roots:
        mid = get_reply_mid(top_reply)
        rpid = top_reply.get("rpid")
        if mid == up_mid and isinstance(rpid, int) and rpid not in seen_rpids:
            seen_rpids.add(rpid)
            records.append(build_comment_record(top_reply))

        if isinstance(rpid, int):
            try:
                sub_replies = await get_sub_replies_for_root(aid, rpid, credential)
            except Exception:
                sub_replies = []
            for sub_reply in sub_replies:
                sub_mid = get_reply_mid(sub_reply)
                sub_rpid = sub_reply.get("rpid")
                if sub_mid == up_mid and isinstance(sub_rpid, int) and sub_rpid not in seen_rpids:
                    seen_rpids.add(sub_rpid)
                    records.append(build_comment_record(sub_reply))

    meta = {
        "aid": aid,
        "bvid": bvid,
        "title": info.get("title", ""),
        "up_mid": up_mid,
        "video_id": video_id,
        "video_url": canonical_url,
    }
    return meta, records


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


async def async_main() -> int:
    args = parse_args()
    ensure_tooling()

    identity = resolve_video_identity(args.url)

    sessdata: str | None = None
    if args.cookie_file:
        sessdata = extract_sessdata(Path(args.cookie_file))
        if not sessdata:
            print("警告：已提供 Cookie 文件，但未找到 SESSDATA，将按未登录状态继续。")

    credential = Credential(sessdata=sessdata) if sessdata else None

    # 先获取标题和 UP 信息，保证目录命名稳定。
    meta, up_comments = await fetch_video_info_and_comments(identity, credential)
    safe_title = sanitize_filename(meta["title"])
    video_id = meta["video_id"]

    out_root = Path(args.out_dir).resolve()
    video_dir = out_root / f"{video_id}_{safe_title}"
    video_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] 正在下载视频到：{video_dir}")
    run_yutto_download(identity.source_url, video_dir, sessdata)

    print(f"[2/3] 正在处理字幕格式：{args.subtitle_format}")
    subtitle_path = convert_or_prepare_subtitle(video_dir, args.subtitle_format)
    if subtitle_path:
        print(f"字幕已保存：{subtitle_path}")
    else:
        print("未找到可用字幕，已跳过字幕导出。")

    print("[3/3] 正在导出 UP 主置顶评论楼（一级+二级）内容")
    comments_path = video_dir / "up_top_hot_comments.json"
    write_json(comments_path, up_comments)
    print(f"评论已保存：{comments_path}（共 {len(up_comments)} 条）")

    # 额外保存视频元信息，便于追溯。
    meta_path = video_dir / "video_meta.json"
    write_json(meta_path, meta)
    print(f"元信息已保存：{meta_path}")

    print("执行完成。")
    return 0


def main() -> None:
    try:
        code = asyncio.run(async_main())
        raise SystemExit(code)
    except KeyboardInterrupt:
        print("用户中断执行。", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
