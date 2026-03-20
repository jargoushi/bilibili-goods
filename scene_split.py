"""
视频场景分割脚本
基于 PySceneDetect 检测画面变化，每个场景截取第一帧保存为图片。

依赖安装:
  pip install scenedetect[opencv]

用法: 修改 main() 中的 video_path，然后运行:
  python scene_split.py
"""

from pathlib import Path
from scenedetect import open_video, SceneManager, ContentDetector


def split_scenes(video_path: str):
    """检测场景并保存每个场景的第一帧"""
    src = Path(video_path)
    if not src.is_file():
        print(f"错误: 文件不存在 -> {src}")
        return

    # 创建输出目录
    out_dir = src.parent / f"{src.stem}_scenes"
    out_dir.mkdir(exist_ok=True)

    # 打开视频并检测场景
    video = open_video(str(src))
    scene_manager = SceneManager()
    # 降低阈值 (默认是 27.0)，值越小越灵敏，越容易检测到场景变化，适合解决"漏检"
    # min_scene_len=15 避免将极短的闪烁(半秒内)误认为场景
    scene_manager.add_detector(ContentDetector(threshold=20.0, min_scene_len=15))
    scene_manager.detect_scenes(video, show_progress=True)

    scene_list = scene_manager.get_scene_list()
    print(f"\n检测到 {len(scene_list)} 个场景")

    if not scene_list:
        print("未检测到场景变化。")
        return

    # 保存每个场景的一张截图
    from scenedetect.scene_manager import save_images
    save_images(
        scene_list=scene_list,
        video=video,
        num_images=1,          # 每个场景只截 1 张
        output_dir=str(out_dir),
        image_name_template="$SCENE_NUMBER",
        frame_margin=1,        # 关键！值为1表示不截取第一帧，而是截取场景的中间帧，避免截到转场过程
    )

    print(f"完成! 图片已保存到: {out_dir}")


def main():
    # ===== 在这里修改视频路径 =====
    video_path = r"D:\py-workspace\my-fullstack-app\bilibili-goods-workspace\对标视频.mp4"
    # ==============================

    split_scenes(video_path)


if __name__ == "__main__":
    main()
