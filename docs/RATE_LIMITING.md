# Rate Limiting

This document describes the rate limiting strategy for AI Governance MVP.

## Overview

Rate limiting protects the API from abuse and ensures fair resource allocation.

**MVP Implementation:** In-memory token bucket (simple, no external dependencies)
**Production:** Place behind Cloudflare/Vercel edge or use Redis

## Current Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/v1/check` | 100 | 60 seconds |
| `/api/evaluate` | 100 | 60 seconds |
| `/health` | Unlimited | - |

**Per API key** - Each customer key gets its own bucket.

## How It Works

Token bucket algorithm:

1. Each API key gets `limit` tokens per `window` seconds
2. Each request costs 1 token
3. When bucket empty → 429 Too Many Requests
4. Window resets after `window` seconds

### Example

```
API key: api_abc123
Limit: 100 requests per 60 seconds

Time 0s:  1st request  → 99 tokens left
Time 1s:  2nd request  → 98 tokens left
...
Time 59s: 100th request → 0 tokens left
Time 60s: 101st request → Request succeeds (window reset)
```

## Configuration

### Default Limits (in `rate_limit.py`)

```python
DEFAULT_LIMIT = 100      # max requests per window
DEFAULT_WINDOW = 60      # seconds
```

### Custom Limits Per Endpoint

```python
# In main.py
@app.post("/v1/check")
async def check(body: CheckRequest, api_key = Depends(api_key_dependency)):
    # Custom: 50 requests per 30 seconds
    check_rate_limit(api_key.id, limit=50, window=30)
    ...
```

## Error Response

When rate limited:

```bash
curl -X POST http://localhost:8000/v1/check \
  -H "Authorization: Bearer api_key"

# After 100 requests in 60 seconds:
HTTP/1.1 429 Too Many Requests
{"detail":"Rate limit exceeded: 100 requests per 60 seconds"}
```

## Production Deployment

### Option 1: Cloudflare (Recommended)

Cloudflare's edge rate limiting is faster and scales automatically.

1. Add to Cloudflare dashboard:
   - **Rate limiting rule:** 100 requests per 60 seconds per IP/key
   - **Action:** Challenge or Block

2. Benefits:
   - Rate limits at edge (no backend load)
   - DDoS protection included
   - Scales globally

### Option 2: Redis

For self-hosted deployments:

```python
# Install: pip install redis
import redis
client = redis.Redis()

def allow_request_redis(key_id, limit=100, window=60):
    key = f"rl:{key_id}"
    count = client.incr(key)
    if count == 1:
        client.expire(key, window)
    return count <= limit
```

### Option 3: Keep In-Memory

Current MVP approach works for ~100 RPS. For higher throughput, migrate to Redis.

## Monitoring

### Check Rate Limit Status

```python
from rate_limit import get_rate_limit_status

status = get_rate_limit_status("api_key_id")
print(status)
# {
#     "count": 45,
#     "window_start": 1700134800,
#     "seconds_remaining": 30,
#     "limit": 100
# }
```

### Memory Usage

In-memory buckets use ~100 bytes per API key.

**Max memory (100k customers):** ~10MB

For higher scale, use Redis.

## Cleanup

Old buckets are kept for 1 hour. Manual cleanup:

```python
from rate_limit import cleanup_old_buckets

# Remove buckets older than 1 hour
cleanup_old_buckets(max_age=3600)
```

## Testing

Reset rate limits in tests:

```python
from rate_limit import reset_rate_limits

@pytest.fixture
def reset_limits():
    reset_rate_limits()
    yield
    reset_rate_limits()
```

## Future Improvements

1. **Redis backend** - For distributed systems
2. **Per-user tiers** - Different limits for different customers
3. **Graduated backoff** - Exponential delay instead of hard block
4. **Analytics** - Track rate limit violations over time
