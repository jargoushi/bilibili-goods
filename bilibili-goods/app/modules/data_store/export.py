"""Excel export helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3

import pandas as pd

from app.config import settings


def export_products_excel(conn: sqlite3.Connection, output_path: Path | None = None) -> Path:
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = settings.excel_output_dir / f"goods_pool_{ts}.xlsx"

    products_df = pd.read_sql_query(
        """
        SELECT id, platform, product_id, name, detail_url, category, price,
               commission_rate, estimated_income, score, tags, status, created_at
        FROM products
        ORDER BY commission_rate DESC, estimated_income DESC
        """,
        conn,
    )

    source_df = pd.read_sql_query(
        """
        SELECT ps.product_id, p.platform, p.product_id AS platform_product_id, ps.video_id,
               ps.source_comment, ps.created_at
        FROM product_sources ps
        JOIN products p ON p.id = ps.product_id
        ORDER BY ps.id DESC
        """,
        conn,
    )

    comments_df = pd.read_sql_query(
        """
        SELECT cl.video_id, cl.comment_id, cl.platform, cl.product_id, cl.resolved_link, cl.comment_text
        FROM comment_links cl
        ORDER BY cl.id DESC
        """,
        conn,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        products_df.to_excel(writer, sheet_name="商品池", index=False)
        source_df.to_excel(writer, sheet_name="来源映射", index=False)
        comments_df.to_excel(writer, sheet_name="评论链接", index=False)
    return output_path
