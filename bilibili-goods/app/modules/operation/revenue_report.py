"""收益报表模块。"""

from __future__ import annotations


def build_revenue_report(rows: list[dict]) -> dict:
    """按输入记录聚合收益。"""
    total_gmv = sum(float(x.get("gmv", 0)) for x in rows)
    total_commission = sum(float(x.get("commission", 0)) for x in rows)
    return {
        "row_count": len(rows),
        "total_gmv": round(total_gmv, 2),
        "total_commission": round(total_commission, 2),
        "avg_commission_per_row": round(total_commission / len(rows), 2) if rows else 0.0,
    }
