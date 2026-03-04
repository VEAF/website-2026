import time
from functools import wraps

from cachetools import TTLCache

# Shared in-memory caches (single worker uvicorn)
teamspeak_cache = TTLCache(maxsize=100, ttl=1200)  # 20 min
dcsbot_cache = TTLCache(maxsize=100, ttl=120)  # 2 min
discord_oauth_states = TTLCache(maxsize=1000, ttl=300)  # 5 min


def cached(cache: TTLCache):
    """Decorator for async functions with TTL caching."""

    def decorator(func):
        timestamps: dict[str, float] = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            if key in cache:
                return cache[key]
            result = await func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = time.monotonic()
            return result

        def invalidate_if_older(min_age: float):
            """Remove all cached entries older than min_age seconds."""
            now = time.monotonic()
            keys_to_remove = [k for k, ts in timestamps.items() if now - ts >= min_age]
            for k in keys_to_remove:
                cache.pop(k, None)
                timestamps.pop(k, None)

        wrapper.cache = cache
        wrapper.invalidate_if_older = invalidate_if_older
        return wrapper

    return decorator
