"""商品详情抓取（MVP：轻量抓取）。"""

from __future__ import annotations

from app.services.crawler_engine import crawler_engine


def fetch_detail_html(detail_url: str) -> str:
    """抓取商品详情页 HTML。"""
    if not detail_url:
        return ""
    try:
        return crawler_engine.get_text(detail_url)
    except Exception:
        # TODO: 增加 playwright 渲染版本，适配动态加载页面。
        return ""
