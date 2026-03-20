import streamlit as st
import pandas as pd
import requests

from app.modules.benchmark.analyzer import analyze_difference
from app.modules.recommender.hot_calendar import get_today_hot_topics
from app.modules.recommender.recommender import recommend_products
from app.modules.scorer.scorer import score_product

st.title("3. 选品中心")
st.caption("热点日历、产品评分、对标差异分析。")

api_base = st.text_input("后端地址", value="http://127.0.0.1:8000").rstrip("/")
hot_topics = get_today_hot_topics()
st.write("今日热点：", " / ".join(hot_topics))

if st.button("加载商品并生成推荐", type="primary"):
    resp = requests.get(f"{api_base}/api/products", params={"limit": 200}, timeout=60)
    if resp.ok:
        rows = resp.json()
        if not rows:
            st.info("没有可推荐商品，请先去“数据采集”页面采集数据。")
        else:
            scored = []
            for row in rows:
                detail = score_product(
                    commission_rate=float(row.get("commission_rate", 0)),
                    selling_point_count=3,
                    competition_score=0.7,
                    comment_heat_score=0.6,
                )
                item = dict(row)
                item.update(detail)
                scored.append(item)
            rec = recommend_products(scored, top_n=20)
            st.dataframe(pd.DataFrame(rec), use_container_width=True)
    else:
        st.error(resp.text)

st.markdown("### 对标差异分析")
benchmark_script = st.text_area("粘贴对标脚本", height=120)
my_points = st.text_area("你的卖点（每行一个）", height=120)
if st.button("生成差异建议"):
    result = analyze_difference(
        benchmark_script=benchmark_script,
        my_points=[x.strip() for x in my_points.splitlines() if x.strip()],
    )
    st.json(result)
