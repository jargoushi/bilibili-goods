"""脚本组件库（内存版）。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScriptComponent:
    component_type: str
    content: str
    tags: list[str]


# TODO: 后续切换为数据库持久化。
SCRIPT_COMPONENTS: list[ScriptComponent] = []


def add_component(component_type: str, content: str, tags: list[str] | None = None) -> None:
    SCRIPT_COMPONENTS.append(
        ScriptComponent(component_type=component_type, content=content, tags=tags or [])
    )


def search_components(component_type: str | None = None, tags: list[str] | None = None) -> list[dict]:
    tags = tags or []
    rows = SCRIPT_COMPONENTS
    if component_type:
        rows = [x for x in rows if x.component_type == component_type]
    if tags:
        rows = [x for x in rows if set(tags).issubset(set(x.tags))]
    return [{"type": x.component_type, "content": x.content, "tags": x.tags} for x in rows]
