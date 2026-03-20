"""评论链接解析工具。"""

from __future__ import annotations

import hashlib
import re
from urllib.parse import parse_qs, urlparse

from app.services.crawler_engine import crawler_engine


# 简单 URL 匹配，先满足评论文本提取场景。
URL_PATTERN = re.compile(r"https?://[^\s]+")


def extract_links_from_text(text: str) -> list[str]:
    """从评论文本中提取链接。"""
    return [item.strip(".,;!?)】》") for item in URL_PATTERN.findall(text or "")]


def detect_platform(url: str) -> str:
    """按域名识别平台。"""
    u = (url or "").lower()
    if any(k in u for k in ["jd.com", "3.cn", "u.jd.com"]):
        return "jd"
    if any(k in u for k in ["taobao.com", "tmall.com", "tb.cn"]):
        return "taobao"
    return "unknown"


def extract_product_id(url: str, platform: str) -> str:
    """从链接中提取商品 ID。"""
    parsed = urlparse(url)
    path = parsed.path or ""

    if platform == "jd":
        # 典型 JD 商品链接：/123456.html
        m = re.search(r"/(\d+)\.html", path)
        if m:
            return m.group(1)
        # 某些跳转参数中带 sku
        qs = parse_qs(parsed.query)
        for key in ["sku", "skuId", "id"]:
            if key in qs and qs[key]:
                return str(qs[key][0])
        return ""

    if platform == "taobao":
        qs = parse_qs(parsed.query)
        for key in ["id", "item_id"]:
            if key in qs and qs[key]:
                return str(qs[key][0])
        # 部分路径里有 item id
        m = re.search(r"(\d{8,})", path)
        return m.group(1) if m else ""

    return ""


def normalize_link(raw_url: str) -> tuple[str, str, str]:
    """链接标准化：短链还原 + 平台识别 + 商品ID提取。"""
    resolved = crawler_engine.resolve_short_link(raw_url)
    platform = detect_platform(resolved)
    product_id = extract_product_id(resolved, platform)
    # 对联盟跳转链（union-click / s.click）等无法直接提取真实商品ID的场景，
    # 生成稳定的兜底ID，先保证流程可跑通、可入库、可测试。
    # TODO: 后续接入联盟API后，替换为真实商品ID。
    if platform != "unknown" and not product_id:
        product_id = build_fallback_product_id(platform, resolved)
    return resolved, platform, product_id


def build_fallback_product_id(platform: str, resolved_link: str) -> str:
    """基于链接生成稳定兜底商品ID。"""
    digest = hashlib.md5(resolved_link.encode("utf-8")).hexdigest()[:12]
    return f"{platform}_link_{digest}"
