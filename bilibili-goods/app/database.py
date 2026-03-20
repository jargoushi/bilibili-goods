"""SQLite helpers and schema bootstrap."""

from contextlib import contextmanager
import sqlite3
from typing import Iterator

from app.config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_url TEXT NOT NULL UNIQUE,
    bvid TEXT,
    aid INTEGER,
    title TEXT,
    cover_url TEXT,
    cover_path TEXT,
    video_path TEXT,
    subtitle_text TEXT,
    subtitle_path TEXT,
    up_name TEXT,
    up_mid INTEGER,
    published_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    product_id TEXT,
    name TEXT,
    detail_url TEXT,
    category TEXT,
    price REAL DEFAULT 0,
    commission_rate REAL DEFAULT 0,
    estimated_income REAL DEFAULT 0,
    selling_points TEXT,
    params_json TEXT,
    tags TEXT,
    score REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    source_comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS comment_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    comment_id TEXT,
    is_top INTEGER DEFAULT 0,
    platform TEXT,
    raw_link TEXT,
    resolved_link TEXT,
    product_id TEXT,
    comment_text TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    result_json TEXT,
    error_text TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_products_platform_pid
ON products(platform, product_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_product_sources_unique
ON product_sources(product_id, video_id, source_comment);

CREATE INDEX IF NOT EXISTS idx_comment_links_video_id
ON comment_links(video_id);

CREATE INDEX IF NOT EXISTS idx_comment_links_platform_pid
ON comment_links(platform, product_id);
"""


def init_db() -> None:
    """Initialize local SQLite schema."""
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.video_output_dir.mkdir(parents=True, exist_ok=True)
    settings.excel_output_dir.mkdir(parents=True, exist_ok=True)
    settings.script_output_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.database_path) as conn:
        conn.executescript(SCHEMA)
        _run_migrations(conn)
        conn.commit()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Yield a sqlite connection with row factory enabled."""
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _run_migrations(conn: sqlite3.Connection) -> None:
    """Best-effort migration for early local schema versions."""
    expected_columns = {
        "videos": {
            "bvid": "TEXT",
            "aid": "INTEGER",
            "cover_url": "TEXT",
            "video_path": "TEXT",
            "subtitle_text": "TEXT",
            "up_name": "TEXT",
            "up_mid": "INTEGER",
            "published_at": "TEXT",
        },
        "products": {
            "detail_url": "TEXT",
            "price": "REAL DEFAULT 0",
            "score": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'active'",
        },
    }
    for table_name, columns in expected_columns.items():
        existing = _get_columns(conn, table_name)
        for col_name, col_type in columns.items():
            if col_name not in existing:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")


def _get_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {str(row[1]) for row in rows}
