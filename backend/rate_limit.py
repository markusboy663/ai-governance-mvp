"""
Rate limiting for API endpoints.

For MVP: in-memory token bucket
For production: use Redis or place behind Cloudflare/Vercel edge
"""

from time import time
from typing import Dict, Tuple
from fastapi import HTTPException

# In-memory rate limit state: {api_key_id: (request_count, window_start_time)}
_rate_limit_state: Dict[str, Tuple[int, int]] = {}

# Default limits
DEFAULT_LIMIT = 100  # requests per window
DEFAULT_WINDOW = 60  # seconds


def get_rate_limit_key(api_key_id: str) -> str:
    """Generate rate limit key from API key ID"""
    return f"rl:{api_key_id}"


def allow_request(
    api_key_id: str,
    limit: int = DEFAULT_LIMIT,
    window: int = DEFAULT_WINDOW
) -> bool:
    """
    Check if request is allowed under rate limit.
    
    Uses token bucket algorithm:
    - Each key gets `limit` tokens per `window` seconds
    - Once window expires, bucket refills
    
    Args:
        api_key_id: The API key ID
        limit: Max requests per window (default: 100)
        window: Time window in seconds (default: 60)
    
    Returns:
        True if request is allowed, False if rate limited
    """
    key = get_rate_limit_key(api_key_id)
    now = int(time())
    
    if key not in _rate_limit_state:
        # First request for this key
        _rate_limit_state[key] = (1, now)
        return True
    
    count, window_start = _rate_limit_state[key]
    elapsed = now - window_start
    
    # Window expired - reset bucket
    if elapsed >= window:
        _rate_limit_state[key] = (1, now)
        return True
    
    # Still in window
    if count < limit:
        _rate_limit_state[key] = (count + 1, window_start)
        return True
    
    # Rate limited
    return False


def check_rate_limit(
    api_key_id: str,
    limit: int = DEFAULT_LIMIT,
    window: int = DEFAULT_WINDOW
) -> None:
    """
    Check rate limit and raise HTTPException if exceeded.
    
    Use this in endpoints:
        @app.post("/v1/check")
        async def check(body: CheckRequest, api_key = Depends(api_key_dependency)):
            check_rate_limit(api_key.id)
            ...
    
    Args:
        api_key_id: The API key ID
        limit: Max requests per window
        window: Time window in seconds
    
    Raises:
        HTTPException: 429 Too Many Requests if rate limited
    """
    if not allow_request(api_key_id, limit, window):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} requests per {window} seconds"
        )


def cleanup_old_buckets(max_age: int = 3600) -> None:
    """
    Clean up old rate limit buckets to prevent memory leak.
    
    Call periodically (e.g., in a background task).
    
    Args:
        max_age: Remove buckets older than this many seconds (default: 1 hour)
    """
    now = int(time())
    expired_keys = [
        key for key, (_, start) in _rate_limit_state.items()
        if now - start > max_age
    ]
    for key in expired_keys:
        del _rate_limit_state[key]


# For testing/debugging
def reset_rate_limits() -> None:
    """Reset all rate limit buckets (for testing)"""
    global _rate_limit_state
    _rate_limit_state = {}


def get_rate_limit_status(api_key_id: str) -> dict:
    """
    Get current rate limit status for debugging.
    
    Returns:
        Dict with current count, window start, and seconds remaining
    """
    key = get_rate_limit_key(api_key_id)
    if key not in _rate_limit_state:
        return {"count": 0, "window_start": None, "seconds_remaining": 0}
    
    count, window_start = _rate_limit_state[key]
    now = int(time())
    remaining = max(0, DEFAULT_WINDOW - (now - window_start))
    
    return {
        "count": count,
        "window_start": window_start,
        "seconds_remaining": remaining,
        "limit": DEFAULT_LIMIT
    }
