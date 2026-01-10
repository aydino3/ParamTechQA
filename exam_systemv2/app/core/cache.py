from typing import Optional, Callable, Any
from functools import wraps
import hashlib
import json
import time
from datetime import timedelta

# Simple in-memory cache (can be replaced with Redis in production)
_cache: dict[str, tuple[Any, float]] = {}


def get_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_result(ttl_seconds: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time to live in seconds (default: 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{get_cache_key(*args, **kwargs)}"
            
            # Check cache
            if cache_key in _cache:
                result, expiry = _cache[cache_key]
                if time.time() < expiry:
                    return result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            _cache[cache_key] = (result, time.time() + ttl_seconds)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{get_cache_key(*args, **kwargs)}"
            
            # Check cache
            if cache_key in _cache:
                result, expiry = _cache[cache_key]
                if time.time() < expiry:
                    return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = (result, time.time() + ttl_seconds)
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def clear_cache(pattern: Optional[str] = None):
    """Clear cache entries matching pattern, or all if pattern is None."""
    if pattern is None:
        _cache.clear()
    else:
        keys_to_remove = [k for k in _cache.keys() if pattern in k]
        for key in keys_to_remove:
            del _cache[key]


def get_cache_stats() -> dict:
    """Get cache statistics."""
    now = time.time()
    valid_entries = sum(1 for _, expiry in _cache.values() if now < expiry)
    expired_entries = len(_cache) - valid_entries
    
    return {
        "total_entries": len(_cache),
        "valid_entries": valid_entries,
        "expired_entries": expired_entries
    }

