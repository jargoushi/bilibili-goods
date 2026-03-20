"""蓝链文案格式化。"""

from __future__ import annotations


def format_blue_link_comment(items: list[dict]) -> str:
    """按商品列表输出评论区蓝链文案。"""
    lines = ["本期好物清单（可直接点链接）："]
    for idx, item in enumerate(items, start=1):
        name = item.get("name") or f"{item.get('platform', '')}-{item.get('product_id', '')}"
        link = item.get("detail_url") or item.get("resolved_link") or ""
        lines.append(f"{idx}. {name} {link}".strip())
    lines.append("需要我做预算分档推荐，可以在评论区留言。")
    return "\n".join(lines)
