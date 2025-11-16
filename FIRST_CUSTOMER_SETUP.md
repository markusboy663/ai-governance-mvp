# 🎯 First Customer Onboarding & Integration Guide

**Version**: 1.0  
**Last Updated**: November 16, 2025  
**Status**: ✅ Production Ready  
**Audience**: Platform operators, pilot customer integrators

---

## 📖 Overview

This guide explains:
1. **How the system works** (architecture & components)
2. **How to use it** (as a platform operator)
3. **How to onboard first customer** (step-by-step)
4. **How customers integrate** (API usage)

---

## Part 1: How The System Works

### 🔄 Request Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ CUSTOMER APPLICATION                                        │
│ (Your AI system using our governance)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ POST /v1/check
                     │ Headers: Authorization: Bearer {API_KEY}
                     │ Body: { "operations": [...], "context": {...} }
                     ↓
┌──────────────────────────────────────────────────────────────┐
│ AI GOVERNANCE MVP - FASTAPI BACKEND (Port 8000)             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. AUTHENTICATION LAYER                                     │
│    ├─ Verify Bearer token = valid API key                  │
│    └─ O(1) lookup using key_id in PostgreSQL               │
│                                                              │
│ 2. RATE LIMITING LAYER                                      │
│    ├─ Token bucket per API key (100 req/60 sec)            │
│    └─ Redis-backed or in-memory fallback                    │
│                                                              │
│ 3. GOVERNANCE ENGINE                                        │
│    ├─ Load customer's active policies                       │
│    ├─ Evaluate operations against policies                  │
│    ├─ Calculate risk score:                                 │
│    │   • Personal data detected: +70 points                 │
│    │   • External model call: +50 points                    │
│    │   • Large dataset: +30 points                          │
│    │   • Unknown operation: +20 points                      │
│    └─ Decision: Allow (score < 50) or Block (score ≥ 50)  │
│                                                              │
│ 4. ASYNC LOGGING                                            │
│    ├─ Enqueue audit log (non-blocking)                      │
│    ├─ Background writer batches logs                        │
│    └─ Store: customer_id, timestamp, decision, risk_score   │
│                                                              │
│ 5. OBSERVABILITY                                            │
│    ├─ Prometheus metrics: requests, latency, errors         │
│    ├─ Grafana dashboards: real-time monitoring              │
│    └─ Sentry: error tracking                                │
│                                                              │
└──────────────┬───────────────────────────────────────────────┘
               │
               │ Response: { "allowed": true/false, "risk_score": 0-100, "reason": "..." }
               ↓
┌──────────────────────────────────────────────────────────────┐
│ CUSTOMER APPLICATION RECEIVES DECISION                       │
│ • If allowed: Continue with AI operation                     │
│ • If blocked: Log governance violation, alert user          │
└──────────────────────────────────────────────────────────────┘
```

### 🗄️ Data Model

**5 Database Tables**:

```
┌─────────────────────┐
│ Customer            │ Represents each company using the system
├─────────────────────┤
│ id (UUID)          │
│ name               │
│ tier (free/pro)    │
│ created_at         │
└─────────────────────┘
         ↓
┌──────────────────────────────────┐
│ APIKey                           │ Authentication credentials
├──────────────────────────────────┤
│ key_id (indexed, O(1) lookup)   │
│ customer_id (foreign key)        │
│ key_hash (bcrypt)                │
│ name (e.g., "prod-api-key")      │
│ active (true/false)              │
│ created_at, rotated_at           │
└──────────────────────────────────┘
         ↓
┌──────────────────────────┐       ┌──────────────────────────┐
│ Policy                   │       │ AuditLog                 │
├──────────────────────────┤       ├──────────────────────────┤
│ id (UUID)               │       │ id (UUID)               │
│ customer_id             │       │ customer_id             │
│ name                    │       │ request_id              │
│ rules (JSON)            │       │ decision (allow/block)  │
│ active (true/false)     │       │ risk_score (0-100)      │
│ created_at              │       │ created_at              │
└──────────────────────────┘       └──────────────────────────┘
```

### 🔐 Security Model

**API Key Flow**:
1. **Generation**: `python scripts/generate_api_key.py` → Creates bcrypt hash
2. **Storage**: Only hash stored (key_hash), actual key shown once
3. **Auth**: `Authorization: Bearer {key}` → Hash lookup in PostgreSQL
4. **Verification**: bcrypt.verify(provided_key, stored_hash)
5. **Rotation**: New key generated, old one kept for 7 days, then revoked

**Rate Limiting**:
- Per-customer quota: 100 requests per 60 seconds
- Token bucket algorithm (refill rate-based)
- Redis-backed for distribution (fallback: in-memory)
- Response header: `X-RateLimit-Remaining: 87`

---

## Part 2: How To Use The System

### 👤 Your Role as Platform Operator

You manage:
- ✅ Customer accounts (create, delete)
- ✅ API keys (generate, rotate, revoke)
- ✅ Governance policies (create, update)
- ✅ Monitoring (view logs, metrics, errors)
- ✅ Support (troubleshoot issues)

### 📊 Admin Dashboard (Frontend, Port 3000)

**Current Features**:
- Customer management
- Policy editor
- API key management
- Audit log viewer
- Metrics dashboard

**Access**: http://localhost:3000/dashboard

---

## Part 3: Onboarding Your First Customer

### Step 1: Create Customer Account

```powershell
# Connect to backend
curl -X POST http://localhost:8000/admin/customers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {YOUR_ADMIN_KEY}" \
  -d '{
    "name": "Acme AI Inc",
    "tier": "pro"
  }'

