"""CRUD helpers for core entities."""

from __future__ import annotations

import json
import sqlite3
from typing import Iterable

from app.modules.data_store.models import (
    CommentLinkRecord,
    CommissionRecord,
    ProductRecord,
    VideoRecord,
)


def upsert_video(conn: sqlite3.Connection, item: VideoRecord) -> int:
    conn.execute(
        """
        INSERT INTO videos (
            source_url, bvid, aid, title, cover_url, cover_path, video_path, subtitle_text,
            subtitle_path, up_name, up_mid, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_url) DO UPDATE SET
            bvid = excluded.bvid,
            aid = excluded.aid,
            title = excluded.title,
            cover_url = excluded.cover_url,
            cover_path = excluded.cover_path,
            video_path = excluded.video_path,
            subtitle_text = excluded.subtitle_text,
            subtitle_path = excluded.subtitle_path,
            up_name = excluded.up_name,
            up_mid = excluded.up_mid,
            published_at = excluded.published_at
        """,
        (
            item.source_url,
            item.bvid,
            item.aid,
            item.title,
            item.cover_url,
            item.cover_path,
            item.video_path,
            item.subtitle_text,
            item.subtitle_path,
            item.up_name,
            item.up_mid,
            item.published_at,
        ),
    )
    row = conn.execute(
        "SELECT id FROM videos WHERE source_url = ?",
        (item.source_url,),
    ).fetchone()
    return int(row["id"])


def replace_comment_links(
    conn: sqlite3.Connection, video_id: int, links: Iterable[CommentLinkRecord]
) -> int:
    conn.execute("DELETE FROM comment_links WHERE video_id = ?", (video_id,))
    count = 0
    for link in links:
        conn.execute(
            """
            INSERT INTO comment_links (
                video_id, comment_id, is_top, platform, raw_link, resolved_link, product_id, comment_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video_id,
                link.comment_id,
                1 if link.is_top else 0,
                link.platform,
                link.raw_link,
                link.resolved_link,
                link.product_id,
                link.comment_text,
            ),
        )
        count += 1
    return count


def upsert_products(conn: sqlite3.Connection, items: Iterable[ProductRecord]) -> list[int]:
    product_ids: list[int] = []
    for item in items:
        conn.execute(
            """
            INSERT INTO products (
                platform, product_id, name, detail_url, category, price,
                commission_rate, estimated_income, tags, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(platform, product_id) DO UPDATE SET
                name = excluded.name,
                detail_url = excluded.detail_url,
                category = excluded.category,
                price = excluded.price,
                commission_rate = excluded.commission_rate,
                estimated_income = excluded.estimated_income,
                tags = excluded.tags,
                status = excluded.status
            """,
            (
                item.platform,
                item.product_id,
                item.name,
                item.detail_url,
                item.category,
                item.price,
                item.commission_rate,
                item.estimated_income,
                item.tags,
                item.status,
            ),
        )
        row = conn.execute(
            "SELECT id FROM products WHERE platform = ? AND product_id = ?",
            (item.platform, item.product_id),
        ).fetchone()
        product_ids.append(int(row["id"]))
    return product_ids


def link_products_to_video(
    conn: sqlite3.Connection, video_id: int, product_db_ids: Iterable[int], source_comment: str
) -> None:
    for pid in product_db_ids:
        conn.execute(
            """
            INSERT OR IGNORE INTO product_sources (product_id, video_id, source_comment)
            VALUES (?, ?, ?)
            """,
            (pid, video_id, source_comment),
        )


def merge_commission(
    links: Iterable[CommentLinkRecord], commissions: dict[tuple[str, str], CommissionRecord]
) -> list[ProductRecord]:
    merged: dict[tuple[str, str], ProductRecord] = {}
    for link in links:
        if not link.product_id:
            continue
        key = (link.platform, link.product_id)
        if key not in merged:
            merged[key] = ProductRecord(
                platform=link.platform,
                product_id=link.product_id,
                detail_url=link.resolved_link,
                name=f"{link.platform}-{link.product_id}",
            )
        comm = commissions.get(key)
        if comm:
            merged[key].commission_rate = comm.commission_rate
            merged[key].estimated_income = comm.estimated_income
    return list(merged.values())


def list_products(conn: sqlite3.Connection, limit: int = 100) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, platform, product_id, name, category, detail_url, commission_rate,
               estimated_income, score, created_at
        FROM products
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def list_comment_links(conn: sqlite3.Connection, video_id: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, comment_id, is_top, platform, raw_link, resolved_link, product_id, comment_text
        FROM comment_links
        WHERE video_id = ?
        ORDER BY id DESC
        """,
        (video_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def save_task(
    conn: sqlite3.Connection,
    task_id: str,
    task_type: str,
    status: str,
    payload: dict | None = None,
    result: dict | None = None,
    error_text: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO tasks (id, task_type, status, payload_json, result_json, error_text, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            status = excluded.status,
            payload_json = excluded.payload_json,
            result_json = excluded.result_json,
            error_text = excluded.error_text,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            task_id,
            task_type,
            status,
            json.dumps(payload or {}, ensure_ascii=False),
            json.dumps(result or {}, ensure_ascii=False),
            error_text,
        ),
    )
