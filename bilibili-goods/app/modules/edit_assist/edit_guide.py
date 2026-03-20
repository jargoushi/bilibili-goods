"""剪辑指引生成器。"""

from __future__ import annotations

from pathlib import Path


def generate_edit_guide(script_lines: list[str], target_path: Path) -> Path:
    """输出结构化剪辑说明。"""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# 剪辑指引", ""]
    for idx, text in enumerate(script_lines, start=1):
        lines.append(f"## 段落 {idx}")
        lines.append(f"- 口播内容：{text}")
        lines.append("- 建议素材：商品主图 / 场景图 / 参数图")
        lines.append("- 建议转场：快速切换 + 放大")
        lines.append("")
    target_path.write_text("\n".join(lines), encoding="utf-8")
    return target_path
