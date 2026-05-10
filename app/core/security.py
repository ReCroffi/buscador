from time import monotonic

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = {}

    async def allow(self, key: str, limit: int, window: int) -> bool:
        now = monotonic()
        hits = [hit for hit in self._hits.get(key, []) if now - hit < window]
        if len(hits) >= limit:
            self._hits[key] = hits
            return False
        hits.append(now)
        self._hits[key] = hits
        return True


memory_limiter = InMemoryRateLimiter()


async def rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "anonymous"
    redis: Redis | None = getattr(request.app.state, "redis", None)
    limit = settings.rate_limit_per_minute
    if redis:
        redis_key = f"rate:{key}"
        count = await redis.incr(redis_key)
        if count == 1:
            await redis.expire(redis_key, 60)
        allowed = count <= limit
    else:
        allowed = await memory_limiter.allow(key, limit, 60)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit")

