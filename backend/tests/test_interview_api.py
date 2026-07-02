"""Integration tests for interview API endpoints — against live backend."""
import uuid

import httpx
import pytest


BASE_URL = "http://localhost:8004"


@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30)


@pytest.fixture
def auth(client):
    """Register test user, return auth token."""
    email = f"intv_{uuid.uuid4().hex[:6]}@test.com"
    r = client.post("/api/v1/auth/register", json={
        "email": email, "password": "test123456", "name": "InterviewTester",
    })
    if r.status_code != 201:
        pytest.skip(f"Register failed: {r.text}")
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "email": email}


@pytest.fixture
def resume(client, auth):
    """Create a test resume and return its ID."""
    r = client.post("/api/v1/resumes", json={"title": "Test Resume", "target_position": "Python Dev"},
                    headers=auth)
    assert r.status_code == 201
    return r.json()["id"]


def test_create_session_with_resume(client, auth, resume):
    """Create an interview session with a resume."""
    r = client.post("/api/v1/interview/sessions", json={
        "session_type": "technical",
        "questions_total": 5,
        "resume_id": resume,
    }, headers=auth)
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["session_type"] == "technical"
    assert data["questions_total"] == 5


def test_create_session_without_resume(client, auth):
    """Create an interview session without resume (should work)."""
    r = client.post("/api/v1/interview/sessions", json={
        "session_type": "hr",
        "questions_total": 3,
    }, headers=auth)
    assert r.status_code == 201
    assert r.json()["session_type"] == "hr"


def test_list_sessions(client, auth, resume):
    """List interview sessions for user."""
    # Create one first
    client.post("/api/v1/interview/sessions", json={
        "session_type": "technical", "questions_total": 3, "resume_id": resume,
    }, headers=auth)

    r = client.get("/api/v1/interview/sessions", headers=auth)
    assert r.status_code == 200
    sessions = r.json()
    assert isinstance(sessions, list)
    assert len(sessions) >= 1


def test_generate_questions(client, auth, resume):
    """Generate interview questions — may be slow, uses 120s timeout."""
    c = httpx.Client(base_url=BASE_URL, timeout=120, headers=auth)
    r = c.post("/api/v1/interview/questions/generate", json={
        "question_count": 3,
        "resume_id": resume,
    })
    assert r.status_code == 201, f"Generate failed: {r.text}"
    questions = r.json()
    assert isinstance(questions, list)
    assert len(questions) == 3
    for q in questions:
        assert "question" in q
        assert "question_type" in q


def test_delete_session(client, auth, resume):
    """Delete an interview session."""
    r = client.post("/api/v1/interview/sessions", json={
        "session_type": "technical", "questions_total": 3, "resume_id": resume,
    }, headers=auth)
    sid = r.json()["id"]

    r = client.delete(f"/api/v1/interview/sessions/{sid}", headers=auth)
    assert r.status_code in (200, 204)


def test_invalid_questions_count_rejected(client, auth):
    """Requesting 50 questions should be rejected (max 30)."""
    r = client.post("/api/v1/interview/questions/generate", json={
        "question_count": 50,
    }, headers=auth)
    assert r.status_code == 422
