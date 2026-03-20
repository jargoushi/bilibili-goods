"""封面模板定义。"""

from __future__ import annotations


def get_cover_templates() -> list[dict]:
    """返回预设封面模板。"""
    return [
        {"name": "简约高亮", "bg_color": "#f6f3ea", "title_color": "#1f2937"},
        {"name": "冲击对比", "bg_color": "#fee2e2", "title_color": "#7f1d1d"},
        {"name": "科技理性", "bg_color": "#dbeafe", "title_color": "#1e3a8a"},
    ]
