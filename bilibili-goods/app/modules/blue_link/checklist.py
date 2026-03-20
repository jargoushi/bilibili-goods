"""发布清单生成。"""

from __future__ import annotations


def build_publish_checklist(title: str, has_cover: bool, has_blue_link: bool) -> list[dict]:
    """生成发布前核对项。"""
    return [
        {"item": "标题已确认", "done": bool(title.strip())},
        {"item": "封面已准备", "done": has_cover},
        {"item": "简介和标签已填写", "done": False},
        {"item": "蓝链评论已准备", "done": has_blue_link},
        {"item": "章节与置顶评论策略已确认", "done": False},
    ]