# Response:
# {
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "name": "Acme AI Inc",
#   "tier": "pro",
#   "created_at": "2025-11-16T10:30:00Z"
# }
```

### Step 2: Generate API Key for Customer

```powershell
# Generate key (shown only once!)
curl -X POST http://localhost:8000/admin/keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {YOUR_ADMIN_KEY}" \
  -d '{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "prod-api-key-001"
  }'

# Response:
# {
#   "id": "key_xxx...",
#   "key_id": "keyid_550e8400",
#   "key": "sk_live_abc123...",  ← SAVE THIS! Only shown once
#   "name": "prod-api-key-001",
#   "created_at": "2025-11-16T10:32:00Z"
# }

# Send this to customer securely (email, secure channel)
# They will use: Authorization: Bearer sk_live_abc123...
```

### Step 3: Create Governance Policies

```powershell
# Define what operations are allowed
curl -X POST http://localhost:8000/policies \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {YOUR_ADMIN_KEY}" \
  -d '{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Allow Internal Data Only",
    "rules": {
      "max_external_calls": 5,
      "block_personal_data": true,
      "allowed_models": ["gpt-4", "claude-3"],
      "max_tokens": 10000
    },
    "active": true
  }'

# Response:
# {
#   "id": "policy_xxx",
#   "customer_id": "550e8400-e29b-41d4-a716-446655440000",
#   "name": "Allow Internal Data Only",
#   "rules": {...},
#   "active": true,
#   "created_at": "2025-11-16T10:35:00Z"
# }
```

### Step 4: Customer Tests Integration

Send this to customer:

```bash
# Test 1: Health check
curl http://localhost:8000/health

# Test 2: Make governance check
curl -X POST http://localhost:8000/v1/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk_live_abc123..." \
  -d '{
    "operations": [
      {
        "type": "llm_call",
        "model": "gpt-4",
        "tokens": 500
      }
    ],
    "context": {
      "user_id": "user_123",
      "session_id": "session_456"
    }
  }'

# Response (if allowed):
# {
#   "allowed": true,
#   "risk_score": 20,
#   "reason": "Within policy limits",
#   "request_id": "req_789"
# }

# Response (if blocked):
# {
#   "allowed": false,
#   "risk_score": 75,
#   "reason": "Personal data detected in context",
#   "request_id": "req_789"
# }
```

### Step 5: Monitor Customer Activity

```powershell
# View customer's audit logs
curl http://localhost:8000/logs \
  -H "Authorization: Bearer {YOUR_ADMIN_KEY}" \
  -d "customer_id=550e8400-e29b-41d4-a716-446655440000"

# View real-time metrics
curl http://localhost:8000/metrics
# Returns Prometheus format metrics:
# - governance_checks_total{customer="acme"}
# - governance_decisions_allowed{customer="acme"}
# - governance_decisions_blocked{customer="acme"}
# - governance_risk_score{customer="acme"}
# - request_latency_ms{endpoint="/v1/check"}
```

---

## Part 4: Customer Integration Instructions

**Send this to your first customer:**

### 📋 What You Need

1. **API Key** (provided by Acme team):
   ```
   sk_live_abc123...
   ```

2. **Endpoint**: `http://localhost:8000/v1/check` (for development)

3. **Documentation**: See examples below

### 🔄 Integration Steps

**Step 1: Make a Governance Check Request**

```python
import requests

# Your API key
API_KEY = "sk_live_abc123..."

# The governance endpoint
url = "http://localhost:8000/v1/check"

# Prepare request
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "operations": [
        {
            "type": "llm_call",
            "model": "gpt-4",
            "tokens": 500,
            "provider": "openai"
        }
    ],
    "context": {
        "user_id": "user_123",
        "session_id": "session_abc",
        "department": "engineering"
    }
}

# Make request
response = requests.post(url, headers=headers, json=payload)
result = response.json()

# Handle response
if response.status_code == 200:
    if result["allowed"]:
        print(f"✅ Allowed! Risk score: {result['risk_score']}")
        # Proceed with AI operation
    else:
        print(f"❌ Blocked! Reason: {result['reason']}")
        # Stop operation, alert user
else:
    print(f"Error: {response.status_code}")
```

**Step 2: Handle Different Response Codes**

```
200 OK → Governance check completed (allowed or blocked)
401 Unauthorized → Invalid or missing API key
429 Too Many Requests → Rate limit exceeded (max 100/60 sec)
500 Server Error → Contact support
```

**Step 3: Implement Rate Limiting**

