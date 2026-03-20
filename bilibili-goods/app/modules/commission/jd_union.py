"""京东联盟佣金查询（MVP 模拟版）。"""

from __future__ import annotations

from app.modules.data_store.models import CommissionRecord


def query_jd_commission(product_ids: list[str]) -> dict[tuple[str, str], CommissionRecord]:
    """查询京东商品佣金。

    说明：
    - 真实联盟 API 需要账号和签名流程。
    - 当前先用稳定可复现的模拟值，保障闭环可跑。
    """
    result: dict[tuple[str, str], CommissionRecord] = {}
    for pid in product_ids:
        if not pid:
            continue
        # 用 product_id 做伪随机，保证同一商品每次结果一致。
        seed = int(pid[-4:] if pid[-4:].isdigit() else abs(hash(pid)) % 10000)
        rate = round(5 + (seed % 1500) / 100, 2)  # 5.00% ~ 20.00%
        income = round(10 + (seed % 5000) / 10, 2)
        record = CommissionRecord(
            platform="jd",
            product_id=pid,
            commission_rate=rate,
            estimated_income=income,
            campaign_name="TODO:接入京东联盟API",
        )
        result[(record.platform, record.product_id)] = record
    return result
