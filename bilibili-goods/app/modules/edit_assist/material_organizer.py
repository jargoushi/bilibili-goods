"""素材整理器。"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess

from app.config import settings


def organize_materials(base_dir: Path, segment_count: int) -> list[str]:
    """按脚本段落创建素材目录。"""
    base_dir.mkdir(parents=True, exist_ok=True)
    dirs = []
    for idx in range(1, segment_count + 1):
        d = base_dir / f"{idx:02d}_segment"
        d.mkdir(parents=True, exist_ok=True)
        dirs.append(str(d))
    return dirs


def run_scene_split_external(video_path: str) -> dict:
    """调用你现有的 `scene_split.py` 脚本。

    说明：
    - 这是桥接函数，便于逐步把老脚本能力并入新工程。
    """
    script = settings.external_scripts_dir / "scene_split.py"
    if not script.exists():
        return {"ok": False, "message": f"未找到脚本: {script}"}
    module = _load_module(script, "scene_split_external")
    if module and hasattr(module, "split_scenes"):
        module.split_scenes(video_path)
        return {"ok": True, "message": "scene_split 执行完成"}
    # 若导入失败，回退到直接调用脚本 main。
    proc = subprocess.run(["python", str(script)], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return {"ok": proc.returncode == 0, "message": "scene_split 已执行（fallback）"}


def run_video_trim_external(video_path: str, start: str, end: str) -> dict:
    """调用你现有的 `video_trim.py` 脚本。"""
    script = settings.external_scripts_dir / "video_trim.py"
    if not script.exists():
        return {"ok": False, "message": f"未找到脚本: {script}"}
    module = _load_module(script, "video_trim_external")
    if module and hasattr(module, "trim_video"):
        module.trim_video(video_path, start, end)
        out_path = str(Path(video_path).with_name(f"{Path(video_path).stem}_trimmed{Path(video_path).suffix}"))
        return {"ok": True, "message": "video_trim 执行完成", "output_path": out_path}
    proc = subprocess.run(["python", str(script)], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return {"ok": proc.returncode == 0, "message": "video_trim 已执行（fallback）"}


def _load_module(script_path: Path, module_name: str):
    """动态加载外部脚本模块。"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None
