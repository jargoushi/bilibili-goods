import streamlit as st
import pandas as pd

from app.modules.operation.comment_monitor import classify_comments
from app.modules.operation.dashboard import build_dashboard_metrics
from app.modules.operation.reply_advisor import build_reply_suggestion
from app.modules.operation.revenue_report import build_revenue_report

st.title("6. 运营数据")
st.caption("评论监控、数据看板、收益报表。")

st.markdown("### 评论分类与回复建议")
comments_text = st.text_area(
    "最新评论（每行一条）",
    value="这个适合学生宿舍吗？\n参数是多少？\n多少钱能拿下？",
)
if st.button("分析评论"):
    comments = [x.strip() for x in comments_text.splitlines() if x.strip()]
    rows = classify_comments(comments)
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    if comments:
        st.text_area("首条评论建议回复", value=build_reply_suggestion(comments[0]), height=150)

st.markdown("### 运营看板")
play_count = st.number_input("播放量", min_value=0, value=10000, step=500)
like_count = st.number_input("点赞量", min_value=0, value=600, step=50)
comment_count = st.number_input("评论量", min_value=0, value=200, step=20)
gmv = st.number_input("GMV", min_value=0.0, value=5000.0, step=100.0)
commission_income = st.number_input("佣金", min_value=0.0, value=600.0, step=50.0)
if st.button("生成看板指标"):
    metrics = build_dashboard_metrics(play_count, like_count, comment_count, gmv, commission_income)
    st.json(metrics)

st.markdown("### 收益报表")
sample_rows = [
    {"video_id": 1, "gmv": 1200, "commission": 150},
    {"video_id": 2, "gmv": 1800, "commission": 210},
    {"video_id": 3, "gmv": 900, "commission": 88},
]
if st.button("生成示例收益报表"):
    report = build_revenue_report(sample_rows)
    st.json(report)
