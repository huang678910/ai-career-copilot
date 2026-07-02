"""Integration tests for Auth endpoints."""
import uuid as uid
import pytest


class TestAuth:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_and_login(self, client):
        """Register a user, then login with correct credentials."""
        email = f"auth_{uid.uuid4().hex[:8]}@test.com"

        reg = await client.post("/api/v1/auth/register", json={
            "email": email, "password": "SecurePass123!", "name": "Auth Test",
        })
        assert reg.status_code == 201
        assert "access_token" in reg.json()

        login = await client.post("/api/v1/auth/login", json={
            "email": email, "password": "SecurePass123!",
        })
        assert login.status_code == 200
        assert "access_token" in login.json()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """Registering with the same email twice should return 409."""
        email = f"dup_{uid.uuid4().hex[:8]}@test.com"

        await client.post("/api/v1/auth/register", json={
            "email": email, "password": "test123456", "name": "First",
        })
        resp = await client.post("/api/v1/auth/register", json={
            "email": email, "password": "test123456", "name": "Second",
        })
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        """Login with wrong password should return 401."""
        email = f"fail_{uid.uuid4().hex[:8]}@test.com"

        await client.post("/api/v1/auth/register", json={
            "email": email, "password": "correct", "name": "Fail Test",
        })
        resp = await client.post("/api/v1/auth/login", json={
            "email": email, "password": "wrong",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token(self, client):
        """Refresh token endpoint with a valid refresh token should return new tokens."""
        import uuid as uid
        email = f"refresh_{uid.uuid4().hex[:8]}@test.com"
        reg = await client.post("/api/v1/auth/register", json={
            "email": email, "password": "TestPass123!", "name": "Refresh Tester",
        })
        assert reg.status_code == 201
        refresh_token = reg.json().get("refresh_token")
        assert refresh_token, "Registration response missing refresh_token"

        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200, f"Refresh failed: {resp.text}"
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_get_me(self, client, auth_headers):
        """Get current user info."""
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "email" in data
