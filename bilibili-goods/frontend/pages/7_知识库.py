import streamlit as st
import pandas as pd

from app.modules.script_library.library import add_component, search_components
from app.modules.script_library.parser import split_script_components

st.title("7. 知识库")
st.caption("脚本库、对标档案、模板管理。")

st.markdown("### 脚本拆解")
raw_script = st.text_area(
    "粘贴脚本文本",
    value="开头先讲痛点。\n然后说为什么这个产品值得买。\n卖点1：体积小。\n卖点2：续航强。\n结尾引导评论区互动。",
)
if st.button("拆解脚本"):
    comp = split_script_components(raw_script)
    st.json(comp)

st.markdown("### 组件入库")
comp_type = st.selectbox("组件类型", options=["hook", "turn", "point", "cta"])
comp_content = st.text_input("组件内容")
comp_tags = st.text_input("标签（逗号分隔）", value="学生,宿舍")
if st.button("保存组件"):
    tags = [x.strip() for x in comp_tags.split(",") if x.strip()]
    add_component(component_type=comp_type, content=comp_content, tags=tags)
    st.success("已保存到内存知识库。")

st.markdown("### 组件检索")
search_type = st.selectbox("按类型筛选", options=["", "hook", "turn", "point", "cta"])
search_tags = st.text_input("标签筛选（逗号分隔）")
if st.button("查询组件"):
    rows = search_components(
        component_type=search_type or None,
        tags=[x.strip() for x in search_tags.split(",") if x.strip()],
    )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
