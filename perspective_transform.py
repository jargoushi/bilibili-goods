"""
视频 3D 透视变形脚本
对视频进行透视变形，生成画中画素材，超出画布的拉伸部分自动裁掉。

依赖安装:
  pip install opencv-python numpy

用法: 修改 main() 中的视频路径和变形参数，然后运行:
  python perspective_transform.py
"""

from pathlib import Path

import cv2
import numpy as np


def apply_perspective_transform(
    input_path: str,
    output_path: str,
    tl_offset_x: float = -50,
    tl_offset_y: float = -80,
):
    """
    对视频应用 3D 透视变形（仅左上角向外拉伸，其余三个角保持不动）

    参数:
        input_path:   输入视频路径
        output_path:  输出视频路径
        tl_offset_x:  左上角水平偏移量（负值=向左拉，正值=向右推）
        tl_offset_y:  左上角垂直偏移量（负值=向上拉，正值=向下推）
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        print(f"[{input_path.name}] 不存在")
        return

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print(f"无法读取视频: {input_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if fps == 0 or np.isnan(fps):
       fps = 30.0 # fallback

    # 输出画布保持与原始尺寸一致，拉伸超出部分直接裁掉
    out_w = orig_w
    out_h = orig_h

    print("="*40)
    print(f"处理文件: {input_path.name}")
    print(f"分辨率: {orig_w}x{orig_h} @ {fps}fps")
    print(f"左上角偏移: x={tl_offset_x}, y={tl_offset_y}")
    print("="*40)

    # 原图 4 个顶点：左上, 右上, 左下, 右下
    pts_src = np.float32([
        [0, 0],
        [orig_w, 0],
        [0, orig_h],
        [orig_w, orig_h]
    ])

    # 目标图 4 个顶点
    # 右上、右下、左下保持原位，只有左上角发生位移
    # 超出画布范围的部分会被自动裁掉
    pts_dst = np.float32([
        [tl_offset_x, tl_offset_y],   # 左上角：向外拉伸（超出部分被裁掉）
        [orig_w, 0],                    # 右上角：原位不动
        [0, orig_h],                    # 左下角：原位不动
        [orig_w, orig_h]               # 右下角：原位不动
    ])

    # 获取透视变换矩阵
    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)

    # 设置输出 Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 执行透视变形
        warped_frame = cv2.warpPerspective(
            frame,
            matrix,
            (out_w, out_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)
        )

        writer.write(warped_frame)
        frame_count += 1

        if frame_count % 30 == 0 or frame_count == total_frames:
            progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
            print(f"\r处理进度: {progress:.1f}% ({frame_count}/{total_frames})", end="")

    print("\n\n完成！")
    print(f"文件输出在: {output_path}")

    cap.release()
    writer.release()
    cv2.destroyAllWindows()


def main():
    # ==== 示例参数配置 ====
    # 将下面的路径替换为你想要变形录屏视频
    # (如果没有可以先找个普通的视频测试一下效果)
    # 此处假设用户在 bilibili-goods-workspace 目录下有一个 input.mp4
    input_video = r"D:\py-workspace\my-fullstack-app\bilibili-goods-workspace\对标视频_trimmed.mp4"
    output_video = r"D:\py-workspace\my-fullstack-app\bilibili-goods-workspace\warped_output.mp4"

    # 如果需要测试，你可以修改这两个路径
    input_path = Path(input_video)

    # 简单拦截一下免得报错退出不好看
    if not input_path.exists():
         print(f"请在 main() 函数中指定一个存在的视频路径！ 当前路径：{input_video}")
         return

    apply_perspective_transform(
        input_path=str(input_path),
        output_path=output_video,
        # —— 核心参数解释 ——
        # tl_offset_x: 左上角水平偏移（负值=向左拉）
        # tl_offset_y: 左上角垂直偏移（负值=向上拉）
        # 例如 (-50, -80) 表示左上角向左移50像素、向上移80像素
        tl_offset_x=-200,
        tl_offset_y=-80,
    )

if __name__ == "__main__":
    main()
