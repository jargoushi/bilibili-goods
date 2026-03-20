"""
滚动黑色网格背景视频生成器
==============================

【方案说明】
    本脚本采用"无缝循环 + ffmpeg 拼接"方案来生成任意时长的滚动网格背景视频：

    1. 生成阶段（本脚本）:
       - 用 OpenCV 逐帧绘制网格，生成一段最短的"无缝循环"视频片段
       - 循环原理: 网格是重复图案，当画面向左滚动恰好 1 个格子宽度后，
         画面与初始帧完全一致，形成无缝衔接
       - 循环时长 = 格子宽度(px) ÷ 滚动速度(px/帧) ÷ 帧率(fps)
       - 例: 1920÷28≈68.57px 宽, 速度 1px/帧, 30fps → 69帧 ≈ 2.3秒

    2. 拼接阶段（ffmpeg 命令）:
       - 利用 ffmpeg 的 -stream_loop 参数，将循环片段无限拼接到目标时长
       - 命令示例: ffmpeg -stream_loop -1 -i grid_loop.mp4 -t 120 -c copy output.mp4
       - -stream_loop -1 = 无限循环输入
       - -t 120 = 输出 120 秒（2 分钟）
       - -c copy = 直接复制流，瞬间完成，无质量损失

    【优势】
    - 循环片段仅 2.3 秒，文件极小
    - 拼接到任意时长只需改 -t 参数，速度极快（毫秒级）
    - 一次生成，无限复用

依赖: pip install opencv-python

用法:
    步骤1 - 生成循环片段: python grid_video.py
    步骤2 - 拼接到目标时长: ffmpeg -stream_loop -1 -i grid_loop.mp4 -t 300 -c copy grid_5min.mp4
"""

import math
import subprocess
import shutil
import cv2
import numpy as np
from pathlib import Path


def generate_grid_loop(
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    grid_cols: int = 28,
    grid_rows: int = 15,
    bg_color: tuple = (26, 26, 26),        # 深灰背景 BGR #1a1a1a
    line_color: tuple = (50, 50, 50),       # 网格线颜色 BGR #323232
    line_thickness: int = 1,
    scroll_speed: float = 1.0,             # 每帧向左移动的像素数
):
    """
    生成最短的无缝循环网格背景视频片段。

    循环原理:
        网格是水平重复图案，向左滚动 1 个格子宽度后，画面回到初始状态。
        因此最短循环帧数 = ceil(格子宽度 / 滚动速度)

    参数:
        output_path:     输出视频路径
        width, height:   视频分辨率
        fps:             帧率
        grid_cols:       横向格子数（决定格子宽度 = width / grid_cols）
        grid_rows:       纵向格子数（决定格子高度 = height / grid_rows）
        bg_color:        背景色 (B, G, R)
        line_color:      网格线颜色 (B, G, R)
        line_thickness:  网格线粗细
        scroll_speed:    滚动速度（像素/帧，越大越快）
    """
    # ---- 计算网格尺寸和循环参数 ----
    grid_w = width / grid_cols                          # 每格宽度 (px)
    grid_h = height / grid_rows                         # 每格高度 (px)
    loop_frames = math.ceil(grid_w / scroll_speed)      # 最短无缝循环帧数
    loop_duration = loop_frames / fps                   # 循环时长 (秒)

    # ---- 初始化视频写入器 ----
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not writer.isOpened():
        print(f"错误: 无法创建视频文件 -> {output_path}")
        return

    # ---- 打印参数信息 ----
    print("=" * 50)
    print("  滚动网格背景 - 无缝循环片段生成器")
    print("=" * 50)
    print(f"  分辨率:     {width}x{height}")
    print(f"  网格:       {grid_cols}列 x {grid_rows}行")
    print(f"  单格尺寸:   {grid_w:.1f} x {grid_h:.1f} px")
    print(f"  帧率:       {fps} fps")
    print(f"  滚动速度:   {scroll_speed} px/帧")
    print(f"  循环帧数:   {loop_frames} 帧")
    print(f"  循环时长:   {loop_duration:.2f} 秒")
    print("=" * 50)
    print()

    # ---- 逐帧绘制 ----
    for i in range(loop_frames):
        # 创建纯色背景
        frame = np.full((height, width, 3), bg_color, dtype=np.uint8)

        # 计算当前帧水平偏移量（取模保证循环）
        offset_x = (i * scroll_speed) % grid_w

        # 绘制竖线（随偏移量滚动）
        x = -offset_x
        while x < width:
            px = int(round(x))
            if 0 <= px < width:
                cv2.line(frame, (px, 0), (px, height), line_color, line_thickness)
            x += grid_w

        # 绘制横线（静止不动）
        y = 0.0
        while y < height:
            py = int(round(y))
            if 0 <= py < height:
                cv2.line(frame, (0, py), (width, py), line_color, line_thickness)
            y += grid_h

        writer.write(frame)

        # 进度显示
        progress = (i + 1) / loop_frames * 100
        print(f"\r  生成中: {progress:.0f}% ({i + 1}/{loop_frames})", end="", flush=True)

    writer.release()
    print(f"\n\n✓ 循环片段已保存: {output_path}")
    return loop_duration


