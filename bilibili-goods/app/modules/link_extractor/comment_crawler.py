"""评论抓取与商品链接提取。"""

from __future__ import annotations

import asyncio
from typing import Any

from app.modules.data_store.models import CommentLinkRecord
from app.modules.link_extractor.link_parser import extract_links_from_text, normalize_link


def crawl_comment_links(aid: int, max_pages: int = 3) -> list[CommentLinkRecord]:
    """抓取评论并提取商品链接。

    说明：
    - 依赖 bilibili-api-python。
    - 若当前环境未安装，将返回空列表（不中断主流程）。
    """
    try:
        return asyncio.run(_crawl_comment_links_async(aid=aid, max_pages=max_pages))
    except Exception:
        # TODO: 接入日志系统记录详细错误。
        return []


async def _crawl_comment_links_async(aid: int, max_pages: int) -> list[CommentLinkRecord]:
    from bilibili_api import comment

    result_records: list[CommentLinkRecord] = []
    seen: set[tuple[str, str, str]] = set()

    # 先抓第1页，优先拿置顶评论。
    first_page = await comment.get_comments(
        oid=aid,
        type_=comment.CommentResourceType.VIDEO,
        page_index=1,
        order=comment.OrderType.LIKE,
        credential=None,
    )
    _collect_from_result(first_page, result_records, seen)

    # 再抓后续页，补充普通评论中的链接。
    for page_index in range(2, max_pages + 1):
        try:
            page_data = await comment.get_comments(
                oid=aid,
                type_=comment.CommentResourceType.VIDEO,
                page_index=page_index,
                order=comment.OrderType.LIKE,
                credential=None,
            )
        except Exception:
            break
        _collect_from_result(page_data, result_records, seen)

    return result_records


def _collect_from_result(
    page_data: dict[str, Any],
    result_records: list[CommentLinkRecord],
    seen: set[tuple[str, str, str]],
) -> None:
    top = (page_data.get("upper") or {}).get("top")
    if isinstance(top, dict):
        _extract_from_reply(top, is_top=True, target=result_records, seen=seen)

    for reply in page_data.get("replies") or []:
        if isinstance(reply, dict):
            _extract_from_reply(reply, is_top=False, target=result_records, seen=seen)


def _extract_from_reply(
    reply: dict[str, Any],
    is_top: bool,
    target: list[CommentLinkRecord],
    seen: set[tuple[str, str, str]],
) -> None:
    content = reply.get("content") or {}
    message = str(content.get("message") or "")
    comment_id = str(reply.get("rpid") or "")

    raw_links: list[str] = []
    raw_links.extend(extract_links_from_text(message))

    # B站评论的 jump_url 里通常包含蓝链。
    jump_url = content.get("jump_url") or {}
    if isinstance(jump_url, dict):
        raw_links.extend(list(jump_url.keys()))

    for raw_link in raw_links:
        resolved_link, platform, product_id = normalize_link(raw_link)
        if platform == "unknown":
            continue
        key = (comment_id, platform, product_id or resolved_link)
        if key in seen:
            continue
        seen.add(key)
        target.append(
            CommentLinkRecord(
                comment_id=comment_id,
                is_top=is_top,
                raw_link=raw_link,
                resolved_link=resolved_link,
                platform=platform,
                product_id=product_id,
                comment_text=message[:300],
            )
        )
