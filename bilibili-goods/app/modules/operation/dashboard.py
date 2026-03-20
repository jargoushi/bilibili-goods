"""运营看板数据聚合。"""

from __future__ import annotations


def build_dashboard_metrics(
    play_count: int,
    like_count: int,
    comment_count: int,
    gmv: float,
    commission_income: float,
) -> dict:
    """构造看板指标。"""
    interaction_rate = 0.0
    if play_count > 0:
        interaction_rate = round((like_count + comment_count) / play_count * 100, 2)
    return {
        "play_count": play_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "interaction_rate_pct": interaction_rate,
        "gmv": round(gmv, 2),
        "commission_income": round(commission_income, 2),
    }
