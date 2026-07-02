"""Integration tests against live running backend."""
import uuid

import httpx
import pytest


BASE_URL = "http://localhost:8004"


@pytest.fixture
def client_sync():
    return httpx.Client(base_url=BASE_URL, timeout=30)


@pytest.fixture
def fresh_user(client_sync):
    """Create a unique test user, return (email, password, token)."""
    email = f"livetest_{uuid.uuid4().hex[:8]}@test.com"
    password = "test123456"
    resp = client_sync.post("/api/v1/auth/register", json={
        "email": email, "password": password, "name": "LiveTest",
    })
    if resp.status_code != 201:
        pytest.skip(f"Cannot register: {resp.status_code} {resp.text}")
    token = resp.json()["access_token"]
    return email, password, token


# ---------- Auth Tests ----------

def test_register_ok(client_sync):
    resp = client_sync.post("/api/v1/auth/register", json={
        "email": f"live_{uuid.uuid4().hex[:6]}@test.com",
        "password": "test123456", "name": "Tester",
    })
    assert resp.status_code == 201
    assert "access_token" in resp.json()


def test_login_ok(fresh_user):
    email, password, _ = fresh_user
    client = httpx.Client(base_url=BASE_URL, timeout=30)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(fresh_user):
    email, _, _ = fresh_user
    client = httpx.Client(base_url=BASE_URL, timeout=30)
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_unauthorized(client_sync):
    resp = client_sync.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403, 422)


# ---------- Rate Limit Tests ----------

def test_rate_limit_login_triggers(client_sync):
    """11 rapid logins should trigger 429 on request 11."""
    statuses = []
    for _ in range(11):
        r = client_sync.post("/api/v1/auth/login", json={
            "email": "nonexist@test.com", "password": "wrong",
        })
        statuses.append(r.status_code)
    # First 10 should be auth errors (401), 11th should be rate limited (429)
    assert statuses[:10].count(401) >= 8  # allow some variance
    assert 429 in statuses, f"No 429 found in {statuses}"


# ---------- Resume Tests ----------

def test_create_resume(fresh_user):
    _, _, token = fresh_user
    client = httpx.Client(base_url=BASE_URL, timeout=30, headers={"Authorization": f"Bearer {token}"})
    resp = client.post("/api/v1/resumes", json={
        "title": "Test Resume", "target_position": "Python Dev",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Resume"


def test_list_resumes(fresh_user):
    _, _, token = fresh_user
    client = httpx.Client(base_url=BASE_URL, timeout=30, headers={"Authorization": f"Bearer {token}"})
    resp = client.get("/api/v1/resumes")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
