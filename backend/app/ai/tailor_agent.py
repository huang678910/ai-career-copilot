import json
import re

from app.ai.base import chat, chat_reasoner
from app.ai.prompts.tailor import TAILOR_SYSTEM


class TailorAgent:
    def tailor(self, resume_data: dict, jd_analysis: dict) -> dict:
        """Tailor a resume based on JD analysis results."""
        user_prompt = f"""请根据以下JD分析结果，优化候选人的简历。

## JD分析结果
{json.dumps(jd_analysis, ensure_ascii=False, indent=2)}

## 候选人简历
{json.dumps(resume_data, ensure_ascii=False, indent=2)}

请输出上述JSON格式的优化结果。"""

        messages = [
            {"role": "system", "content": TAILOR_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

        response = chat(messages, temperature=0.5, max_tokens=8192)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if match:
                result = json.loads(match.group(1))
            else:
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                else:
                    result = {"error": "Failed to parse AI response", "raw_response": response}

        return result

    def analyze_skill_gaps(self, resume_data: dict, jd_analysis: dict) -> dict:
        """Deep analysis of skill gaps using reasoner."""
        prompt = f"""深度分析以下候选人与职位要求的技能差距。

JD要求的技术栈：{json.dumps(jd_analysis.get('tech_stack', {}), ensure_ascii=False)}
候选人技能：{json.dumps(resume_data.get('skills', []), ensure_ascii=False)}
候选人项目经验：{json.dumps(resume_data.get('projects', []), ensure_ascii=False)}

请分析：
1. 完全匹配的技能（候选人有且JD要求）
2. 部分匹配的技能（候选人有相关经验但不是完全相同）
3. 缺失的关键技能（JD要求但候选人没有）
4. 对每个缺失技能，评估其对面试的影响程度（致命/重要/加分项）
5. 给出具体的学习建议（时间估算、学习资源方向）"""

        try:
            response = chat_reasoner([{"role": "user", "content": prompt}])
            return {"analysis": response}
        except Exception as e:
            return {"analysis": f"Analysis failed: {str(e)}"}
