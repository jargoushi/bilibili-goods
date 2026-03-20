"""OCR 参数抽取（MVP：正则版占位）。"""

from __future__ import annotations

import re


def extract_params_from_text(raw_text: str) -> dict[str, str]:
    """从文本中提取简单参数。

    说明：
    - 当前先做规则抽取，适配“参数名: 参数值”场景。
    - TODO: 后续接入 PaddleOCR + 表格结构化。
    """
    params: dict[str, str] = {}
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([\u4e00-\u9fa5A-Za-z0-9_ -]{1,20})[:：]\s*(.+)$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            params[key] = val
    return params
