import json
import logging
from collections.abc import Generator

from app.ai.base import chat, chat_stream
from app.ai.prompts.resume_guided import GUIDED_RESUME_SYSTEM, RESUME_SUMMARY_PROMPT
from app.ai.prompts.resume import STAR_GENERATION_PROMPT, PROJECT_HIGHLIGHT_PROMPT

_log = logging.getLogger("resume_agent")

ORDERED_SECTIONS = ["basic_info", "job_target", "education", "skills", "projects", "work_experience"]
LIST_SECTIONS = {"education", "skills", "projects", "work_experience"}

RESUME_COACH_SYSTEM = """你是一位资深的职业规划师和简历专家。

请自然地与用户对话，帮助他完善简历。对话中自然地覆盖以下方面：
- 基本信息（姓名、邮箱、电话、城市）
- 求职意向（目标职位、行业、城市、薪资）
- 教育背景（学校、学位、专业、时间）
- 专业技能（按类别整理，标注熟练度）
- 项目经历（STAR 格式，量化成果）
- 工作/实习经历（STAR 格式，量化成果）

规则：
1. 自然地引导对话，一次聚焦 1-2 个方面
2. 主动追问细节和量化成果，将模糊描述转化为 STAR 格式
3. 用户在对话中提及的任何信息都会被自动提取并更新到简历预览面板中
4. 如果用户已有简历数据，请先确认并询问需要改进的地方
5. 保持对话自然流畅，不要输出 JSON"""


