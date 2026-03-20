import streamlit as st

from app.config import settings
from app.modules.edit_assist.edit_guide import generate_edit_guide
from app.modules.edit_assist.material_organizer import organize_materials
from app.modules.edit_assist.srt_generator import generate_srt_from_lines
from app.modules.script_gen.editor import get_script_versions, save_script_version
from app.modules.script_gen.generator import generate_script
from app.modules.tts.tts_manager import synthesize

st.title("4. 内容生产")
st.caption("脚本生成、TTS 配音、素材包整理。")

product_name = st.text_input("商品名称", value="便携榨汁杯")
target_crowd = st.text_input("目标人群", value="学生党")
points_text = st.text_area("卖点（每行一个）", value="轻便易携带\n充电一次可用多次\n清洗方便")

if st.button("生成脚本初稿", type="primary"):
    points = [x.strip() for x in points_text.splitlines() if x.strip()]
    script = generate_script(product_name=product_name, selling_points=points, target_crowd=target_crowd)
    script_id = product_name.strip() or "default_script"
    save_script_version(script_id=script_id, content=script)
    st.session_state["current_script_id"] = script_id
    st.text_area("脚本初稿", value=script, height=220)

script_id = st.session_state.get("current_script_id")
if script_id:
    versions = get_script_versions(script_id)
    st.write(f"当前脚本ID：{script_id}，版本数：{len(versions)}")
    st.dataframe(versions, use_container_width=True)

st.markdown("### TTS 合成")
engine = st.selectbox("引擎", options=["chattts", "cosyvoice"])
voice = st.text_input("音色", value="female_a")
tts_text = st.text_area("配音文本", value="这是一次 TTS 测试文本。")
if st.button("生成配音"):
    result = synthesize(text=tts_text, engine=engine, voice=voice)
    st.json(result)

st.markdown("### 剪辑辅助")
if st.button("生成素材结构与剪辑指引"):
    lines = [x.strip() for x in tts_text.splitlines() if x.strip()]
    output_dir = settings.output_dir / "edit_package"
    dirs = organize_materials(output_dir / "materials", segment_count=max(1, len(lines)))
    guide_path = generate_edit_guide(lines or ["示例段落"], output_dir / "edit_guide.md")
    srt_path = generate_srt_from_lines(lines or ["示例字幕"], output_dir / "subtitles.srt")
    st.write("素材目录：", dirs)
    st.write("剪辑指引：", str(guide_path))
    st.write("字幕文件：", str(srt_path))
