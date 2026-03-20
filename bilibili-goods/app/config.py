"""Application settings."""

from dataclasses import dataclass
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = BASE_DIR.parent


@dataclass(frozen=True)
class Settings:
    app_name: str = "Bilibili Goods Factory"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    database_path: Path = Path(
        os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "db" / "app.db"))
    )
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "data" / "output")))
    video_output_dir: Path = Path(
        os.getenv("VIDEO_OUTPUT_DIR", str(BASE_DIR / "data" / "output" / "videos"))
    )
    excel_output_dir: Path = Path(
        os.getenv("EXCEL_OUTPUT_DIR", str(BASE_DIR / "data" / "output" / "excel"))
    )
    script_output_dir: Path = Path(
        os.getenv("SCRIPT_OUTPUT_DIR", str(BASE_DIR / "data" / "output" / "scripts"))
    )
    external_cookie_file: Path = Path(
        os.getenv("COOKIE_FILE", str(WORKSPACE_DIR / "cookie.txt"))
    )
    external_scripts_dir: Path = WORKSPACE_DIR
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    max_retry: int = int(os.getenv("MAX_RETRY", "3"))


settings = Settings()
