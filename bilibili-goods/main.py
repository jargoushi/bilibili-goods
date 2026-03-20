"""Unified launcher for API and Streamlit UI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parent


def _spawn(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.Popen:
    return subprocess.Popen(cmd, cwd=PROJECT_ROOT, env=env)


def _stop_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()


def _run_api(host: str, port: int, reload_enabled: bool) -> subprocess.Popen:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload_enabled:
        cmd.append("--reload")
    return _spawn(cmd)


def _run_ui(port: int) -> subprocess.Popen:
    _prepare_streamlit_config()
    # 关闭首次启动邮箱收集提示，避免交互阻塞导致 8501 端口起不来。
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_GLOBAL_EMAIL"] = ""
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/streamlit_app.py",
        "--server.port",
        str(port),
        "--browser.gatherUsageStats",
        "false",
    ]
    return _spawn(cmd, env=env)


def _prepare_streamlit_config() -> None:
    """准备 Streamlit 配置，避免首次启动进入交互提问。"""
    streamlit_dir = Path.home() / ".streamlit"
    streamlit_dir.mkdir(parents=True, exist_ok=True)

    credentials_file = streamlit_dir / "credentials.toml"
    if not credentials_file.exists():
        credentials_file.write_text('[general]\nemail = ""\n', encoding="utf-8")

    config_file = streamlit_dir / "config.toml"
    # 若配置文件不存在则写入基础配置；存在则保持用户已有配置不覆盖。
    if not config_file.exists():
        config_file.write_text(
            "[browser]\n"
            "gatherUsageStats = false\n",
            encoding="utf-8",
        )


def _monitor(processes: list[subprocess.Popen]) -> int:
    try:
        while True:
            for proc in processes:
                code = proc.poll()
                if code is not None:
                    return code
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        for proc in processes:
            _stop_process(proc)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bilibili goods project launcher",
    )
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument("--api-host", default="127.0.0.1", help="API host")
    parser.add_argument("--api-port", type=int, default=8000, help="API port")
    parser.add_argument("--ui-port", type=int, default=8501, help="Streamlit port")
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable uvicorn reload mode",
    )

    subparsers.add_parser("all", help="Start API + UI")
    subparsers.add_parser("api", help="Start API only")
    subparsers.add_parser("ui", help="Start UI only")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    command = args.command or "all"
    reload_enabled = not args.no_reload

    if command == "api":
        print(f"[launcher] API -> http://{args.api_host}:{args.api_port}")
        proc = _run_api(args.api_host, args.api_port, reload_enabled)
        return _monitor([proc])

    if command == "ui":
        print(f"[launcher] UI  -> http://127.0.0.1:{args.ui_port}")
        proc = _run_ui(args.ui_port)
        return _monitor([proc])

    print(f"[launcher] API -> http://{args.api_host}:{args.api_port}")
    print(f"[launcher] UI  -> http://127.0.0.1:{args.ui_port}")
    procs = [
        _run_api(args.api_host, args.api_port, reload_enabled),
        _run_ui(args.ui_port),
    ]
    return _monitor(procs)


if __name__ == "__main__":
    raise SystemExit(main())