```python
# Check response headers
remaining = response.headers.get("X-RateLimit-Remaining")
reset_at = response.headers.get("X-RateLimit-Reset")

if remaining and int(remaining) < 10:
    print(f"⚠️ Approaching rate limit! {remaining} requests left")
    
if response.status_code == 429:
    print(f"Rate limited until {reset_at}")
    # Back off and retry after reset time
```

---

## 🎯 First Customer Success Criteria

Before considering first customer integration complete:

### ✅ Technical Setup
- [ ] Customer account created
- [ ] API key generated and delivered securely
- [ ] Governance policies configured
- [ ] 15 integration tests passing
- [ ] Backend responding on 8000
- [ ] Frontend dashboard accessible

### ✅ Customer Testing
- [ ] Customer tested API with cURL
- [ ] Customer tested with their own code
- [ ] Rate limiting verified
- [ ] Error handling confirmed
- [ ] Audit logs visible in dashboard

### ✅ Operations
- [ ] Monitoring dashboard set up (Grafana)
- [ ] Alert rules configured
- [ ] Support procedures documented
- [ ] Incident runbooks prepared
- [ ] Weekly check-in scheduled

---

## 🚀 Deployment Checklist

### Before Going to Production

**Infrastructure**:
- [ ] PostgreSQL database configured (not SQLite)
- [ ] Redis instance available (rate limiting)
- [ ] SSL/TLS certificates installed
- [ ] DNS records configured
- [ ] CDN configured (if using)

**Security**:
- [ ] Environment variables set (.env file)
- [ ] API key rotation policy active
- [ ] CORS configured correctly
- [ ] Rate limits tuned for production
- [ ] Sentry DSN configured (error tracking)

**Operations**:
- [ ] Backup strategy in place
- [ ] Monitoring alerts active
- [ ] Runbooks documented
- [ ] Support team trained
- [ ] On-call schedule established

**Documentation**:
- [ ] Integration guide sent to customer
- [ ] SLA document signed
- [ ] Support contact established
- [ ] Training completed

---

## 📊 Monitoring & Observability

### Key Metrics to Watch

**Per-Customer**:
- Total requests (should be steady)
- Allowed vs blocked decisions
- Average risk score
- Error rate
- Rate limit violations

**Per-API-Key**:
- Requests per key
- Key rotation frequency
- Key age (oldest/newest)

**System-Wide**:
- p95 latency (target: < 500ms)
- Error rate (target: < 1%)
- Database connection pool usage
- Redis memory usage
- Queue depth (async logs)

### Grafana Dashboard

Import `docs/grafana-dashboard.json` for:
- 11-panel monitoring dashboard
- Real-time metrics visualization
- SLA monitoring
- Alert configuration

---

## 🆘 Troubleshooting First Customer Issues

### Issue: "401 Unauthorized"
```
Cause: Invalid or expired API key
Solution: 
  1. Verify key format (starts with sk_live_)
  2. Check Authorization header format (Bearer {key})
  3. Regenerate key if necessary
```

### Issue: "429 Too Many Requests"
```
Cause: Rate limit exceeded (100 req/60 sec)
Solution:
  1. Check current request rate
  2. Implement request batching/queuing
  3. Request higher tier if needed
```

### Issue: "403 Forbidden - Risk Score Too High"
```
Cause: Governance policy blocked request
Solution:
  1. Review what triggered high risk score
  2. Adjust policies if needed
  3. Provide more context (less personal data)
```

### Issue: "500 Server Error"
```
Cause: Backend error
Solution:
  1. Check server logs: `docker logs governance-backend`
  2. Check Sentry for error details
  3. Contact support with request_id
```

---

## 📞 Support & Escalation

### Level 1: Self-Service (Customer)
- Check integration guide (this document)
- Review API documentation
- Test with provided cURL examples
- Check rate limit headers

### Level 2: Email Support
- Response time: 4 business hours
- Contact: support@example.com
- Include: request_id, error message, reproduction steps

### Level 3: Phone Support (Pro tier only)
- Response time: 1 hour
- Available: 9am-5pm your timezone
- Contact: +1-xxx-xxx-xxxx

---

## 🔄 Next Steps After First Customer

1. **Gather Feedback** (Week 1)
   - Customer pain points
   - Feature requests
   - Performance observations

2. **Optimize Based on Feedback** (Week 2-3)
   - Adjust policies
   - Improve documentation
   - Fix any bugs

3. **Onboard 2nd-3rd Customers** (Week 4)
   - Repeat onboarding process
   - Look for patterns
   - Refine procedures

4. **Prepare for Scale** (Week 5-6)
   - Load testing
   - Infrastructure optimization
   - Team training

---

## 📚 Additional Resources

- **[QUICK_START.md](QUICK_START.md)** - Backend/frontend setup
- **[docs/architecture/README.md](docs/architecture/README.md)** - System design
- **[docs/TESTING.md](docs/TESTING.md)** - Complete API examples
- **[docs/RATE_LIMITING.md](docs/RATE_LIMITING.md)** - Rate limiting details
- **[docs/SECURITY_LOAD_TESTING.md](docs/SECURITY_LOAD_TESTING.md)** - Performance tests

---

**Status**: ✅ Ready to onboard first customer  
**Last Updated**: November 16, 2025  
**Support**: See troubleshooting section above
