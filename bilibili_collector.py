"""
B站视频采集脚本
输入BV号，采集：字幕、评论区蓝链（商品链接）、视频元信息。

依赖安装（在虚拟环境下）:
  pip install bilibili-api-python aiohttp httpx openpyxl

用法:
  # 采集单个视频
  python bilibili_collector.py BV1xxxxxxxxxx

  # 采集多个视频
  python bilibili_collector.py BV1aaa BV1bbb BV1ccc

  # 首次使用需要登录（扫码），登录后会缓存Cookie
  # 字幕获取必须登录，评论第1页不需要登录
"""

import asyncio
import json
import re
import sys
from pathlib import Path

import httpx
from bilibili_api import Credential, comment, video
from openpyxl import Workbook


# ============ 配置 ============

# Cookie缓存文件路径
COOKIE_FILE = Path(__file__).parent / ".bilibili_cookie.json"

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "采集输出"


# ============ Cookie / 登录 ============

def load_credential() -> Credential | None:
    """从缓存文件加载Cookie"""
    if not COOKIE_FILE.exists():
        return None
    try:
        data = json.loads(COOKIE_FILE.read_text(encoding="utf-8"))
        return Credential(
            sessdata=data.get("sessdata", ""),
            bili_jct=data.get("bili_jct", ""),
            buvid3=data.get("buvid3", ""),
            dedeuserid=data.get("dedeuserid", ""),
            ac_time_value=data.get("ac_time_value", ""),
        )
    except Exception as e:
        print(f"加载Cookie失败: {e}")
        return None


def save_credential(credential: Credential):
    """保存Cookie到缓存文件"""
    data = {
        "sessdata": credential.sessdata or "",
        "bili_jct": credential.bili_jct or "",
        "buvid3": credential.buvid3 or "",
        "dedeuserid": credential.dedeuserid or "",
        "ac_time_value": credential.ac_time_value or "",
    }
    COOKIE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Cookie已缓存到: {COOKIE_FILE}")


async def login_by_qrcode() -> Credential:
    """通过扫码登录B站，返回Credential"""
    try:
        # 新版本 bilibili-api-python
        from bilibili_api.login_v2 import login_with_qrcode_term as login_with_qrcode
    except Exception:
        # 兼容旧版本
        from bilibili_api.login import login_with_qrcode

    print("=" * 40)
    print("需要登录B站（扫码），用于获取字幕等数据")
    print("=" * 40)

    # login_with_qrcode 会在终端显示二维码
    credential = await asyncio.to_thread(login_with_qrcode)

    if not isinstance(credential, Credential):
        print("登录失败，请重试")
        sys.exit(1)

    save_credential(credential)
    print("登录成功！\n")
    return credential


async def get_credential() -> Credential:
    """获取Credential：优先从缓存加载，否则扫码登录"""
    credential = load_credential()
    if credential and credential.sessdata:
        print("已从缓存加载Cookie")
        return credential
    return await login_by_qrcode()


# ============ 工具函数 ============

def extract_bvid(input_str: str) -> str:
    """从URL或纯BV号中提取BV号"""
    # 匹配 BV 号（12位字母数字）
    match = re.search(r"(BV[a-zA-Z0-9]{10})", input_str)
    if match:
        return match.group(1)
    raise ValueError(f"无法从 '{input_str}' 中提取BV号")


