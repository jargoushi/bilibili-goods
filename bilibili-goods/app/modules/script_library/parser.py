"""脚本拆解器。"""

from __future__ import annotations


def split_script_components(script_text: str) -> dict[str, list[str]]:
    """将脚本按句子粗分为组件。

    规则：
    - 前2句视为 hook
    - 最后1句视为 cta
    - 中间句优先作为 point
    """
    lines = [x.strip() for x in script_text.splitlines() if x.strip()]
    if not lines:
        return {"hook": [], "turn": [], "point": [], "cta": []}
    hook = lines[:2]
    cta = lines[-1:]
    middle = lines[2:-1] if len(lines) > 3 else []
    turn = middle[:1]
    point = middle[1:] if len(middle) > 1 else middle
    return {"hook": hook, "turn": turn, "point": point, "cta": cta}
