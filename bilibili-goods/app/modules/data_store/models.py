"""Data models used across the MVP pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VideoRecord:
    source_url: str
    title: str = ""
    bvid: str | None = None
    aid: int | None = None
    cover_url: str | None = None
    cover_path: str | None = None
    video_path: str | None = None
    subtitle_text: str = ""
    subtitle_path: str | None = None
    up_name: str | None = None
    up_mid: int | None = None
    published_at: str | None = None


@dataclass(slots=True)
class CommentLinkRecord:
    comment_id: str
    is_top: bool
    raw_link: str
    resolved_link: str
    platform: str
    product_id: str
    comment_text: str = ""


@dataclass(slots=True)
class CommissionRecord:
    platform: str
    product_id: str
    commission_rate: float
    estimated_income: float
    campaign_name: str = ""
    query_status: str = "ok"
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProductRecord:
    platform: str
    product_id: str
    name: str = ""
    detail_url: str | None = None
    category: str = ""
    price: float = 0.0
    commission_rate: float = 0.0
    estimated_income: float = 0.0
    tags: str = ""
    status: str = "active"
