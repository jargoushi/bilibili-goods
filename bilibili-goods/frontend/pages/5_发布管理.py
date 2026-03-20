import streamlit as st
import pandas as pd

from app.modules.blue_link.checklist import build_publish_checklist
from app.modules.blue_link.formatter import format_blue_link_comment
from app.modules.cover.generator import generate_cover_plan

st.title("5. 发布管理")
st.caption("封面生成、蓝链格式化、发布清单。")

title = st.text_input("视频标题", value="学生党宿舍必备3个实用好物")
category = st.text_input("品类", value="宿舍好物")

if st.button("生成封面方案", type="primary"):
    plans = generate_cover_plan(title=title, category=category)
    st.dataframe(pd.DataFrame(plans), use_container_width=True)

st.markdown("### 蓝链文案")
items_text = st.text_area(
    "商品清单（每行：名称,链接）",
    value="便携榨汁杯,https://item.jd.com/10000001.html\n桌面收纳盒,https://detail.tmall.com/item.htm?id=1234567890",
)
if st.button("生成蓝链评论文本"):
    items = []
    for line in items_text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [x.strip() for x in line.split(",", 1)]
        if len(parts) == 2:
            items.append({"name": parts[0], "detail_url": parts[1]})
    content = format_blue_link_comment(items)
    st.text_area("蓝链评论", value=content, height=200)

st.markdown("### 发布清单")
has_cover = st.checkbox("封面已确认", value=False)
has_blue_link = st.checkbox("蓝链已准备", value=False)
if st.button("生成发布Checklist"):
    checklist = build_publish_checklist(title=title, has_cover=has_cover, has_blue_link=has_blue_link)
    st.dataframe(pd.DataFrame(checklist), use_container_width=True)
