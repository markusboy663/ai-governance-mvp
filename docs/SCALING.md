# Scaling & Performance Optimization Guide

This document outlines optimization strategies for scaling the AI Governance MVP beyond initial deployment.

## 1. API Key Format Optimization (Key-ID Pattern)

### Current Implementation (MVP-1)
- **Format**: `api_<random_string>`
- **Lookup**: Full table scan on every request (loops through all APIKey rows)
- **Performance**: O(n) - acceptable for <1000 customers, ~10ms per request

### Planned Optimization (MVP-2)
- **Format**: `<key-id>.<raw-secret>`
  - Example: `123e4567-89ab-cdef-0123-456789abcdef.uM2x7jK9vL2qWpZ4mN8sT1xH5dF6gY3`
  - Structure:
    - `key-id`: UUID (primary key of APIKey row) - enables direct DB lookup
    - `raw-secret`: Random 32+ character string - securely hashed and stored

### Migration Path

**Step 1: Update generate_api_key.py**
```python
# Current
raw_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
api_key_hash = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt())
# Store only hash

# Optimized
key_id = str(uuid.uuid4())  # APIKey.id
raw_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
api_key_hash = bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt())
# Return: f"{key_id}.{raw_key}"  # Give to customer once
# Store: APIKey(id=key_id, api_key_hash=api_key_hash, ...)
```

**Step 2: Update auth.py**
```python
# Current (O(n) scan)
async def verify_api_key(api_key_str: str, session: AsyncSession):
    result = await session.execute(
        select(APIKey).where(APIKey.is_active == True)
    )
    for api_key in result.scalars():
        if bcrypt.checkpw(api_key_str.encode(), api_key.api_key_hash.encode()):
            return api_key
    return None

# Optimized (O(1) lookup + comparison)
async def verify_api_key(api_key_str: str, session: AsyncSession):
    key_id, raw_secret = api_key_str.split('.', 1)
    api_key = await session.get(APIKey, key_id)
    if api_key and api_key.is_active and bcrypt.checkpw(
        raw_secret.encode(), api_key.api_key_hash.encode()
    ):
        return api_key
    return None
```

### Performance Impact

| Metric | Current (MVP-1) | Optimized (MVP-2) |
|--------|-----------------|-------------------|
| Lookup Time | O(n) ~10ms (1000 keys) | O(1) <1ms |
| DB Queries | Full table scan | Single row fetch by PK |
| Index Used | None (full scan) | PRIMARY KEY (automatic) |
| Scales To | ~1000 keys/100ms | 100k+ keys/1ms |

### Implementation Priority
- **Not urgent**: Current MVP handles <100 concurrent requests adequately
- **Schedule**: Implement when approaching 1000+ active API keys or >100 RPS
- **Breaking change**: Existing keys become invalid; generate new keys during migration

---

## 2. Rate Limiting at Scale (Distributed Redis)

### Current Implementation (MVP-1)
- **Method**: In-memory token bucket (Python dict)
- **Location**: Single process
- **Limitation**: Doesn't work with multiple backend instances

### Planned Optimization (MVP-2+)

**Redis-based Rate Limiting**
```python
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379")

async def allow_request(api_key_id: str, limit: int = 100, window: int = 60):
    key = f"rate_limit:{api_key_id}"
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    results = await pipe.execute()
    count = results[0]
    return count <= limit
```

**Benefits**:
- Distributed across multiple backend instances
- Survives process restarts
- Shared rate limit state across load balancer

### When to Migrate
- Initial deployment: Single instance → Use in-memory MVP
- Multi-instance setup: Use Redis (Upstash, AWS ElastiCache, self-hosted)

---

## 3. Audit Logging at Scale

### Current Implementation (MVP-1)
- **Storage**: PostgreSQL table (`UsageLog`)
- **Write pattern**: Synchronous `session.add()` in request handler
- **Risk**: High write contention under heavy load

### Planned Optimization (MVP-2+)

**Option A: Async Queue (Recommended)**
```python
# Use Celery + RabbitMQ or simple Redis queue

# In main.py endpoint
async def log_audit(event: Dict):
    await audit_queue.put(event)  # Non-blocking

# Separate worker process
async def audit_worker():
    while True:
        event = await audit_queue.get()
        await session.execute(
            insert(UsageLog).values(**event)
        )
```

**Option B: Write to Kafka/EventHub**
- Purpose: Decouple governance logic from logging
- Benefits: Failover tolerant, replay-able, analytics-ready

### Recommendations
1. **Phase 1 (Now)**: DB writes in-request (current)
2. **Phase 2 (Scale)**: Queue-based writes (decoupled)
3. **Phase 3 (Enterprise)**: Event streaming (Kafka/Kinesis)

---

## 4. Policy Engine Scaling

### Current Implementation (MVP-1)
- **Strategy**: Load from `CustomerPolicy` table per request
- **Lookup**: Customer ID + Policy evaluation
- **Caching**: None

### Planned Optimization (MVP-2+)

