"""通用爬虫引擎基类（请求、下载、短链还原）。"""

from __future__ import annotations

from pathlib import Path
import time

import requests

from app.config import settings


class CrawlerEngine:
    """统一封装 HTTP 请求，给各抓取模块复用。"""

    def __init__(self) -> None:
        self.session = requests.Session()
        # 统一 User-Agent，避免不同模块各自定义造成不一致。
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            }
        )

    def get_text(self, url: str, timeout: int | None = None) -> str:
        """获取文本内容，内置重试。"""
        response = self._request("GET", url, timeout=timeout)
        return response.text

    def get_json(self, url: str, timeout: int | None = None) -> dict:
        """获取 JSON 内容，失败时抛出异常给上层处理。"""
        response = self._request("GET", url, timeout=timeout)
        return response.json()

    def resolve_short_link(self, url: str) -> str:
        """短链还原：跟随重定向拿到最终链接。"""
        try:
            resp = self.session.get(
                url,
                allow_redirects=True,
                timeout=settings.request_timeout_seconds,
            )
            return str(resp.url)
        except Exception:
            # 还原失败时返回原始链接，避免主流程中断。
            return url

    def download_file(self, url: str, dest: Path) -> Path:
        """下载二进制文件到指定路径。"""
        dest.parent.mkdir(parents=True, exist_ok=True)
        response = self._request("GET", url, stream=True)
        with dest.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return dest

    def _request(
        self,
        method: str,
        url: str,
        timeout: int | None = None,
        stream: bool = False,
    ) -> requests.Response:
        """统一请求入口：重试 + 退避 + 状态码校验。"""
        timeout = timeout or settings.request_timeout_seconds
        last_error: Exception | None = None
        for idx in range(settings.max_retry):
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=timeout,
                    stream=stream,
                )
                response.raise_for_status()
                return response
            except Exception as exc:
                last_error = exc
                # 简单指数退避，避免请求瞬间打满。
                time.sleep(0.5 * (idx + 1))
        raise RuntimeError(f"请求失败: {url}") from last_error


crawler_engine = CrawlerEngine()
