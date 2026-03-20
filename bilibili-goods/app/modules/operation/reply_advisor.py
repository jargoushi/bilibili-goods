"""评论回复建议模块。"""

from __future__ import annotations

from app.services.ai_gateway import ai_gateway


def build_reply_suggestion(comment_text: str, knowledge: str = "") -> str:
    """生成回复建议草稿。"""
    return ai_gateway.make_reply_suggestion(comment_text, knowledge=knowledge)
