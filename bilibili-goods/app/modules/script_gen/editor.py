"""脚本编辑管理（内存版）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ScriptVersion:
    version: int
    content: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


_SCRIPT_STORE: dict[str, list[ScriptVersion]] = {}


def save_script_version(script_id: str, content: str) -> ScriptVersion:
    versions = _SCRIPT_STORE.setdefault(script_id, [])
    next_version = len(versions) + 1
    item = ScriptVersion(version=next_version, content=content)
    versions.append(item)
    return item


def get_script_versions(script_id: str) -> list[dict]:
    versions = _SCRIPT_STORE.get(script_id, [])
    return [{"version": v.version, "content": v.content, "created_at": v.created_at} for v in versions]
