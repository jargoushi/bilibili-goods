"""热点日历（MVP 静态版）。"""

from __future__ import annotations

from datetime import date


def get_today_hot_topics(today: date | None = None) -> list[str]:
    """返回当天热点主题。

    TODO: 后续对接真实热点数据源（节日/季节/平台热词）。
    """
    today = today or date.today()
    month = today.month
    if month in (6, 7, 8):
        return ["夏季清凉", "宿舍降温", "旅行收纳"]
    if month in (11, 12, 1):
        return ["冬季保暖", "年货清单", "居家舒适"]
    return ["开学季", "效率工具", "性价比好物"]
