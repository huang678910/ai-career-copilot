"""Unit tests for AI output JSON parsing. Verifies _parse_single_json handles various formats."""
import json

import pytest

from app.ai.resume_agent import GuidedResumeAgent


class TestParseSingleJSON:
    """Verify _parse_single_json handles the json_object mode response formats."""

    def test_valid_bare_json(self):
        text = '{"type": "resume_update", "section": "basic_info", "data": {"name": "张三", "email": "z@test.com"}}'
        result = GuidedResumeAgent._parse_single_json(text)
        assert result is not None
        assert result["type"] == "resume_update"
        assert result["section"] == "basic_info"
        assert result["data"]["name"] == "张三"

    def test_json_with_code_fence(self):
        text = """好的，以下是你的信息：
```json
{"type": "resume_update", "section": "skills", "data": [{"name": "Python", "level": "精通"}]}
```
"""
        result = GuidedResumeAgent._parse_single_json(text)
        assert result is not None
        assert result["section"] == "skills"
        assert len(result["data"]) == 1

    def test_json_without_language_tag(self):
        text = """```
{"type": "resume_update", "section": "education", "data": []}
```"""
        result = GuidedResumeAgent._parse_single_json(text)
        assert result is not None
        assert result["type"] == "resume_update"

    def test_plain_text_returns_none(self):
        result = GuidedResumeAgent._parse_single_json("这是一段没有JSON的纯文本回复。")
        assert result is None

    def test_resume_ready(self):
        text = '{"type": "resume_ready", "summary": "Experienced Python developer with 5+ years."}'
        result = GuidedResumeAgent._parse_single_json(text)
        assert result is not None
        assert result["type"] == "resume_ready"
        assert "Python" in result["summary"]

    def test_invalid_json_returns_none(self):
        result = GuidedResumeAgent._parse_single_json('{"broken": json')
        assert result is None

    def test_nested_objects(self):
        text = '{"type": "resume_update", "section": "projects", "data": [{"name": "ProjA", "tech_stack": ["Python", "React"]}]}'
        result = GuidedResumeAgent._parse_single_json(text)
        assert result is not None
        assert len(result["data"]) == 1
        assert result["data"][0]["tech_stack"] == ["Python", "React"]

    def test_empty_string_returns_none(self):
        assert GuidedResumeAgent._parse_single_json("") is None
        assert GuidedResumeAgent._parse_single_json("   ") is None


class TestJSONEndToEnd:
    """Simulate the full Phase 2 extraction flow."""

    def test_merge_preserves_previous_data(self):
        """When AI returns JSON for a new section, old sections are preserved."""
        # Simulate session state after basic_info was collected
        existing = {
            "basic_info": {"name": "张三", "email": "z@test.com"},
            "job_target": {"target_position": "工程师"},
        }

        # AI now returns skills data (not basic_info)
        ai_response = """```json
{"type": "resume_update", "section": "skills", "data": [{"name": "Python", "level": "精通"}]}
```"""

        # Parse the response
        parsed = GuidedResumeAgent._parse_single_json(ai_response)
        assert parsed is not None

        # Defensive merge (the correct behavior):
        merged = dict(existing)
        section = parsed.get("section", "")
        new_value = parsed.get("data", None)
        if new_value is not None:
            merged[section] = new_value

        # Existing data preserved
        assert "basic_info" in merged
        assert merged["basic_info"]["name"] == "张三"
        assert "job_target" in merged
        assert merged["job_target"]["target_position"] == "工程师"
        # New section added
        assert "skills" in merged
        assert merged["skills"][0]["name"] == "Python"

    def test_merge_overwrites_existing_section(self):
        """When AI returns data for an already-existing section, it updates it."""
        existing = {"basic_info": {"name": "张三"}}
        ai = """```json
{"type": "resume_update", "section": "basic_info", "data": {"name": "李四", "email": "lisi@test.com"}}
```"""
        parsed = GuidedResumeAgent._parse_single_json(ai)
        merged = dict(existing)
        section = parsed.get("section", "")
        new_value = parsed.get("data", None)
        if new_value is not None:
            merged[section] = new_value

        # Updated data replaces old
        assert merged["basic_info"]["name"] == "李四"
        assert merged["basic_info"]["email"] == "lisi@test.com"
