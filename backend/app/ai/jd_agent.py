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
        result = self._parse_json(response)

        return result

    def _parse_json(self, text: str) -> dict:
        """Robust JSON extraction — balanced brackets, fixes common AI errors."""
        import re as re_mod
        text = re_mod.sub(r'```(?:json)?\s*', '', text)
        text = re_mod.sub(r'```\s*', '', text)
        start = text.find('{')
        if start == -1:
            return {"error": "No JSON object found", "raw_response": text}
        depth, end = 0, start
        for i in range(start, len(text)):
            if text[i] == '{': depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        # Fix common AI JSON errors
        json_str = re_mod.sub(r',\s*}', '}', json_str)
        json_str = re_mod.sub(r',\s*]', ']', json_str)
        json_str = re_mod.sub(r'"\s*\n\s*"', '",\n"', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response", "raw_response": text}

    def _parse_json_array(self, text: str) -> list:
        """Robust JSON array extraction."""
        import re as re_mod
        text = re_mod.sub(r'```(?:json)?\s*', '', text)
        text = re_mod.sub(r'```\s*', '', text)
        start = text.find('[')
        if start == -1:
            return []
        depth, end = 0, start
        for i in range(start, len(text)):
            if text[i] == '[': depth += 1
            elif text[i] == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        json_str = re_mod.sub(r',\s*}', '}', json_str)
        json_str = re_mod.sub(r',\s*]', ']', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return []
