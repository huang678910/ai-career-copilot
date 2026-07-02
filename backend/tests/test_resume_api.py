"""Integration tests for Resume CRUD API endpoints."""
import uuid as uid
import pytest


class TestResumeCRUD:
    """Test resume creation, retrieval, update, and deletion."""

    @pytest.mark.asyncio
    async def test_create_resume(self, client, auth_headers):
        """Create a resume should return 201 with valid fields."""
        resp = await client.post(
            "/api/v1/resumes",
            json={"title": "My Resume", "target_position": "Python Engineer"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "My Resume"
        assert data["target_position"] == "Python Engineer"
        assert "id" in data
        assert data["language"] == "zh"

    @pytest.mark.asyncio
    async def test_list_resumes(self, client, auth_headers):
        """Listing resumes should return a list."""
        await client.post("/api/v1/resumes", json={"title": "R1", "target_position": "P1"}, headers=auth_headers)
        await client.post("/api/v1/resumes", json={"title": "R2", "target_position": "P2"}, headers=auth_headers)

        resp = await client.get("/api/v1/resumes", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    @pytest.mark.asyncio
    async def test_get_resume(self, client, auth_headers):
        """Get a single resume by ID."""
        create = await client.post(
            "/api/v1/resumes",
            json={"title": "Get Test", "target_position": "Test"},
            headers=auth_headers,
        )
        resume_id = create.json()["id"]

        resp = await client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Get Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_id(self, client, auth_headers):
        """Get a resume with a non-existent UUID should return 404."""
        resp = await client.get(
            f"/api/v1/resumes/{uid.uuid4()}",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_resume(self, client, auth_headers):
        """Update a resume's fields."""
        create = await client.post(
            "/api/v1/resumes",
            json={"title": "Original", "target_position": "Old"},
            headers=auth_headers,
        )
        resume_id = create.json()["id"]

        resp = await client.put(
            f"/api/v1/resumes/{resume_id}",
            json={"title": "Updated", "target_position": "New"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"
        assert resp.json()["target_position"] == "New"

    @pytest.mark.asyncio
    async def test_delete_resume(self, client, auth_headers):
        """Delete a resume should succeed."""
        create = await client.post(
            "/api/v1/resumes",
            json={"title": "Delete Me", "target_position": "Delete"},
            headers=auth_headers,
        )
        resume_id = create.json()["id"]

        resp = await client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
        assert resp.status_code in (200, 204)

        get_resp = await client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_cannot_access_other_user_resume(self, client, auth_headers):
        """User A should not access User B's resume."""
        create = await client.post(
            "/api/v1/resumes",
            json={"title": "Secret", "target_position": "Private"},
            headers=auth_headers,
        )
        resume_id = create.json()["id"]

        reg = await client.post("/api/v1/auth/register", json={
            "email": f"other_{uid.uuid4().hex[:8]}@test.com",
            "password": "test123456", "name": "Other User",
        })
        assert reg.status_code == 201
        diff_token = reg.json()["access_token"]
        diff_headers = {"Authorization": f"Bearer {diff_token}"}

        resp = await client.get(f"/api/v1/resumes/{resume_id}", headers=diff_headers)
        assert resp.status_code == 404


class TestResumeEducation:
    """Test education sub-resource CRUD."""

    @pytest.mark.asyncio
    async def test_add_education(self, client, auth_headers):
        create = await client.post(
            "/api/v1/resumes",
            json={"title": "Edu Test", "target_position": "Test"},
            headers=auth_headers,
        )
        resume_id = create.json()["id"]

        resp = await client.post(
            f"/api/v1/resumes/{resume_id}/education",
            json={
                "school": "Peking University", "degree": "Bachelor",
                "major": "CS", "start_date": "2014-09-01", "end_date": "2018-07-01",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["school"] == "Peking University"
        assert data["major"] == "CS"
