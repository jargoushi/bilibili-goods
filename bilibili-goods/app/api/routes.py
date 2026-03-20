"""HTTP 路由：打通 MVP 采集闭环。"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.database import get_conn
from app.modules.commission.jd_union import query_jd_commission
from app.modules.commission.taobao_union import query_taobao_commission
from app.modules.data_store.crud import (
    link_products_to_video,
    list_comment_links,
    list_products as list_products_db,
    merge_commission,
    replace_comment_links,
    save_task,
    upsert_products,
    upsert_video,
)
from app.modules.data_store.export import export_products_excel
from app.modules.link_extractor.comment_crawler import crawl_comment_links
from app.modules.video_parser.downloader import parse_video_url, record_to_dict
from app.services.task_queue import task_queue


router = APIRouter(prefix="/api", tags=["core"])


class CollectRequest(BaseModel):
    video_urls: list[str] = Field(default_factory=list, description="对标视频链接列表")
    download_video: bool = Field(default=False, description="是否下载视频文件")


def _collect_pipeline(video_urls: list[str], download_video: bool) -> dict[str, Any]:
    """核心采集流水线（同步）。"""
    if not video_urls:
        raise ValueError("video_urls 不能为空")

    summary: dict[str, Any] = {
        "total_videos": len(video_urls),
        "success_videos": 0,
        "total_links": 0,
        "total_products": 0,
        "videos": [],
    }

    for url in video_urls:
        # 1) 解析视频
        video_record = parse_video_url(url, download_video=download_video)
        link_records = []
        if video_record.aid:
            # 2) 抓评论并提取商品链接
            link_records = crawl_comment_links(aid=video_record.aid)

        # 3) 佣金查询（按平台分组）
        jd_ids = sorted({item.product_id for item in link_records if item.platform == "jd"})
        tb_ids = sorted({item.product_id for item in link_records if item.platform == "taobao"})
        commission_map = {}
        commission_map.update(query_jd_commission(jd_ids))
        commission_map.update(query_taobao_commission(tb_ids))

        # 4) 入库
        with get_conn() as conn:
            video_id = upsert_video(conn, video_record)
            link_count = replace_comment_links(conn, video_id, link_records)
            product_records = merge_commission(link_records, commission_map)
            product_db_ids = upsert_products(conn, product_records)
            link_products_to_video(conn, video_id, product_db_ids, source_comment="auto_collect")
            conn.commit()

        # 5) 汇总结果
        summary["success_videos"] += 1
        summary["total_links"] += link_count
        summary["total_products"] += len(product_db_ids)
        summary["videos"].append(
            {
                "video_id": video_id,
                "video": record_to_dict(video_record),
                "link_count": link_count,
                "product_count": len(product_db_ids),
                "products": [asdict(p) for p in product_records],
            }
        )
    return summary


@router.get("/health")
def api_health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/products")
def list_products(limit: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    with get_conn() as conn:
        return list_products_db(conn, limit=limit)


@router.post("/collect/run")
def run_collect(req: CollectRequest) -> dict[str, Any]:
    """同步采集接口：请求返回时任务已完成。"""
    try:
        return _collect_pipeline(req.video_urls, req.download_video)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/collect/run-async")
def run_collect_async(req: CollectRequest) -> dict[str, Any]:
    """异步采集接口：立即返回 task_id。"""
    payload = req.model_dump()
    task_id = task_queue.submit(
        task_type="collect",
        payload=payload,
        fn=_collect_pipeline,
        video_urls=req.video_urls,
        download_video=req.download_video,
    )
    with get_conn() as conn:
        save_task(conn, task_id=task_id, task_type="collect", status="PENDING", payload=payload)
        conn.commit()
    return {"task_id": task_id, "status": "PENDING"}


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, Any]:
    """查询异步任务状态。"""
    state = task_queue.to_dict(task_id)
    if state:
        with get_conn() as conn:
            save_task(
                conn,
                task_id=task_id,
                task_type=state["task_type"],
                status=state["status"],
                payload=state["payload"],
                result=state["result"],
                error_text=state["error_text"],
            )
            conn.commit()
        return state

    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="task not found")
    return dict(row)


@router.get("/videos")
def list_videos(limit: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, source_url, bvid, aid, title, up_name, created_at
            FROM videos
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


@router.get("/videos/{video_id}/links")
def get_video_links(video_id: int) -> list[dict]:
    with get_conn() as conn:
        return list_comment_links(conn, video_id=video_id)


@router.post("/products/export")
def export_products() -> dict[str, str]:
    """导出商品池 Excel。"""
    with get_conn() as conn:
        out_path = export_products_excel(conn)
    return {"excel_path": str(Path(out_path).resolve())}
