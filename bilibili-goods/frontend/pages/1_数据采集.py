import streamlit as st
import pandas as pd
import requests


st.title("1. 数据采集")
st.caption("对标视频解析、评论商品提取、佣金查询、入库导出。")

# 统一 API 地址配置，便于本地/远程切换。
api_base = st.text_input("后端地址", value="http://127.0.0.1:8000").rstrip("/")

st.markdown("### 输入对标视频链接（每行一个）")
urls_text = st.text_area(
    "视频链接",
    placeholder="https://www.bilibili.com/video/BVxxxx\nhttps://www.bilibili.com/video/BVyyyy",
    height=140,
)
download_video = st.checkbox("同时下载视频文件（依赖 yutto）", value=False)

col1, col2, col3 = st.columns(3)


def _parse_urls(raw: str) -> list[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]


def _safe_request(method: str, url: str, **kwargs):
    """统一请求封装，避免前端因网络错误直接崩溃。"""
    try:
        return requests.request(method, url, **kwargs)
    except Exception as exc:
        st.error(f"请求失败：{exc}")
        return None


with col1:
    if st.button("同步采集（等待完成）", type="primary", use_container_width=True):
        urls = _parse_urls(urls_text)
        if not urls:
            st.warning("请先输入至少一个视频链接。")
        else:
            with st.spinner("正在采集，请稍候..."):
                resp = _safe_request(
                    "POST",
                    f"{api_base}/api/collect/run",
                    json={"video_urls": urls, "download_video": download_video},
                    timeout=300,
                )
            if resp is None:
                st.stop()
            if resp.ok:
                data = resp.json()
                st.success(
                    f"完成：成功 {data['success_videos']}/{data['total_videos']} 个视频，"
                    f"提取链接 {data['total_links']} 条，商品 {data['total_products']} 个。"
                )
                rows = []
                for item in data.get("videos", []):
                    for p in item.get("products", []):
                        rows.append(
                            {
                                "video_id": item["video_id"],
                                "platform": p.get("platform", ""),
                                "product_id": p.get("product_id", ""),
                                "name": p.get("name", ""),
                                "commission_rate": p.get("commission_rate", 0),
                                "estimated_income": p.get("estimated_income", 0),
                            }
                        )
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.error(f"采集失败：{resp.text}")

with col2:
    if st.button("异步采集（后台运行）", use_container_width=True):
        urls = _parse_urls(urls_text)
        if not urls:
            st.warning("请先输入至少一个视频链接。")
        else:
            resp = _safe_request(
                "POST",
                f"{api_base}/api/collect/run-async",
                json={"video_urls": urls, "download_video": download_video},
                timeout=30,
            )
            if resp is None:
                st.stop()
            if resp.ok:
                task_id = resp.json().get("task_id")
                st.session_state["collect_task_id"] = task_id
                st.success(f"已提交任务：{task_id}")
            else:
                st.error(f"提交失败：{resp.text}")

with col3:
    if st.button("导出商品Excel", use_container_width=True):
        resp = _safe_request("POST", f"{api_base}/api/products/export", timeout=60)
        if resp is None:
            st.stop()
        if resp.ok:
            st.info(f"导出完成：{resp.json().get('excel_path')}")
        else:
            st.error(f"导出失败：{resp.text}")

task_id = st.session_state.get("collect_task_id")
if task_id:
    st.markdown("### 异步任务状态")
    resp = _safe_request("GET", f"{api_base}/api/tasks/{task_id}", timeout=30)
    if resp is None:
        st.stop()
    if resp.ok:
        task = resp.json()
        st.json(task)
        if task.get("status") == "SUCCESS":
            st.success("任务已完成。")
        elif task.get("status") == "FAILED":
            st.error(f"任务失败：{task.get('error_text', '')}")
    else:
        st.warning(f"无法获取任务状态：{resp.text}")
