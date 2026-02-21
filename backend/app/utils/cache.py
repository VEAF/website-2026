from functools import wraps

from cachetools import TTLCache

# Shared in-memory caches (single worker uvicorn)
teamspeak_cache = TTLCache(maxsize=100, ttl=1200)  # 20 min
dcsbot_cache = TTLCache(maxsize=100, ttl=120)  # 2 min


def cached(cache: TTLCache):
    """Decorator for async functions with TTL caching."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            if key in cache:
                return cache[key]
            result = await func(*args, **kwargs)
            cache[key] = result
            return result

        wrapper.cache = cache
        return wrapper

    return decorator
