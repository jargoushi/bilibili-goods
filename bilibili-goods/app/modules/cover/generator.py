"""封面生成器（MVP：文本方案输出）。"""

from __future__ import annotations

from app.modules.cover.templates import get_cover_templates


def generate_cover_plan(title: str, category: str) -> list[dict]:
    """生成封面方案描述。

    TODO: 后续接 Pillow 真正渲染图片。
    """
    templates = get_cover_templates()
    plans = []
    for idx, tpl in enumerate(templates, start=1):
        plans.append(
            {
                "index": idx,
                "template": tpl["name"],
                "title": title,
                "subtitle": f"{category} 推荐清单",
                "ratio": ["16:9", "4:3"],
            }
        )
    return plans
