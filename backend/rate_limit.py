"""
Rate limiting for API endpoints with Redis support.

Strategy:
- Primary: Redis token bucket (distributed, multi-instance)
- Fallback: In-memory token bucket (if REDIS_URL not set)
- Uses Lua script for atomic operations (Redis)
- Simple dict for in-memory (single-instance)

Configuration:
- REDIS_URL: redis://localhost:6379 (optional)
- If not set: uses in-memory (warning logged)
"""

import os
import asyncio
from time import time
from typing import Dict, Tuple, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", None)
DEFAULT_LIMIT = 100  # requests per window
DEFAULT_WINDOW = 60  # seconds

# Redis client (initialized lazily)
_redis_client = None
_redis_available = False

# In-memory fallback state
_rate_limit_state: Dict[str, Tuple[int, int]] = {}

# Lua script for atomic Redis rate limiting (token bucket)
# Returns: [remaining_tokens, reset_at_timestamp]
RATE_LIMIT_LUA = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local current = redis.call('GET', key)
if current == false then
    -- First request: set count=1, expiry=window
    redis.call('SET', key, '1', 'EX', window)
    return {limit - 1, now + window}
end

local count, reset_at
if string.find(current, ':') then
    -- Format: count:reset_at
    local parts = {}
    for part in string.gmatch(current, "[^:]+") do
        table.insert(parts, part)
    end
    count = tonumber(parts[1])
    reset_at = tonumber(parts[2])
else
    -- Legacy format: just count
    count = tonumber(current)
    reset_at = now + window
end

if now >= reset_at then
    -- Window expired: reset
    redis.call('SET', key, '1', 'EX', window)
    return {limit - 1, now + window}
elseif count < limit then
    -- Still have tokens: increment
    redis.call('SET', key, count + 1 .. ':' .. reset_at, 'EX', window)
    return {limit - (count + 1), reset_at}
else
    -- Rate limited
    return {0, reset_at}
end
"""


async def _init_redis():
    """Initialize Redis client (async)"""
    global _redis_client, _redis_available
    
    if not REDIS_URL:
        logger.warning("⚠️  REDIS_URL not set - using in-memory rate limiting (single instance only)")
        _redis_available = False
        return
    
    try:
        import aioredis
        _redis_client = await aioredis.from_url(REDIS_URL, decode_responses=True)
        # Test connection
        await _redis_client.ping()
        _redis_available = True
        logger.info("✅ Redis rate limiting initialized")
    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e} - falling back to in-memory")
        _redis_available = False


async def get_redis():
    """Get Redis client (initialize if needed)"""
    global _redis_client
    if _redis_client is None:
        await _init_redis()
    return _redis_client


def get_rate_limit_key(api_key_id: str) -> str:
    """Generate rate limit key from API key ID"""
    return f"rl:{api_key_id}"


async def allow_request(
    api_key_id: str,
    limit: int = DEFAULT_LIMIT,
    window: int = DEFAULT_WINDOW
) -> Tuple[bool, Dict]:
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
        Tuple of (allowed: bool, info: dict)
        info contains: remaining_tokens, reset_at_timestamp
    """
    key = get_rate_limit_key(api_key_id)
    now = int(time())
    
    if _redis_available:
        # Use Redis
        try:
            redis = await get_redis()
            if redis:
                # Execute Lua script atomically
                result = await redis.eval(
                    RATE_LIMIT_LUA,
                    1,  # number of keys
                    key,  # key
                    limit,  # argv[1]
                    window,  # argv[2]
                    now  # argv[3]
                )
                remaining, reset_at = result
                allowed = remaining >= 0
                return allowed, {
                    "remaining": max(0, remaining),
                    "reset_at": reset_at,
                    "backend": "redis"
                }
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e} - falling back to in-memory")
    
    # In-memory fallback
    if key not in _rate_limit_state:
        _rate_limit_state[key] = (1, now)
        return True, {
            "remaining": limit - 1,
            "reset_at": now + window,
            "backend": "memory"
        }
    
    count, window_start = _rate_limit_state[key]
    elapsed = now - window_start
    
    # Window expired - reset bucket
    if elapsed >= window:
        _rate_limit_state[key] = (1, now)
        return True, {
            "remaining": limit - 1,
            "reset_at": now + window,
            "backend": "memory"
        }
    
    # Still in window
    if count < limit:
        _rate_limit_state[key] = (count + 1, window_start)
        return True, {
            "remaining": limit - (count + 1),
            "reset_at": window_start + window,
            "backend": "memory"
        }
    
    # Rate limited
    return False, {
        "remaining": 0,
        "reset_at": window_start + window,
        "backend": "memory"
    }