**In-Memory Policy Cache with TTL**
```python
from functools import lru_cache
import asyncio

_policy_cache = {}  # {customer_id: (policies, timestamp)}
POLICY_CACHE_TTL = 300  # 5 minutes

async def get_customer_policies(customer_id: str, session: AsyncSession):
    now = time.time()
    if customer_id in _policy_cache:
        policies, cached_at = _policy_cache[customer_id]
        if now - cached_at < POLICY_CACHE_TTL:
            return policies
    
    # Cache miss - fetch from DB
    result = await session.execute(
        select(CustomerPolicy).where(
            CustomerPolicy.customer_id == customer_id
        )
    )
    policies = result.scalars().all()
    _policy_cache[customer_id] = (policies, now)
    return policies
```

**Benefits**:
- 99% cache hit rate (assuming 5 min stability)
- Eliminates DB queries for repeated customers
- Graceful degradation (stale policies acceptable)

---

## 5. Infrastructure Scaling Recommendations

### Single Instance (Current)
```
┌─────────────────┐
│  FastAPI (1)    │
│  SQLModel ORM   │
│  PostgreSQL ←──┬┘
│                 │
└─────────────────┘
```
- Works for: <100 RPS, <1000 customers
- Cost: ~$10-20/mo (small backend + managed DB)

### Multi-Instance (MVP-2)
```
┌──────────────────────┐
│  Load Balancer       │
├──────────┬───────────┤
│FastAPI 1 │ FastAPI 2 │
├──────────┴───────────┤
│  Shared Redis        │  (Rate Limiting)
│  PostgreSQL (pooled) │  (Data)
└──────────────────────┘
```
- Works for: <1000 RPS, 10k+ customers
- Components:
  - `FastAPI instances`: 2-4 replicas behind load balancer
  - `Redis`: Shared rate limiting state (Upstash, ElastiCache)
  - `PostgreSQL`: Connection pooling (PgBouncer, Supabase)
- Cost: ~$50-100/mo

### Enterprise Scale (MVP-3+)
```
┌────────────────────────────────┐
│  CDN + Cloudflare Rate Limit   │
├────────────────────────────────┤
│  Kubernetes cluster (auto-scale)│
│  ├─ FastAPI pods               │
│  ├─ Celery workers (logging)   │
│  └─ Redis cluster              │
├────────────────────────────────┤
│  PostgreSQL replicas + Pgpool2 │
│  Kafka (audit trail)           │
│  ElasticSearch (analytics)     │
└────────────────────────────────┘
```
- Works for: >5000 RPS, 100k+ customers
- Cost: ~$500-2000/mo

---

## 6. Database Optimization Roadmap

### Current (MVP-1)
- ✅ Indexes on frequently queried columns (customer_id, created_at, api_key_id)
- ✅ UNIQUE index on Policy.key
- ✅ Foreign key constraints

### Planned (MVP-2+)
- Partition `UsageLog` by date (old records → separate storage)
- Read replicas for audit queries (analytics queries don't block writes)
- Archive old logs to cold storage (S3) after 90 days

### Query Performance Targets
| Query | Current | Target |
|-------|---------|--------|
| `/v1/check` endpoint | <50ms | <10ms |
| Audit log query (1000 rows) | <100ms | <20ms |
| Policy lookup | <10ms | <5ms |

---

## Implementation Checklist for MVP-2

- [ ] **Key-ID Format**: Update `generate_api_key.py` to emit `id.raw` format
- [ ] **Auth Optimization**: Update `auth.py` to split token and use direct lookup
- [ ] **Add index**: `CREATE INDEX idx_apikey_id ON apikey(id)` (already exists as PK)
- [ ] **Redis Setup**: Add `redis` to requirements, configure connection string
- [ ] **Rate Limit Migration**: Replace in-memory dict with Redis
- [ ] **Policy Caching**: Add TTL-based cache layer
- [ ] **Load Testing**: Benchmark before/after with k6 or Apache JMeter
- [ ] **Documentation**: Update deployment guide with Redis/scaling architecture

---

## Monitoring & Alerting

### Key Metrics to Track
1. **API Response Time**: p50, p95, p99 latencies
2. **Rate Limit Hit Rate**: % of requests throttled
3. **Cache Hit Rate**: Policy cache effectiveness
4. **Database Connection Pool**: Active connections vs. max
5. **Error Rates**: 4xx, 5xx percentages

### Alerting Rules
- Response time p99 > 500ms → Scale out
- Rate limit hit rate > 10% → Increase limit or add capacity
- DB connections > 80% of pool → Add replicas
- Error rate > 1% → Investigate

---

## Summary

| Phase | Focus | Timeline |
|-------|-------|----------|
| **MVP-1 (Current)** | Single instance, in-memory rate limit, full table scan for keys | Now |
| **MVP-2** | Multi-instance with Redis, key-ID optimization, policy caching | When >1000 customers |
| **MVP-3** | Enterprise scale with Kubernetes, event streaming, analytics | When >50k customers |

Start with MVP-1, monitor metrics, upgrade to MVP-2 when bottlenecks appear.
