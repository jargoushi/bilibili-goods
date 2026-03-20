"""Streamlit dashboard entrypoint."""

import streamlit as st


st.set_page_config(
    page_title="B站好物工业化操作台",
    page_icon="B",
    layout="wide",
)

st.title("B站好物工业化生产操作台（MVP骨架）")
st.write("当前页面用于统一导航。请从左侧进入各功能页。")

st.markdown(
    """
### 当前已搭建
- 数据采集、商品库、选品中心、内容生产、发布管理、运营数据、知识库页面
- FastAPI 后端基础接口与 SQLite 初始化
- 目录结构与模块占位文件（可按阶段逐步填充业务逻辑）
"""
)