async def check_rate_limit(
    api_key_id: str,
    limit: int = DEFAULT_LIMIT,
    window: int = DEFAULT_WINDOW
) -> None:
    """
    Check rate limit and raise HTTPException if exceeded.
    
    Use this in endpoints:
        @app.post("/v1/check")
        async def check(body: CheckRequest, api_key = Depends(api_key_dependency)):
            await check_rate_limit(api_key.id)
            ...
    
    Args:
        api_key_id: The API key ID
        limit: Max requests per window
        window: Time window in seconds
    
    Raises:
        HTTPException: 429 Too Many Requests if rate limited
    """
    allowed, info = await allow_request(api_key_id, limit, window)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} requests per {window} seconds",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset_at"]),
                "X-RateLimit-Backend": info["backend"]
            }
        )


async def cleanup_old_buckets(max_age: int = 3600) -> None:
    """
    Clean up old rate limit buckets to prevent memory leak.
    
    Call periodically (e.g., in a background task).
    Redis handles expiry automatically via SET EX.
    
    Args:
        max_age: Remove buckets older than this many seconds (default: 1 hour)
    """
    if _redis_available:
        # Redis handles cleanup via TTL
        return
    
    # In-memory cleanup
    now = int(time())
    expired_keys = [
        key for key, (_, start) in _rate_limit_state.items()
        if now - start > max_age
    ]
    for key in expired_keys:
        del _rate_limit_state[key]


def reset_rate_limits() -> None:
    """Reset all rate limit buckets (for testing)"""
    global _rate_limit_state
    _rate_limit_state = {}


async def get_rate_limit_status(api_key_id: str) -> dict:
    """
    Get current rate limit status for debugging.
    
    Returns:
        Dict with current count, window start, and seconds remaining
    """
    key = get_rate_limit_key(api_key_id)
    now = int(time())
    
    if _redis_available:
        try:
            redis = await get_redis()
            if redis:
                val = await redis.get(key)
                if not val:
                    return {
                        "count": 0,
                        "reset_at": None,
                        "seconds_remaining": 0,
                        "limit": DEFAULT_LIMIT,
                        "backend": "redis"
                    }
                # Try to parse new format: count:reset_at
                if ':' in val:
                    count, reset_at = val.split(':')
                    count = int(count)
                    reset_at = int(reset_at)
                else:
                    count = int(val)
                    reset_at = now + DEFAULT_WINDOW
                
                remaining = max(0, reset_at - now)
                return {
                    "count": count,
                    "reset_at": reset_at,
                    "seconds_remaining": remaining,
                    "limit": DEFAULT_LIMIT,
                    "backend": "redis"
                }
        except Exception as e:
            logger.warning(f"Failed to get Redis status: {e}")
    
    # In-memory status
    if key not in _rate_limit_state:
        return {
            "count": 0,
            "reset_at": None,
            "seconds_remaining": 0,
            "limit": DEFAULT_LIMIT,
            "backend": "memory"
        }
    
    count, window_start = _rate_limit_state[key]
    remaining = max(0, DEFAULT_WINDOW - (now - window_start))
    
    return {
        "count": count,
        "reset_at": window_start + DEFAULT_WINDOW,
        "seconds_remaining": remaining,
        "limit": DEFAULT_LIMIT,
        "backend": "memory"
    }
