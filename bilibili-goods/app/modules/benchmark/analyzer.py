"""对标差异分析（MVP 规则版）。"""

from __future__ import annotations


def analyze_difference(benchmark_script: str, my_points: list[str]) -> dict:
    """返回差异化建议。

    TODO: 后续接入 LLM 做更细粒度结构分析。
    """
    benchmark_lines = [line.strip() for line in benchmark_script.splitlines() if line.strip()]
    suggestions: list[str] = []
    if len(benchmark_lines) < 6:
        suggestions.append("对标脚本信息较少，建议补充更多样本再分析。")
    if len(my_points) < 3:
        suggestions.append("你的卖点数量偏少，建议补充“场景+人群+痛点”表达。")
    if not suggestions:
        suggestions.append("建议在开头 5 秒强化冲突感，并增加价格对比段落。")
    return {
        "benchmark_line_count": len(benchmark_lines),
        "my_point_count": len(my_points),
        "suggestions": suggestions,
    }