class GuidedResumeAgent:
    """Stateless resume builder. After each user message, the AI extracts
    the COMPLETE resume state (all 6 sections) from the full conversation
    history. No section tracking, no state machine — the data is the state."""

    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def start_session(self, session_id: str, collected_data: dict | None = None) -> str:
        """Initialize a guided resume session. Returns the AI's first message."""
        data = dict(collected_data or {})
        data.pop("_meta", None)

        self._sessions[session_id] = {
            "history": [{"role": "system", "content": RESUME_COACH_SYSTEM}],
            "collected_data": data,
        }

        if collected_data and len(collected_data) > 0:
            import json as _json
            data_summary = _json.dumps(data, ensure_ascii=False, indent=2)
            prompt = (
                "用户已有以下简历数据：\n" + data_summary + "\n\n"
                "请简短告知用户：我已看到您的简历内容（提及1-2个具体亮点，"
                "如目标职位、某项技能或项目名称），并询问是否需要继续完善或做出什么改进？"
                "直接向用户提问，不要输出JSON。"
            )
        else:
            prompt = "请向用户打招呼，介绍自己是 AI 简历助手，可以帮他创建一份专业的简历。引导用户开始从基本信息（姓名、邮箱、电话、城市）填写。直接向用户提问，不要输出JSON。"

        self._sessions[session_id]["history"].append({"role": "user", "content": prompt})
        return chat(
            [{"role": "system", "content": RESUME_COACH_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=1024,
        )

    def init_silent(self, session_id: str, collected_data: dict | None = None,
                    history_msgs: list | None = None) -> None:
        """Initialize session silently — no AI call. For resuming without auto-response."""
        data = dict(collected_data or {})
        data.pop("_meta", None)

        self._sessions[session_id] = {
            "history": [{"role": "system", "content": RESUME_COACH_SYSTEM}],
            "collected_data": data,
        }

        if history_msgs:
            sess = self._sessions[session_id]
            for m in history_msgs:
                role = m.role if hasattr(m, 'role') else m.get('role', 'user')
                content = m.content if hasattr(m, 'content') else m.get('content', '')
                if role == "ai":
                    role = "assistant"
                sess["history"].append({"role": role, "content": content})
            if len(sess["history"]) > 41:
                sess["history"] = [sess["history"][0]] + sess["history"][-40:]

    def chat_stream(self, session_id: str, user_message: str) -> Generator[str, None, None]:
        """Process user input. Yields AI response chunks.

        Phase 1: AI conversation (streamed to user).
        Phase 2: AI extracts the COMPLETE resume state (all 6 sections)
                 from the full conversation history + current data.
                 Replaces collected_data entirely."""
        sess = self._sessions.get(session_id)
        if not sess:
            yield "Error: Session not found. Please refresh the page."
            return

        # --- Phase 1: Conversation (streamed to user) ---
        sess["history"].append({"role": "user", "content": user_message})

        full_response = ""
        for chunk in chat_stream(sess["history"], temperature=0.7, max_tokens=8192):
            full_response += chunk
            yield chunk

        sess["history"].append({"role": "assistant", "content": full_response})

        # Trim history
        if len(sess["history"]) > 25:
            sess["history"] = [sess["history"][0]] + sess["history"][-24:]

        # --- Phase 2: Extract COMPLETE resume state ---
        try:
            extraction_prompt = self._build_extraction_prompt(
                sess["history"], sess["collected_data"]
            )
            json_response = chat(
                [{"role": "system", "content": "You are a JSON extraction assistant. Always output valid JSON objects."},
                 {"role": "user", "content": extraction_prompt}],
                temperature=0.1,
                max_tokens=4096,
                max_retries=1,
                response_format={"type": "json_object"},
            )
            if json_response:
                _log.info("Phase 2 raw (first 300 chars): %s", json_response[:300])
                parsed = self._parse_single_json(json_response)
                if not parsed:
                    import re as _re
                    cleaned = _re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_response.strip())
                    parsed = self._parse_single_json(cleaned)
                if parsed:
                    parsed.pop("_meta", None)
                    # Preserve existing summary — Phase 2 extraction template
                    # doesn't include "summary", so it would be lost on replace
                    existing_summary = sess["collected_data"].get("summary")
                    sess["collected_data"] = parsed
                    if existing_summary and not parsed.get("summary"):
                        sess["collected_data"]["summary"] = existing_summary
                    _log.info("Phase 2 replaced collected_data, keys: %s", list(parsed.keys()))
                else:
                    _log.warning("Phase 2 parse FAILED")
            else:
                _log.warning("Phase 2 extraction returned EMPTY")
        except Exception:
            _log.exception("Phase 2 extraction crashed")

    def get_progress(self, session_id: str) -> dict:
        """Derive progress purely from collected_data. No state machine."""
        sess = self._sessions.get(session_id)
        if not sess:
            return {"completed": [], "collected_data": {}}

        collected = sess.get("collected_data", {})
        completed = []
        for sec in ORDERED_SECTIONS:
            data = collected.get(sec)
            if not data:
                continue
            if sec in LIST_SECTIONS:
                if isinstance(data, list) and len(data) > 0:
                    completed.append(sec)
            elif isinstance(data, dict) and any(v for v in data.values() if v):
                completed.append(sec)

        return {
            "completed": completed,
            "collected_data": collected,
        }

    def build_summary(self, session_id: str) -> str:
        """Generate a professional summary from collected data."""
        sess = self._sessions.get(session_id)
        if not sess:
            return ""
        data = sess["collected_data"]

        skills_list = data.get("skills", [])
        skill_names = []
        for s in (skills_list if isinstance(skills_list, list) else []):
            if isinstance(s, dict):
                skill_names.append(s.get("name", ""))

        work_list = data.get("work_experience", [])
        work_descs = []
        for w in (work_list if isinstance(work_list, list) else []):
            if isinstance(w, dict):
                work_descs.append(f"{w.get('title','')}@{w.get('company','')}: {w.get('description','')[:80]}")

        proj_list = data.get("projects", [])
        proj_descs = []
        for p in (proj_list if isinstance(proj_list, list) else []):
            if isinstance(p, dict):
                proj_descs.append(f"{p.get('name','')}: {p.get('description','')[:80]}")

        edu_list = data.get("education", [])
        edu_descs = []
        for e in (edu_list if isinstance(edu_list, list) else []):
            if isinstance(e, dict):
                edu_descs.append(f"{e.get('school','')} {e.get('degree','')} {e.get('major','')}")

        target = data.get("job_target", {})
        target_pos = target.get("target_position", "") if isinstance(target, dict) else ""

        prompt = RESUME_SUMMARY_PROMPT.format(
            target_position=target_pos,
            skills=", ".join(skill_names[:15]),
            work_summary="; ".join(work_descs),
            project_summary="; ".join(proj_descs),
            education_summary="; ".join(edu_descs),
        )
        summary = chat([{"role": "user", "content": prompt}], temperature=0.5, max_tokens=1024)
        if summary:
            sess["collected_data"]["summary"] = summary
        return summary

    def get_collected_data(self, session_id: str) -> dict:
        sess = self._sessions.get(session_id)
        if not sess:
            return {}
        data = dict(sess["collected_data"])
        data.pop("_meta", None)
        return data

    def reset_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def generate_star(self, raw_description: str) -> str:
        prompt = STAR_GENERATION_PROMPT.format(raw_description=raw_description)
        return chat([{"role": "user", "content": prompt}])

    def extract_highlights(self, project_name: str, project_description: str) -> str:
        prompt = PROJECT_HIGHLIGHT_PROMPT.format(
            project_name=project_name, project_description=project_description
        )
        return chat([{"role": "user", "content": prompt}])

    # ── Private helpers ──────────────────────────────────────────────

    @staticmethod
    def _parse_single_json(text: str) -> dict | None:
        """Parse a json_object mode response. Handles bare JSON, code fences,
        and leading/trailing noise."""
        import json as _json
        text = text.strip()
        if text and ord(text[0]) == 0xFEFF:
            text = text[1:]
        if text.startswith("```"):
            lines = text.split("\n")
            if len(lines) >= 3:
                text = "\n".join(lines[1:-1]).strip()
            else:
                text = text[3:].strip()
                if text.endswith("```"):
                    text = text[:-3].strip()
        brace_start = text.find("{")
        if brace_start == -1:
            return None
        brace_end = text.rfind("}")
        if brace_end == -1 or brace_end <= brace_start:
            return None
        text = text[brace_start:brace_end + 1]
        try:
            return _json.loads(text)
        except _json.JSONDecodeError:
            return None

    @staticmethod
    def _build_extraction_prompt(history: list[dict], current_data: dict) -> str:
        """Build a prompt that asks the AI to extract the COMPLETE resume state
        (all 6 sections) from the full conversation history."""
        import json as _json

        # Build conversation context
        conv_lines = []
        for m in history[1:]:  # skip system prompt
            role = m.get("role", "user")
            if role not in ("user", "assistant"):
                continue
            label = "User" if role == "user" else "Assistant"
            conv_lines.append(label + ": " + m["content"][:500])
        context = "\n".join(conv_lines)

        # Show current data so AI can copy unchanged fields
        data_display = _json.dumps(current_data, ensure_ascii=False, indent=2)

        return (
            "Current complete resume data:\n"
            + data_display + "\n"
            "\n"
            "Conversation:\n"
            + context + "\n"
            "\n"
            "Output the COMPLETE updated resume as a single JSON object with ALL 6 sections:\n"
            '{\n'
            '  "basic_info": {"name": "", "email": "", "phone": "", "city": ""},\n'
            '  "job_target": {"target_position": "", "industry": "", "city": "", "salary": ""},\n'
            '  "education": [{"school": "", "degree": "", "major": "", "start_date": "", "end_date": "", "gpa": "", "description": ""}],\n'
            '  "skills": [{"category": "", "name": "", "level": ""}],\n'
            '  "projects": [{"name": "", "role": "", "start_date": "", "end_date": "", "description": "", "tech_stack": [], "highlights": []}],\n'
            '  "work_experience": [{"company": "", "title": "", "location": "", "start_date": "", "end_date": "", "description": "", "highlights": []}]\n'
            '}\n'
            "\n"
            "CRITICAL RULES:\n"
            "1. Start from the CURRENT data shown above. For each field:\n"
            "   - If the user just mentioned/changed it → use the new value\n"
            "   - If the user did NOT mention it → COPY the existing value unchanged\n"
            "2. For list sections (education, skills, projects, work_experience):\n"
            "   include ALL items — existing items PLUS any new items discussed.\n"
            "3. ONLY fill in data the user explicitly provided. NEVER invent or guess.\n"
            "4. Empty strings '' and empty arrays [] are valid. Use [] for empty list sections.\n"
            "\n"
            "Only output the JSON object, no other text."
        )
