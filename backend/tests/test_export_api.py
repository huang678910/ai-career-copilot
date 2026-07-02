"""Integration tests for PDF/DOCX export endpoints."""
import pytest

RESUME_DATA = {
    "basic_info": {"name": "Test User", "email": "test@example.com", "phone": "13800000000", "city": "Shenzhen"},
    "target_position": "Senior Backend Engineer",
    "summary": "5 years of backend development experience.",
    "skills": [{"category": "Backend", "name": "Python", "level": "Expert"}],
    "education": [{"school": "Tsinghua", "degree": "Master", "major": "CS", "start_date": "2015-09-01", "end_date": "2018-07-01"}],
    "work_experiences": [{"company": "Tencent", "title": "Engineer", "start_date": "2019-03-01", "end_date": None, "description": "Backend dev"}],
}


class TestExportPDF:
    """Test PDF sync export endpoint."""

    PDF_MAGIC = b"%PDF-"

    @pytest.mark.asyncio
    async def test_export_pdf_success(self, client, auth_headers):
        """Export a resume with basic data should return a valid PDF."""
        create = await client.post("/api/v1/resumes", json={"title": "PDF Test", "target_position": "Engineer"}, headers=auth_headers)
        assert create.status_code == 201
        resume_id = create.json()["id"]

        export = await client.post(
            f"/api/v1/export/resume/{resume_id}/pdf/sync",
            json={"resume_data": RESUME_DATA, "template": "professional"},
            headers=auth_headers,
        )
        assert export.status_code == 200
        assert export.headers["content-type"] == "application/pdf"
        pdf = export.content
        assert len(pdf) >= 1000
        assert pdf[:5] == self.PDF_MAGIC

    @pytest.mark.asyncio
    async def test_export_pdf_all_templates(self, client, auth_headers):
        """All 4 templates should produce valid PDFs."""
        create = await client.post("/api/v1/resumes", json={"title": "Templates", "target_position": "Test"}, headers=auth_headers)
        assert create.status_code == 201
        resume_id = create.json()["id"]

        for template in ("professional", "modern", "classic", "compact"):
            export = await client.post(
                f"/api/v1/export/resume/{resume_id}/pdf/sync",
                json={"resume_data": RESUME_DATA, "template": template},
                headers=auth_headers,
            )
            assert export.status_code == 200
            pdf = export.content
            assert pdf[:5] == self.PDF_MAGIC

    @pytest.mark.asyncio
    async def test_export_with_chat(self, client, auth_headers):
        """Export with chat highlights."""
        create = await client.post("/api/v1/resumes", json={"title": "Chat", "target_position": "Test"}, headers=auth_headers)
        assert create.status_code == 201
        resume_id = create.json()["id"]

        data = {**RESUME_DATA, "chat_highlights": "Use STAR method\nQuantify results"}
        export = await client.post(
            f"/api/v1/export/resume/{resume_id}/pdf/sync",
            json={"resume_data": data, "template": "professional"},
            headers=auth_headers,
        )
        assert export.status_code == 200
        assert export.content[:5] == self.PDF_MAGIC

    @pytest.mark.asyncio
    async def test_export_no_auth(self, client):
        """Export without auth should return 401/403 (or 422 if body validation fails before auth)."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        export = await client.post(
            f"/api/v1/export/resume/{fake_id}/pdf/sync",
            json={"resume_data": {}, "template": "professional"},
        )
        assert export.status_code in (401, 403, 422)


class TestExportDOCX:
    """Test DOCX sync export endpoint."""

    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    @pytest.mark.asyncio
    async def test_export_docx_success(self, client, auth_headers):
        create = await client.post("/api/v1/resumes", json={"title": "DOCX", "target_position": "Test"}, headers=auth_headers)
        assert create.status_code == 201
        resume_id = create.json()["id"]

        export = await client.post(
            f"/api/v1/export/resume/{resume_id}/docx/sync",
            json={"resume_data": RESUME_DATA, "template": "classic"},
            headers=auth_headers,
        )
        assert export.status_code == 200
        assert export.headers["content-type"] == self.DOCX_MIME
        assert len(export.content) >= 1000
