"""评论监控模块（MVP 占位）。"""

from __future__ import annotations

from app.services.ai_gateway import ai_gateway


def classify_comments(comments: list[str]) -> list[dict]:
    """批量分类评论。"""
    rows = []
    for text in comments:
        rows.append({"text": text, "type": ai_gateway.classify_comment(text)})
    return rows
