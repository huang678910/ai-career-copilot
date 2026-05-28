import json
import re
from collections.abc import Generator

from app.ai.base import chat, chat_stream
from app.ai.prompts.interview import (
    INTERVIEW_FEEDBACK_SYSTEM,
    INTERVIEW_QUESTION_GENERATOR,
    MOCK_INTERVIEW_SYSTEM,
)


def _build_dynamic_fallback(count: int, jd_data: dict | None = None, resume_data: dict | None = None) -> list[dict]:
    """Generate varied fallback questions matching the requested count (module-level helper)."""
    templates = [
        ("technical", "请做自我介绍，重点突出技术背景和核心优势", "easy"),
        ("technical", "请描述一个你最有挑战性的技术项目，以及你的解决方案", "medium"),
        ("behavioral", "你未来的职业规划是什么？未来3-5年希望达到什么目标？", "easy"),
        ("technical", "在你使用的技术栈中，最擅长的是什么？为什么？", "medium"),
        ("project_deep_dive", "请详细说明你最近项目中遇到的一个技术难点及解决方案", "hard"),
        ("technical", "如何进行代码质量控制和Code Review？", "medium"),
        ("behavioral", "描述一次你与团队成员产生分歧的经历，以及如何解决的", "medium"),
        ("fundamental", "请解释常用数据结构（如HashMap、ArrayList）的实现原理", "medium"),
        ("technical", "你如何保证系统的高可用性和性能优化？", "hard"),
        ("behavioral", "为什么想加入我们公司？", "easy"),
        ("fundamental", "请解释HTTP/HTTPS协议的区别及工作原理", "easy"),
        ("technical", "你如何进行技术选型？评估一个新技术时会考虑哪些因素？", "medium"),
        ("project_deep_dive", "描述你的项目中数据库设计的关键决策", "hard"),
        ("behavioral", "你的优点和缺点分别是什么？", "easy"),
        ("technical", "请描述你对微服务/系统架构设计的理解", "hard"),
    ]
    result = []
    for i in range(count):
        t = templates[i % len(templates)]
        result.append({"type": t[0], "category": "综合", "question": t[1], "difficulty": t[2]})
    return result


class InterviewAgent:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def generate_questions(
        self,
        jd_data: dict | None = None,
        resume_data: dict | None = None,
        question_count: int = 10,
    ) -> list[dict]:
        """Generate interview questions based on JD and resume."""
        context = ""
        if jd_data:
            context += f"\n## 职位描述分析\n{json.dumps(jd_data, ensure_ascii=False, indent=2)}"
        if resume_data:
            context += f"\n## 候选人简历\n{json.dumps(resume_data, ensure_ascii=False, indent=2)}"

        if not context:
            context = "无特定JD或简历信息，请生成通用技术面试题。"

        prompt = INTERVIEW_QUESTION_GENERATOR.format(question_count=question_count) + context

        try:
            response = chat([{"role": "user", "content": prompt}], temperature=0.8, max_tokens=8192, max_retries=2)

            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
                if match:
                    result = json.loads(match.group(1))
                else:
                    match = re.search(r'\[.*\]', response, re.DOTALL)
                    if match:
                        result = json.loads(match.group(0))
                    else:
                        raise ValueError("No JSON array found in AI response")

            if isinstance(result, list) and len(result) > 0:
                if len(result) < question_count:
                    print(f"[InterviewAgent] AI returned {len(result)} questions, requested {question_count}")
                return result[:question_count] if len(result) >= question_count else result

        except Exception as e:
            print(f"[InterviewAgent] Failed to generate via API: {e}, using dynamic fallback for {question_count} questions")

        return _build_dynamic_fallback(question_count, jd_data, resume_data)

    def start_session(self, session_id: str, session_type: str = "technical", questions_total: int = 10, resume_data: dict | None = None) -> None:
        system_prompt = MOCK_INTERVIEW_SYSTEM.format(interview_type=session_type, questions_total=questions_total)
        if resume_data:
            import json
            resume_context = f"\n\n## 候选人简历信息\n{json.dumps(resume_data, ensure_ascii=False, indent=2)}\n\n请根据以上简历内容生成个性化面试问题，紧密结合候选人的实际项目经历、技术栈和工作经验进行提问。"
            system_prompt += resume_context
        self._sessions[session_id] = {
            "type": session_type,
            "questions_total": questions_total,
            "history": [{"role": "system", "content": system_prompt}],
            "questions_asked": 0,
            "scores": [],
        }

    def chat_stream(self, session_id: str, user_message: str | None = None) -> Generator[str, None, None]:
        """Stream an interview response. If user_message is None, ask first question."""
        sess = self._sessions.get(session_id)
        if not sess:
            yield "Error: Session not found"
            return

        if user_message:
            sess["history"].append({"role": "user", "content": user_message})
        else:
            sess["history"].append({"role": "user", "content": "请开始面试，提出第一个问题。"})

        full_response = ""
        for chunk in chat_stream(sess["history"], temperature=0.8, max_tokens=2048):
            full_response += chunk
            yield chunk

        sess["history"].append({"role": "assistant", "content": full_response})

        # Trim history: keep system prompt + last 20 messages
        if len(sess["history"]) > 21:
            sess["history"] = [sess["history"][0]] + sess["history"][-20:]

    def generate_feedback(self, session_id: str) -> dict:
        """Generate comprehensive feedback for a completed session."""
        sess = self._sessions.get(session_id)
        if not sess:
            return {"error": "Session not found"}

        feedback_prompt = f"""请为以下面试会话生成反馈报告。

面试类型：{sess['type']}
提问数量：{sess['questions_asked']}

面试记录：
{json.dumps(sess['history'][1:], ensure_ascii=False, indent=2)}

请按JSON格式输出反馈报告。"""

        messages = [
            {"role": "system", "content": INTERVIEW_FEEDBACK_SYSTEM},
            {"role": "user", "content": feedback_prompt},
        ]
        response = chat(messages, temperature=0.4, max_tokens=4096)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_feedback": response}

    def get_questions_asked(self, session_id: str) -> int:
        sess = self._sessions.get(session_id)
        return sess["questions_asked"] if sess else 0

    def end_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
