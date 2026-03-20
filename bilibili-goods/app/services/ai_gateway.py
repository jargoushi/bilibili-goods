"""AI 网关（MVP版）。

说明：
- 当前实现先提供本地规则能力，确保流程可运行。
- 后续可在 TODO 位置接入 DeepSeek/豆包/元宝真实接口。
"""

from __future__ import annotations

import re


class AIGateway:
    """统一 AI 入口，避免业务模块直接绑定单一模型。"""

    def summarize_selling_points(self, text: str, max_points: int = 5) -> list[str]:
        """从文本中提取卖点句（规则版）。"""
        # 先按中文标点切句，再过滤过短句。
        candidates = [
            seg.strip()
            for seg in re.split(r"[。！？\n]", text)
            if len(seg.strip()) >= 8
        ]
        # 去重并截断数量。
        result: list[str] = []
        seen: set[str] = set()
        for sentence in candidates:
            if sentence in seen:
                continue
            seen.add(sentence)
            result.append(sentence)
            if len(result) >= max_points:
                break
        return result

    def classify_comment(self, text: str) -> str:
        """评论分类（规则版），后续可替换 LLM。"""
        text = text.strip()
        if any(k in text for k in ["推荐", "求", "买哪个", "哪个好"]):
            return "求推荐"
        if any(k in text for k in ["参数", "尺寸", "功率", "材质"]):
            return "问参数"
        if any(k in text for k in ["多少钱", "比价", "便宜", "贵"]):
            return "比价"
        if any(k in text for k in ["坏了", "售后", "退货", "保修"]):
            return "售后"
        return "闲聊"

    def make_reply_suggestion(self, question: str, knowledge: str = "") -> str:
        """生成运营回复建议（规则版模板）。"""
        # TODO: 接入真实大模型并添加风格模板/安全策略。
        knowledge_part = f"参考信息：{knowledge}\n" if knowledge else ""
        return (
            f"{knowledge_part}"
            f"建议回复：已收到你的问题「{question}」。"
            "我整理了适合你场景的选项，重点看预算、使用频率和空间限制。"
            "如果你告诉我预算区间，我可以给你更具体的推荐。"
        )


ai_gateway = AIGateway()
