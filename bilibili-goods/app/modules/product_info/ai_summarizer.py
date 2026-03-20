"""商品卖点提炼。"""

from __future__ import annotations

from app.services.ai_gateway import ai_gateway


def summarize_selling_points(raw_text: str, max_points: int = 5) -> list[str]:
    """提炼卖点。"""
    return ai_gateway.summarize_selling_points(raw_text, max_points=max_points)
