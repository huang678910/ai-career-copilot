"""Snapshot tests for HTML resume generation — no database required.

These test that build_html_resume produces structurally correct HTML
compatible with xhtml2pdf's limited CSS engine.
"""
import pytest

from app.utils.document_gen import build_html_resume

# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_FULL = {
    "basic_info": {
        "name": "张三",
        "email": "zhang@test.com",
        "phone": "13800138000",
        "city": "北京",
    },
    "target_position": "资深 Python 工程师",
    "summary": "8年Python开发经验，擅长后端架构和分布式系统设计。",
    "work_experiences": [
        {
            "company": "字节跳动",
            "title": "高级后端工程师",
            "location": "北京",
            "start_date": "2020-03",
            "end_date": "",
            "description": "负责推荐系统核心服务开发和架构升级",
            "highlights": [
                "将系统 QPS 从 5k 提升至 50k",
                "主导了微服务拆分，服务数量从 3 增长到 12",
            ],
        },
    ],
    "projects": [
        {
            "name": "实时数仓平台",
            "role": "技术负责人",
            "start_date": "2022-01",
            "end_date": "2023-06",
            "description": "基于 Flink + Kafka 搭建实时数据处理平台",
            "tech_stack": ["Flink", "Kafka", "ClickHouse"],
            "highlights": [
                "日处理数据量超过 100 亿条",
                "查询延迟从分钟级降低到秒级",
            ],
        },
    ],
    "education": [
        {
            "school": "北京大学",
            "degree": "硕士",
            "major": "计算机科学与技术",
            "start_date": "2014-09",
            "end_date": "2017-07",
            "description": "研究方向：分布式系统",
        },
    ],
    "skills": [
        {"category": "后端", "name": "Python", "level": "精通"},
        {"category": "后端", "name": "Go", "level": "熟练"},
        {"category": "数据库", "name": "PostgreSQL", "level": "熟练"},
    ],
    "job_target": {
        "target_position": "技术经理/架构师",
        "industry": "互联网",
    },
}

MOCK_MINIMAL = {
    "basic_info": {
        "name": "李四",
        "email": "li@test.com",
    },
}

MOCK_WITH_CHAT = {
    "basic_info": {
        "name": "王五",
        "email": "wang@test.com",
        "phone": "13900139000",
        "city": "上海",
    },
    "chat_highlights": "建议突出项目结果而非过程\n用 STAR 法则重构工作经历描述\n强调团队协作能力",
    "work_experiences": [
        {
            "company": "阿里巴巴",
            "title": "后端开发",
            "start_date": "2019-01",
            "end_date": "2022-12",
        },
    ],
    "education": [
        {
            "school": "复旦大学",
            "degree": "本科",
            "major": "软件工程",
            "start_date": "2015-09",
            "end_date": "2019-06",
        },
    ],
    "skills": [
        {"category": "前端", "name": "React", "level": "熟练"},
    ],
}


# ── Structural tests ──────────────────────────────────────────────────────────

class TestBuildHtmlResume:

    def test_full_resume_contains_sections(self):
        """Full resume should contain all 5 section headings."""
        html = build_html_resume(MOCK_FULL)
        assert 'font-size:18pt' in html
        assert 'font-weight:bold' in html
        assert "bgcolor=\"#1a365d\"" in html or 'bgcolor="#1a365d"' in html
        assert "自我评价" in html
        assert "工作经历" in html
        assert "项目经历" in html
        assert "教育背景" in html
        assert "专业技能" in html

    def test_minimal_resume_works(self):
        """Even bare-minimum data should produce valid HTML."""
        html = build_html_resume(MOCK_MINIMAL)
        assert "个人简历" in html
        assert "李四" in html
        assert "li@test.com" in html

    def test_empty_data_does_not_crash(self):
        """Empty dict should produce a page without errors."""
        html = build_html_resume({})
        assert "个人简历" in html
        assert "</html>" in html

    def test_none_values_do_not_crash(self):
        """None values in nested fields should not raise."""
        html = build_html_resume({
            "basic_info": {"name": None, "email": None},
        })
        assert "个人简历" in html

    def test_all_templates_produce_valid_html(self):
        """All 4 templates must produce output without errors."""
        for template in ("professional", "modern", "classic", "compact"):
            html = build_html_resume(MOCK_FULL, template=template)
            assert "AI Career Copilot" in html
            assert "专业简历" in html
            assert "</html>" in html

    def test_company_end_date_fallback_to_now(self):
        """Empty end_date should display as 至今."""
        html = build_html_resume(MOCK_FULL)
        assert "至今" in html

    def test_escapes_html_injection(self):
        """User-provided fields should be HTML-escaped."""
        html = build_html_resume({
            "basic_info": {"name": "<script>alert('xss')</script>", "email": "a@b.com"},
        })
        assert "&lt;script&gt;" in html
        assert "<script>" not in html.split("个人简历")[1] if "个人简历" in html else True


# ── CSS compatibility tests (for xhtml2pdf) ───────────────────────────────────

class TestCssXhtml2pdfCompatibility:

    def test_no_flexbox_css(self):
        """xhtml2pdf does NOT support display:flex — must use <table>."""
        html = build_html_resume(MOCK_FULL)
        assert 'display: flex' not in html
        assert 'flex-shrink' not in html
        assert 'flex: 1' not in html

    def test_no_max_width_on_body(self):
        """max-width on body causes overflow on A4; must be removed."""
        html = build_html_resume(MOCK_FULL)
        assert 'max-width' not in html

    def test_word_break_present(self):
        """word-break: break-word is critical for preventing text overflow."""
        html = build_html_resume(MOCK_FULL)
        assert 'word-break:break-word' in html or 'word-break: break-word' in html

    def test_page_break_inside_not_needed(self):
        """Inline style approach doesn't use page-break-inside; items are rendered as p tags."""
        pass

    def test_top_row_is_table(self):
        """Header must use <table> for xhtml2pdf compatibility."""
        html = build_html_resume(MOCK_FULL)
        assert '<table width="100%"' in html
        assert '照片粘贴处' in html

    def test_no_white_space_pre_wrap(self):
        """white-space:pre-wrap is not supported by xhtml2pdf."""
        html = build_html_resume(MOCK_WITH_CHAT)
        assert 'white-space:pre-wrap' not in html

    def test_no_letter_spacing(self):
        """letter-spacing removed for xhtml2pdf compatibility."""
        html = build_html_resume(MOCK_FULL)
        assert 'letter-spacing' not in html


# ── Content correctness ───────────────────────────────────────────────────────

class TestContentCorrectness:

    def test_target_position_rendered(self):
        html = build_html_resume(MOCK_FULL)
        assert "资深 Python 工程师" in html

    def test_skills_grouped_by_category(self):
        html = build_html_resume(MOCK_FULL)
        assert "精通" in html
        assert "熟练" in html

    def test_chat_highlights_rendered(self):
        html = build_html_resume(MOCK_WITH_CHAT)
        assert "STAR" in html
        assert "亮点" in html

    def test_project_tech_stack_inline(self):
        html = build_html_resume(MOCK_FULL)
        assert "ClickHouse" in html

    def test_summary_before_experience(self):
        """Summary/自我评价 should appear before work experience."""
        html = build_html_resume(MOCK_FULL)
        summary_idx = html.index("自我评价")
        work_idx = html.index("工作经历")
        assert summary_idx < work_idx, "自我评价 should come before 工作经历"

    def test_footer_present(self):
        html = build_html_resume(MOCK_FULL)
        assert "AI Career Copilot" in html
