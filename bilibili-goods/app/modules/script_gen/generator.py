"""脚本生成器（模板版）。"""

from __future__ import annotations


def generate_script(
    product_name: str,
    selling_points: list[str],
    target_crowd: str = "通用人群",
    duration_hint: str = "60秒",
) -> str:
    """生成口播稿初稿。"""
    points = selling_points[:4] if selling_points else ["性价比高", "使用体验好"]
    return (
        f"你还在为同类产品踩坑吗？今天给{target_crowd}推荐一款：{product_name}。\n"
        f"先说结论：这款产品在{duration_hint}内容里最值得讲的点有{len(points)}个。\n"
        + "\n".join([f"第{i+1}个卖点：{p}。" for i, p in enumerate(points)])
        + "\n如果你也有同样场景，评论区告诉我预算，我给你更细的选购建议。"
    )
