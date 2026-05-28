import json
import re

from app.ai.base import chat, chat_reasoner
from app.ai.prompts.jd_analysis import JD_ANALYSIS_SYSTEM, JD_ANALYSIS_USER


class JDAgent:
    def analyze(self, raw_text: str) -> dict:
        """Analyze a job description and return structured results."""
        user_prompt = JD_ANALYSIS_USER.format(raw_text=raw_text)
        messages = [
            {"role": "system", "content": JD_ANALYSIS_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

        response = chat(messages, temperature=0.3, max_tokens=4096)

        # Parse JSON from response
        try:
            # Try direct JSON parse first
            result = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if match:
                result = json.loads(match.group(1))
            else:
                # Try to find bare JSON object
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                else:
                    result = {"error": "Failed to parse AI response", "raw_response": response}

        # Run risk deep analysis with reasoner if risk score is high
        risk_score = result.get("risk_score", 0)
        if risk_score >= 3:
            risk_flags = result.get("risk_flags", [])
            if risk_flags:
                deep_analysis = self._deep_risk_analysis(raw_text, risk_flags)
                result["risk_flags"] = deep_analysis

        return result

    def _deep_risk_analysis(self, raw_text: str, initial_flags: list) -> list:
        """Use reasoner for deeper risk analysis."""
        prompt = f"""深度分析以下职位描述的风险信号。已知初步风险标记：{json.dumps(initial_flags, ensure_ascii=False)}

JD文本：
{raw_text[:2000]}

请逐一分析每个风险信号的真实性，给出0-10的置信度评分和详细理由。
输出JSON格式：[{"type": "风险类型", "signal": "信号描述", "severity": "high/medium/low", "confidence": 0-10, "reason": "分析理由"}]"""
        try:
            response = chat_reasoner([{"role": "user", "content": prompt}])
            # Try to parse the reasoner's structured response
            try:
                parsed = json.loads(response)
                return parsed if isinstance(parsed, list) else initial_flags
            except json.JSONDecodeError:
                match = re.search(r'\[.*\]', response, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(0))
                    except json.JSONDecodeError:
                        pass
                return initial_flags
        except Exception:
            return initial_flags
