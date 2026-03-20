"""
视频裁剪脚本
用法: python video_trim.py <视频路径> <开始时间> <结束时间>
时间格式: HH:MM:SS 或 MM:SS 或 纯秒数

示例:
  python video_trim.py video.mp4 00:01:30 00:02:45
  python video_trim.py video.mp4 1:30 2:45
  python video_trim.py video.mp4 90 165
"""

import sys
import subprocess
import shutil
from pathlib import Path


def check_ffmpeg():
    """检查 ffmpeg 是否可用"""
    if shutil.which("ffmpeg") is None:
        print("错误: 未找到 ffmpeg，请先安装 ffmpeg 并确保其在 PATH 中。")
        print("下载地址: https://ffmpeg.org/download.html")
        sys.exit(1)


def parse_time(time_str: str) -> str:
    """
    将各种时间格式统一转为 HH:MM:SS.xxx 格式（ffmpeg 可直接识别）。
    支持: HH:MM:SS / MM:SS / 纯秒数
    """
    parts = time_str.split(":")
    if len(parts) == 3:
        return time_str  # HH:MM:SS
    if len(parts) == 2:
        return f"00:{parts[0].zfill(2)}:{parts[1]}"  # MM:SS
    # 纯秒数
    try:
        float(time_str)
        return time_str
    except ValueError:
        print(f"错误: 无法解析时间 '{time_str}'，请使用 HH:MM:SS / MM:SS / 秒数 格式。")
        sys.exit(1)


def trim_video(video_path: str, start: str, end: str):
    """裁剪视频并保存到同目录下"""
    src = Path(video_path)
    if not src.is_file():
        print(f"错误: 文件不存在 -> {src}")
        sys.exit(1)

    start_fmt = parse_time(start)
    end_fmt = parse_time(end)

    out = src.with_name(f"{src.stem}_trimmed{src.suffix}")

    cmd = [
        "ffmpeg",
        "-i", str(src),
        "-ss", start_fmt,
        "-to", end_fmt,
        "-c", "copy",       # 直接复制流，速度极快且无损
        "-avoid_negative_ts", "make_zero",
        "-y",                # 覆盖已有文件
        str(out),
    ]

    print(f"输入: {src}")
    print(f"输出: {out}")
    print(f"时间: {start_fmt} -> {end_fmt}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print("ffmpeg 执行失败:")
        print(result.stderr)
        sys.exit(1)

    print(f"完成! 已保存到: {out}")


def main():
    # ===== 在这里修改参数 =====
    video_path = r"D:\py-workspace\my-fullstack-app\bilibili-goods-workspace\对标视频.mp4"  # 视频路径
    start_time = "00:00:00"  # 开始时间
    end_time = "00:01:00"    # 结束时间
    # ==========================

    check_ffmpeg()
    trim_video(video_path, start_time, end_time)


if __name__ == "__main__":
    main()