def extend_to_duration(loop_path: str, target_seconds: int, output_path: str):
    """
    使用 ffmpeg 将循环片段拼接到目标时长。

    原理:
        ffmpeg -stream_loop -1  → 无限循环输入视频
        -t {target_seconds}     → 截取指定时长
        -c copy                 → 直接复制流，零损耗、极速完成

    参数:
        loop_path:       循环片段路径
        target_seconds:  目标时长（秒）
        output_path:     输出视频路径
    """
    if shutil.which("ffmpeg") is None:
        print("错误: 未找到 ffmpeg，请手动执行以下命令:")
        print(f'  ffmpeg -stream_loop -1 -i "{loop_path}" -t {target_seconds} -c copy "{output_path}"')
        return

    cmd = [
        "ffmpeg",
        "-stream_loop", "-1",
        "-i", str(loop_path),
        "-t", str(target_seconds),
        "-c", "copy",
        "-y",
        str(output_path),
    ]

    print(f"\n  拼接中: {loop_path} → {target_seconds}秒 → {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    if result.returncode != 0:
        print(f"ffmpeg 失败:\n{result.stderr}")
        return

    print(f"✓ 已生成 {target_seconds}秒 背景视频: {output_path}")


def main():
    # ===========================
    #   参数配置区
    # ===========================

    # 输出目录（所有文件保存在这里）
    out_dir = Path(r"D:\py-workspace\my-fullstack-app\bilibili-goods-workspace")

    # 循环片段路径（中间产物，约2秒，文件很小）
    loop_path = str(out_dir / "grid_loop.mp4")

    # 第一步: 生成最短无缝循环片段
    generate_grid_loop(
        output_path=loop_path,
        width=1920,          # 视频宽度
        height=1080,         # 视频高度
        fps=30,              # 帧率
        grid_cols=28,        # 横向格子数
        grid_rows=15,        # 纵向格子数
        scroll_speed=1.0,    # 滚动速度（像素/帧）
    )

    # 第二步: 拼接到目标时长（按需修改秒数）
    target_seconds = 60      # 目标时长: 60秒
    output_path = str(out_dir / f"grid_bg_{target_seconds}s.mp4")
    extend_to_duration(loop_path, target_seconds, output_path)

    # ===========================
    #   如需其他时长，复制下面两行修改秒数即可:
    #   target_seconds = 300
    #   extend_to_duration(loop_path, target_seconds, str(out_dir / f"grid_bg_{target_seconds}s.mp4"))
    # ===========================


if __name__ == "__main__":
    main()
