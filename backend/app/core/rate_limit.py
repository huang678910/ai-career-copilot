"""Pure ASGI rate limiter — avoids BaseHTTPMiddleware which conflicts with asyncpg."""
import os
import time
from collections import defaultdict

from starlette.responses import JSONResponse

from app.core.config import settings

# Skip rate limiting in test environment
_skip_rate_limit = os.environ.get("APP_ENV") == "test"

# Fallback in-memory store when Redis is unavailable
_in_memory: dict[str, list[float]] = defaultdict(list)
_token_usage: dict[str, dict[str, int]] = defaultdict(lambda: {"tokens": 0, "calls": 0})

# Rate limit config: (max_requests, window_seconds)
RATE_LIMITS: dict[str, tuple[int, int]] = {
    "/api/v1/interview/questions/generate": (5, 60),
    "/api/v1/resumes/import": (5, 60),
    "/api/v1/tailor": (5, 10),
    "/api/v1/jd-analysis": (5, 5),
    "/api/v1/auth/login": (10, 60),
    "/api/v1/auth/register": (10, 60),
}

DEFAULT_RATE = (20, 60)  # 20 requests per 60 seconds
DAILY_TOKEN_LIMIT = 100_000

_redis_client = None


async def _get_redis_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await _redis_client.ping()
    except Exception:
        _redis_client = False
    return _redis_client if _redis_client is not False else None


async def _redis_check(key: str, max_req: int, window: int) -> bool:
    r = await _get_redis_client()
    if r is None:
        return _memory_check(key, max_req, window)
    try:
        now = time.time()
        cutoff = now - window
        async with r.pipeline() as pipe:
            pipe.zremrangebyscore(key, 0, cutoff)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window * 2)
            _, _, count, _ = await pipe.execute()
        return count <= max_req
    except Exception:
        return _memory_check(key, max_req, window)


def _memory_check(key: str, max_req: int, window: int) -> bool:
    now = time.time()
    cutoff = now - window
    _in_memory[key] = [t for t in _in_memory[key] if t > cutoff]
    _in_memory[key].append(now)
    return len(_in_memory[key]) <= max_req


def _extract_user_id(scope: dict) -> str:
    """Extract user ID from ASGI scope headers without importing FastAPI tools."""
    headers = dict(scope.get("headers", []))
    auth = headers.get(b"authorization", b"").decode("latin-1", errors="ignore")
    if auth.startswith("Bearer "):
        try:
            from app.core.security import decode_token
            payload = decode_token(auth.split(" ", 1)[1])
            return payload.get("sub", "anon")
        except Exception:
            pass
    return "anon"


async def _send_429(send) -> None:
    """Send a 429 Too Many Requests response."""
    body = '{"detail":"请求过于频繁，请稍后再试","error":{"code":"RATE_LIMITED","message":"Too many requests"}}'.encode("utf-8")
    await send({
        "type": "http.response.start",
        "status": 429,
        "headers": [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(body)).encode()),
        ],
    })
    await send({"type": "http.response.body", "body": body})


class RateLimitMiddleware:
    """Pure ASGI middleware — no BaseHTTPMiddleware threading issues with asyncpg."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or _skip_rate_limit:
            await self.app(scope, receive, send)
            return

        try:
            path = scope.get("path", "").rstrip("/")
            user_id = _extract_user_id(scope)
            max_req, window = RATE_LIMITS.get(path, DEFAULT_RATE)
            key = f"ratelimit:{user_id}:{path}"

            ok = await _redis_check(key, max_req, window)
            if not ok:
                await _send_429(send)
                return
        except Exception:
            pass  # Rate limiter failure should never block requests

        await self.app(scope, receive, send)


def track_token_usage(user_id: str, tokens: int):
    """Record AI token consumption for a user (in-memory, best-effort)."""
    import datetime
    today = datetime.date.today().isoformat()
    key = f"tokens:{user_id}:{today}"
    _token_usage[key]["tokens"] += tokens
    _token_usage[key]["calls"] += 1


def check_token_limit(user_id: str) -> bool:
    """Check if user has exceeded daily token limit (in-memory)."""
    import datetime
    today = datetime.date.today().isoformat()
    key = f"tokens:{user_id}:{today}"
    return _token_usage.get(key, {}).get("tokens", 0) < DAILY_TOKEN_LIMIT