def format_seconds(seconds: float) -> str:
    """秒数转 MM:SS 格式"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


# ============ 核心采集功能 ============

async def fetch_video_info(v: video.Video) -> dict:
    """获取视频基本信息"""
    info = await v.get_info()
    return {
        "bvid": info.get("bvid", ""),
        "aid": info.get("aid", 0),
        "title": info.get("title", ""),
        "desc": info.get("desc", ""),
        "pic": info.get("pic", ""),
        "duration": info.get("duration", 0),
        "view": info["stat"]["view"],
        "danmaku": info["stat"]["danmaku"],
        "like": info["stat"]["like"],
        "coin": info["stat"]["coin"],
        "favorite": info["stat"]["favorite"],
        "reply": info["stat"]["reply"],
        "owner_name": info["owner"]["name"],
        "owner_mid": info["owner"]["mid"],
        "cid": info.get("cid", 0),
        "pages": info.get("pages", []),
    }


async def fetch_subtitle(v: video.Video, cid: int) -> str:
    """获取视频字幕，返回纯文本"""
    try:
        subtitle_info = await v.get_subtitle(cid=cid)
    except Exception as e:
        print(f"  获取字幕接口失败: {e}")
        return ""

    subtitles = subtitle_info.get("subtitles", [])
    if not subtitles:
        print("  未找到字幕（该视频可能无CC字幕/AI字幕）")
        return ""

    # 优先选中文字幕
    target = subtitles[0]
    for sub in subtitles:
        if "zh" in sub.get("lan", ""):
            target = sub
            break

    url = target.get("subtitle_url", "")
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url

    print(f"  字幕语言: {target.get('lan_doc', '未知')}")

    # 下载字幕JSON
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        subtitle_json = resp.json()

    # 拼接为纯文本（带时间戳）
    lines = []
    for item in subtitle_json.get("body", []):
        time_str = format_seconds(item["from"])
        lines.append(f"[{time_str}] {item['content']}")

    return "\n".join(lines)


async def fetch_blue_links(aid: int, credential: Credential | None) -> list[dict]:
    """
    获取评论区蓝链（商品链接）
    返回: [{"url": "...", "title": "...", "comment": "..."}]
    """
    blue_links = []
    seen_urls = set()

    # 先用旧版API获取第1页（包含置顶评论）
    try:
        result = await comment.get_comments(
            oid=aid,
            type_=comment.CommentResourceType.VIDEO,
            page_index=1,
            order=comment.OrderType.LIKE,
            credential=credential,
        )
    except Exception as e:
        print(f"  获取评论失败: {e}")
        return blue_links

    # 提取置顶评论中的蓝链
    top_reply = result.get("upper", {}).get("top")
    if top_reply:
        _extract_links(top_reply, blue_links, seen_urls, is_top=True)

    # 提取普通评论中的蓝链（通常蓝链在置顶评论里，但也检查前几页）
    for reply in result.get("replies", []) or []:
        _extract_links(reply, blue_links, seen_urls, is_top=False)

    # 翻页获取更多评论（最多3页，蓝链一般在前面）
    for page in range(2, 4):
        try:
            result = await comment.get_comments(
                oid=aid,
                type_=comment.CommentResourceType.VIDEO,
                page_index=page,
                order=comment.OrderType.LIKE,
                credential=credential,
            )
            for reply in result.get("replies", []) or []:
                _extract_links(reply, blue_links, seen_urls, is_top=False)
        except Exception:
            break

    return blue_links


def _extract_links(reply: dict, blue_links: list, seen_urls: set, is_top: bool):
    """从单条评论中提取蓝链"""
    content = reply.get("content", {})
    message = content.get("message", "")
    jump_urls = content.get("jump_url", {})

    if not jump_urls:
        return

    for url, info in jump_urls.items():
        # 过滤非商品链接（如B站内部跳转、搜索链接等）
        if _is_product_link(url):
            if url not in seen_urls:
                seen_urls.add(url)
                blue_links.append({
                    "url": url,
                    "title": info.get("title", ""),
                    "platform": _detect_platform(url),
                    "is_top": is_top,
                    "comment_text": message[:100],
                })


def _is_product_link(url: str) -> bool:
    """判断是否为商品链接（京东/淘宝）"""
    product_domains = [
        "jd.com", "京东", "taobao.com", "tmall.com",
        "item.jd", "union.click", "u.jd.com",
        "s.click.taobao", "uland.taobao",
        "mobile.yangkeduo",  # 拼多多
    ]
    return any(domain in url for domain in product_domains)


def _detect_platform(url: str) -> str:
    """检测商品链接所属平台"""
    if any(d in url for d in ["jd.com", "u.jd.com", "union.click"]):
        return "京东"
    if any(d in url for d in ["taobao.com", "tmall.com", "s.click.taobao"]):
        return "淘宝"
    if "yangkeduo" in url:
        return "拼多多"
    return "未知"


# ============ 输出保存 ============

def save_results(bvid: str, video_info: dict, subtitle_text: str, blue_links: list[dict]):
    """保存采集结果到文件"""
    # 用视频标题作为子目录名（去除特殊字符）
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', video_info["title"])[:50]
    out_dir = OUTPUT_DIR / f"{bvid}_{safe_title}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 保存视频元信息
    info_path = out_dir / "视频信息.json"
    info_path.write_text(
        json.dumps(video_info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 2. 保存字幕
    if subtitle_text:
        subtitle_path = out_dir / "字幕.txt"
        subtitle_path.write_text(subtitle_text, encoding="utf-8")

        # 同时保存一份不带时间戳的纯文本（方便AI改写）
        pure_text = re.sub(r"\[\d{2}:\d{2}\] ", "", subtitle_text)
        pure_path = out_dir / "字幕_纯文本.txt"
        pure_path.write_text(pure_text, encoding="utf-8")

    # 3. 保存蓝链到Excel
    if blue_links:
        wb = Workbook()
        ws = wb.active
        ws.title = "蓝链商品"
        ws.append(["序号", "商品标题", "链接", "平台", "是否置顶评论", "评论内容"])
        for i, link in enumerate(blue_links, 1):
            ws.append([
                i,
                link["title"],
                link["url"],
                link["platform"],
                "是" if link["is_top"] else "否",
                link["comment_text"],
            ])
        # 调整列宽
        ws.column_dimensions["B"].width = 40
        ws.column_dimensions["C"].width = 60
        ws.column_dimensions["F"].width = 50
        excel_path = out_dir / "蓝链商品.xlsx"
        wb.save(str(excel_path))

    print(f"\n  输出目录: {out_dir}")
    print(f"  视频信息: 视频信息.json")
    if subtitle_text:
        print(f"  字幕文件: 字幕.txt / 字幕_纯文本.txt")
    if blue_links:
        print(f"  蓝链商品: 蓝链商品.xlsx （共 {len(blue_links)} 条）")


# ============ 主流程 ============

async def collect_one(bvid: str, credential: Credential):
    """采集单个视频"""
    print(f"\n{'='*50}")
    print(f"开始采集: {bvid}")
    print(f"{'='*50}")

    v = video.Video(bvid=bvid, credential=credential)

    # 1. 获取视频信息
    print("\n[1/3] 获取视频信息...")
    video_info = await fetch_video_info(v)
    print(f"  标题: {video_info['title']}")
    print(f"  UP主: {video_info['owner_name']}")
    print(f"  播放: {video_info['view']}  点赞: {video_info['like']}  评论: {video_info['reply']}")

    # 2. 获取字幕
    print("\n[2/3] 获取字幕...")
    subtitle_text = await fetch_subtitle(v, video_info["cid"])
    if subtitle_text:
        line_count = len(subtitle_text.strip().split("\n"))
        print(f"  字幕行数: {line_count}")
    else:
        print("  未获取到字幕")

    # 3. 获取评论区蓝链
    print("\n[3/3] 获取评论区蓝链...")
    blue_links = await fetch_blue_links(video_info["aid"], credential)
    if blue_links:
        print(f"  找到 {len(blue_links)} 条商品链接:")
        for link in blue_links:
            print(f"    [{link['platform']}] {link['title'][:30]} -> {link['url'][:60]}")
    else:
        print("  未找到商品链接")

    # 4. 保存结果
    print("\n[保存结果]")
    save_results(bvid, video_info, subtitle_text, blue_links)


async def main():
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法: python bilibili_collector.py <BV号或URL> [BV号2] [BV号3] ...")
        print("示例: python bilibili_collector.py BV1uv411q7Mv")
        print("示例: python bilibili_collector.py https://www.bilibili.com/video/BV1uv411q7Mv")
        sys.exit(1)

    bvids = []
    for arg in sys.argv[1:]:
        try:
            bvids.append(extract_bvid(arg))
        except ValueError as e:
            print(f"跳过无效输入: {e}")

    if not bvids:
        print("没有有效的BV号")
        sys.exit(1)

    # 获取登录凭证
    credential = await get_credential()

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 逐个采集
    for bvid in bvids:
        try:
            await collect_one(bvid, credential)
        except Exception as e:
            print(f"\n采集 {bvid} 失败: {e}")

    print(f"\n{'='*50}")
    print(f"全部采集完成！共处理 {len(bvids)} 个视频")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
