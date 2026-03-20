import streamlit as st
import pandas as pd
import requests


st.title("2. 商品库")
st.caption("统一数据库、筛选、排序、导出。")

api_base = st.text_input("后端地址", value="http://127.0.0.1:8000").rstrip("/")
limit = st.slider("加载数量", min_value=20, max_value=500, value=100, step=20)


def _safe_request(method: str, url: str, **kwargs):
    try:
        return requests.request(method, url, **kwargs)
    except Exception as exc:
        st.error(f"请求失败：{exc}")
        return None


if st.button("刷新商品数据", type="primary"):
    resp = _safe_request("GET", f"{api_base}/api/products", params={"limit": limit}, timeout=60)
    if resp is None:
        st.stop()
    if resp.ok:
        st.session_state["products_rows"] = resp.json()
    else:
        st.error(f"获取失败：{resp.text}")

rows = st.session_state.get("products_rows", [])
if rows:
    df = pd.DataFrame(rows)
    platform_filter = st.multiselect(
        "平台筛选",
        options=sorted(df["platform"].dropna().unique().tolist()),
        default=sorted(df["platform"].dropna().unique().tolist()),
    )
    if platform_filter:
        df = df[df["platform"].isin(platform_filter)]
    st.dataframe(df, use_container_width=True)
else:
    st.info("当前没有商品数据，请先刷新或去“数据采集”页面跑一次采集。")

if st.button("导出当前商品池Excel"):
    resp = _safe_request("POST", f"{api_base}/api/products/export", timeout=60)
    if resp is None:
        st.stop()
    if resp.ok:
        st.success(f"导出完成：{resp.json().get('excel_path')}")
    else:
        st.error(f"导出失败：{resp.text}")
