"""选品推荐器（MVP）。"""

from __future__ import annotations

from app.modules.recommender.hot_calendar import get_today_hot_topics


def recommend_products(products: list[dict], top_n: int = 20) -> list[dict]:
    """基于评分和热点主题做简单推荐。"""
    hot_topics = get_today_hot_topics()
    # 当前先按 score、佣金排序。
    ranked = sorted(
        products,
        key=lambda x: (float(x.get("score", 0)), float(x.get("commission_rate", 0))),
        reverse=True,
    )
    result = []
    for row in ranked[:top_n]:
        row = dict(row)
        row["recommend_reason"] = f"当前热点：{hot_topics[0]}，且评分/佣金较高"
        result.append(row)
    return result
