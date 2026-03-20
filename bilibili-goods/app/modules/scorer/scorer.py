"""产品评分模型（MVP 加权版）。"""

from __future__ import annotations


def score_product(
    commission_rate: float,
    selling_point_count: int,
    competition_score: float,
    comment_heat_score: float,
) -> dict[str, float]:
    """计算商品总分并返回拆解明细。

    权重：
    - 佣金 30%
    - 卖点数量 20%
    - 竞争度（低竞争高得分）30%
    - 评论热度 20%
    """
    commission_norm = min(max(commission_rate / 20.0, 0.0), 1.0)
    points_norm = min(max(selling_point_count / 10.0, 0.0), 1.0)
    competition_norm = min(max(competition_score, 0.0), 1.0)
    comment_norm = min(max(comment_heat_score, 0.0), 1.0)

    total = (
        commission_norm * 0.30
        + points_norm * 0.20
        + competition_norm * 0.30
        + comment_norm * 0.20
    )
    return {
        "score": round(total * 100, 2),
        "commission_score": round(commission_norm * 100, 2),
        "selling_point_score": round(points_norm * 100, 2),
        "competition_score": round(competition_norm * 100, 2),
        "comment_heat_score": round(comment_norm * 100, 2),
    }
