"""淘宝联盟佣金查询（MVP 模拟版）。"""

from __future__ import annotations

from app.modules.data_store.models import CommissionRecord


def query_taobao_commission(product_ids: list[str]) -> dict[tuple[str, str], CommissionRecord]:
    """查询淘宝商品佣金。

    说明：
    - 真实对接需要淘宝联盟账号、签名与权限。
    - 当前先提供可运行的模拟查询，后续替换实现。
    """
    result: dict[tuple[str, str], CommissionRecord] = {}
    for pid in product_ids:
        if not pid:
            continue
        seed = int(pid[-4:] if pid[-4:].isdigit() else abs(hash(pid)) % 10000)
        rate = round(3 + (seed % 1200) / 100, 2)  # 3.00% ~ 15.00%
        income = round(8 + (seed % 3000) / 10, 2)
        record = CommissionRecord(
            platform="taobao",
            product_id=pid,
            commission_rate=rate,
            estimated_income=income,
            campaign_name="TODO:接入淘宝联盟API",
        )
        result[(record.platform, record.product_id)] = record
    return result
