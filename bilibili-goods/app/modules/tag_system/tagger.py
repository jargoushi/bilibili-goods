"""卖点标签系统（规则版）。"""

from __future__ import annotations


SCENE_RULES = {
    "宿舍": ["宿舍", "小空间", "寝室"],
    "户外": ["露营", "户外", "旅行"],
    "上班": ["办公室", "通勤", "工位"],
}
PEOPLE_RULES = {
    "学生": ["学生", "上学", "校园"],
    "打工人": ["打工人", "上班族", "白领"],
    "宝妈": ["宝妈", "孩子", "婴儿"],
}
NEED_RULES = {
    "省钱": ["便宜", "性价比", "省钱"],
    "提升效率": ["效率", "快速", "省时"],
    "舒适": ["舒服", "舒适", "体验"],
}


def auto_tag(text: str) -> list[str]:
    """根据关键词自动打标签。"""
    text = text or ""
    tags: list[str] = []
    for name, keys in {**SCENE_RULES, **PEOPLE_RULES, **NEED_RULES}.items():
        if any(k in text for k in keys):
            tags.append(name)
    return sorted(set(tags))
