# Production Readiness Checklist

**Status**: ✅ Pilot Launch Ready | 🚀 Pre-deployment verification

**Purpose**: Verify all infrastructure, security, compliance, and operational requirements are met before deploying to production.

**Target**: Pilot customer deployment (2-4 week timeline from today)

---

## 1. 🔐 Secrets Management

### Overview
Manage sensitive configuration (API keys, DB credentials, etc.) securely across environments.

### Hosting-Specific Configuration

#### **Render (Backend)**
```
Environment: Production
Variables to configure:
```

| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@neon...` | ✅ Yes |
| `REDIS_URL` | Redis Cloud or local | `redis://:password@host:6379` | ✅ Yes |
| `SENTRY_DSN` | Sentry project DSN | `https://xxx@xxx.ingest.sentry.io/xxx` | ✅ Yes |
| `ADMIN_API_KEY` | Generate with `scripts/generate_api_key.py` | `admin_xxxxx...` | ✅ Yes |
| `JWT_SECRET` | Random 32+ char string | `$(openssl rand -hex 32)` | ⏳ Phase 2 |
| `ENVIRONMENT` | Deployment environment | `production` | ✅ Yes |
| `LOG_LEVEL` | Logging level | `INFO` | ✅ Yes |

**Render Setup Steps**:
1. Create new Web Service on render.com
2. Connect GitHub repository
3. Set Runtime: `Python 3.11`
4. Add environment variables in Dashboard
5. Set Build Command: `pip install -r requirements.txt && alembic upgrade head`
6. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
7. Deploy

---

#### **Vercel (Frontend)**
```
Environment: Production
Variables to configure:
```

| Variable | Source | Example | Required |
|----------|--------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend URL | `https://api.yourdomain.com` | ✅ Yes |
| `NEXT_PUBLIC_ADMIN_KEY` | From backend admin key | Same as backend `ADMIN_API_KEY` | ✅ Yes |
| `NEXT_PUBLIC_SENTRY_DSN` | Same Sentry DSN | `https://xxx@xxx...` | ✅ Yes |

**Vercel Setup Steps**:
1. Create new Project on vercel.com
2. Connect GitHub repository (frontend folder)
3. Set Framework: `Next.js`
4. Set Root Directory: `frontend`
5. Add environment variables
6. Deploy

---

#### **Neon (PostgreSQL Database)**
```sql
Database Setup:
```

**Steps**:
1. Create account at neon.tech
2. Create new project
3. Copy connection string: `postgresql://user:password@...`
4. Add to Render environment variables as `DATABASE_URL`
5. Enable auto-backups (see section 2)

**First Deploy Only**:
```bash
# SSH into Render or run migration locally against production DB
alembic upgrade head
python scripts/seed_policies.py  # Initialize default policies
python scripts/generate_api_key.py admin@company.com  # Create admin key
```

---

#### **Redis Cloud (Rate Limiting)**
```
Setup:
```

**Steps**:
1. Create account at rediscloud.com
2. Create new database (free tier available)
3. Copy connection string: `redis://:password@host:port`
4. Add to Render environment variables as `REDIS_URL`
5. Enable auto-backup (25 GB snapshots included)

---

### Secret Rotation Strategy

**Monthly Rotation** (post-pilot):
1. Generate new `ADMIN_API_KEY`: `python scripts/generate_api_key.py admin@company.com`
2. Update in Render environment
3. Test dashboard access
4. Delete old key (if tracking keys)
5. Document rotation date

**Emergency Rotation** (if compromised):
1. Immediately rotate `DATABASE_URL` (Neon password reset)
2. Rotate `REDIS_URL` (RedisCloud password reset)
3. Regenerate `ADMIN_API_KEY`
4. Check Sentry for suspicious activity
5. Notify affected customers

---

## 2. 📦 Database Backups

### Strategy
- **Primary**: Automated snapshots (Neon)
- **Frequency**: Daily snapshots, 14-day retention
- **Recovery Time**: < 1 hour restore

### Neon Auto-Backup

**Enable Backups**:
1. Log into neon.tech dashboard
2. Select project → Settings → Backups
3. Enable "Automatic backups"
4. Set retention: 14 days (free tier default)
5. Schedule: Daily 2 AM UTC (off-peak)

**Manual Backup**:
```bash
# Export data (before each deployment)
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Store in S3/GitHub (if needed)
```

**Restore Procedure** (if needed):
1. Neon dashboard → Backups → select snapshot
2. Click "Restore"
3. Wait for recovery (5-10 minutes)
4. Verify data integrity
5. Update `DATABASE_URL` if restored to new endpoint

**Backup Verification** (monthly):
1. Create test restore to separate Neon project
2. Run migration: `alembic upgrade head`
3. Query sample data to verify integrity
4. Delete test project

---

### Redis Backup

**RedisCloud Auto-Backup**:
1. RedisCloud dashboard → Database → Backups
2. Enable "Automatic backup"
3. Frequency: Daily
4. Retention: 7 days

**Manual Backup**:
```bash
# Trigger backup
redis-cli --host $REDIS_HOST -a $REDIS_PASSWORD BGSAVE

# Download from RedisCloud dashboard
```

---

## 3. 🔒 HTTPS, Domain & CORS

### HTTPS Configuration

**Render** (Backend):
- ✅ Automatic HTTPS (*.onrender.com subdomain)
- ✅ Free SSL certificate (auto-renewed)
- No additional configuration needed

**Vercel** (Frontend):
- ✅ Automatic HTTPS (*.vercel.app subdomain)
- ✅ Free SSL certificate (auto-renewed)
- No additional configuration needed

**Custom Domain Setup**:
```
Example: api.mycompany.com (backend)
```

**Steps**:
1. Render dashboard → Settings → Custom Domain
2. Add `api.mycompany.com`
3. Update DNS: Add CNAME record pointing to Render URL
4. Wait for DNS propagation (up to 24 hours)
5. Render auto-provisions SSL certificate

---

### CORS Configuration

**Current** (`backend/main.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Dev frontend
        "http://localhost:3001",      # Alt dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For Production** (update before deploying):
```python
import os

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],  # Explicit methods
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,  # Cache preflight 1 hour
)
```

**Environment Variable**:
```
# In Render production environment:
CORS_ORIGINS=https://dashboard.mycompany.com,https://dashboard-staging.mycompany.com
```

**Security Notes**:
- ✅ No `allow_origins=["*"]` (too permissive)
- ✅ Explicit methods (no unnecessary OPTIONS, PUT, DELETE)
- ✅ Specific headers only
- ✅ Credentials enabled for auth headers

---

## 4. 📋 Legal Documents

### DPA (Data Processing Agreement)

**Purpose**: Required when processing customer data (GDPR compliance).

**Template Contents**:
```
1. Data Processing Scope
   - What data is processed (audit logs, API keys)
   - How long data is stored (90 days default)
   - Purpose (governance enforcement, audit trail)

2. Data Security
   - Encryption in transit (HTTPS)
   - Encryption at rest (Neon, RedisCloud defaults)
   - Access controls (admin key auth)
   - Incident response (Sentry monitoring)

3. Sub-processors
   - Neon (PostgreSQL hosting)
   - RedisCloud (Redis hosting)
   - Render (Backend hosting)
   - Vercel (Frontend hosting)
   - Sentry (Error tracking)

4. Data Subject Rights
   - Access: Customer can request logs
   - Deletion: 90-day auto-purge
   - Portability: Export to CSV

5. Liability & Indemnification
   - AI Governance responsible for data security
   - Customer liable for API key management
```

**File**: `legal/DPA_TEMPLATE.md`

**Usage**:
1. Customize for your company/customer
2. Have legal team review
3. Send to customer for signature
4. Store signed copy

---

### Terms of Service (Simple Template)

**Template Contents**:
```
1. Service Description
   - What the platform does
   - Rate limits (100 req/60 sec)
   - SLA (99.5% uptime target)

2. Acceptable Use
   - No harassment/abuse
   - No malicious testing
   - No data exfiltration

3. Limitations
   - Beta/pilot phase (use at own risk)
   - No warranties (provided as-is)
   - Liability cap (refund of fees paid)

4. Termination
   - Either party can terminate (30 days notice)
   - Data deleted 90 days after termination
   - Fees non-refundable for pilot

5. Privacy
   - Audit logs stored 90 days
   - Personal data minimization (metadata only)
   - GDPR compliance (DPA required)

6. Contact
   - support@company.com
   - Legal: legal@company.com
```

**File**: `legal/TERMS_TEMPLATE.md`

**Usage**:
1. Customize for your company
2. Have legal team review
3. Post on website
4. Send to customer with DPA

---

## 5. 📞 Support & Contact Flow

### Support Channels

**Tier 1: Email Support** (24-48 hour response)
```
support@company.com
- General questions
- Feature requests
- Non-urgent bugs
```

**Tier 2: Slack/Discord** (pilot phase, real-time)
```
#ai-governance-support (internal team channel)
- Urgent issues
- Direct customer contact (pilot phase)
- Real-time debugging
```

**Tier 3: Escalation** (via phone, for critical issues)
```
On-call: +1-XXX-XXX-XXXX
- Production outage (> 15 min downtime)
- Data loss incident
- Security breach
```

---

### Support Workflow

**New Ticket** (Customer → support@company.com):
```
1. Receive email
2. Auto-reply: "Ticket #XXX received, response within 24 hours"
3. Triage: Assign label (bug/feature/question)
4. Respond: Troubleshoot or escalate
5. Resolve: Close with summary
6. Follow-up: Check satisfaction 1 week later
```

**Bug Report Template** (for customer to use):
```
Subject: [BUG] Dashboard not loading

Description:
- What happened: Dashboard shows blank screen
- Expected: Should show API keys list
- Steps to reproduce:
  1. Login with admin key
  2. Navigate to /dashboard/keys
  3. See blank screen
- Environment: Chrome, macOS
- API Key: admin_xxx...
- Timestamp: 2025-11-16 14:30 UTC

Logs/Screenshots: [attached]
```

---

### Status Page

**Option 1: Uptime Robot** (free):
```
https://uptime.mycompany.com
- Monitor /health endpoint
- Status updates via email/RSS
- Show to customers
```

**Option 2: Statuspage.io** (paid):
```
https://status.mycompany.com
- Real-time uptime dashboard
- Incident notifications
- Scheduled maintenance warnings
```

---

## 6. 📊 Monitoring Alerts

### Alert Thresholds

| Alert | Threshold | Action |
|-------|-----------|--------|
| **Error Rate** | > 1% of requests | Page on-call engineer |
| **API Latency** | > 500 ms p95 | Investigate backend |
| **DB Connection Pool** | > 80% utilized | Scale up or optimize queries |
| **Redis Memory** | > 80% used | Increase Redis instance |
| **Rate Limit Violations** | > 10% blocked | Review customer limits |
| **Sentry Issues** | > 10 new errors/hour | Investigate immediately |
| **Disk Space** | > 80% full | Clean up or expand |
| **Backup Failure** | Backup failed for 24h | Manual intervention needed |

---

### Setup in Sentry

**Error Rate Alert**:
```
1. Sentry dashboard → Alerts → Create Alert Rule
2. Condition: Error events > 10 in 5 minutes
3. Action: Send to #alerts Slack channel
4. Name: "High Error Rate"
```

**Performance Alert**:
```
1. Sentry → Alerts → Create Alert Rule
2. Condition: Transaction duration > 1000ms (p95)
3. Action: Send to #alerts Slack channel
4. Name: "Slow API Response"
```

---

### Grafana Dashboard Alerts

**Current Status**: ✅ Prometheus + Grafana dashboard deployed

**Alerts to Configure**:
```
1. Dashboard.go → Alerting → Alert rules
2. Create rules for each metric:
   - api_requests_total (count)
   - api_response_time (latency)
   - rate_limit_hits (violations)
   - database_query_time (slow queries)
```

**Example Rule**:
```yaml
alert: HighErrorRate
expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.01
for: 5m
annotations:
  summary: "High error rate detected"
  action: "Check backend logs in Sentry"
```

---

### Alerting Destinations

**Option 1: Email Notifications** (basic)
```
- Sentry auto-sends to configured email
- Alertmanager sends to ops team
```

**Option 2: Slack Integration** (recommended)
```
1. Create Slack workspace #alerts channel
2. Sentry → Integrations → Slack → Connect
3. Grafana → Alerting → Notification channels → Slack
4. Render → Settings → Notifications → Slack

All alerts flow to #alerts in real-time
```

**Option 3: PagerDuty** (for on-call escalation)
```
1. Create PagerDuty account
2. Sentry → Integrations → PagerDuty
3. Set escalation policy: Page on-call engineer
4. Configure notification routing
```

---

## 7. 💳 Billing & Stripe Sandbox

### Billing Model Options

**Option A: Per-API-Key Monthly** (simplest)
```
- Free tier: 10,000 requests/month
- Pro tier: $49/month (unlimited requests)
- Enterprise: Custom pricing + support

Billing cycle: Monthly from signup date
```

**Option B: Pay-as-You-Go** (usage-based)
```
- $0.01 per 1,000 requests
- $0.50 per policy evaluation
- Minimum: $10/month

Billing cycle: Monthly, invoiced on 1st
```

**Option C: Pilot (Free/Custom)** (for pilot phase)
```
- Pilot customers: Free for 6 months
- After pilot: Move to Pro tier or custom
- Commitment: Feedback + case study
```

**Current Recommendation**: **Option C (Pilot Free)** for first customer, then evaluate usage patterns for tier selection.

---

### Stripe Sandbox Setup

**Step 1: Create Stripe Account**
```
1. Go to stripe.com
2. Sign up for developer account
3. Enable "Test Mode"
4. Copy test API keys
```

**Step 2: Add Stripe to Backend**
```bash
pip install stripe
```

**Step 3: Create Billing Endpoint**
```python
# backend/billing.py (NEW)

import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

async def create_subscription(customer_id: str, tier: str) -> dict:
    """Create monthly subscription for customer"""
    
    # Tier price IDs (from Stripe dashboard)
    PRICE_IDS = {
        "pro": "price_xxxx",
        "enterprise": "price_yyyy",
    }
    
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": PRICE_IDS[tier]}],
        payment_behavior="default_incomplete",
    )
    
    return {
        "subscription_id": subscription.id,
        "status": subscription.status,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
    }

async def get_invoice(subscription_id: str) -> dict:
    """Get current invoice"""
    
    subscription = stripe.Subscription.retrieve(subscription_id)
    invoices = stripe.Invoice.list(subscription=subscription_id, limit=1)
    
    if invoices.data:
        return {
            "invoice_id": invoices.data[0].id,
            "amount": invoices.data[0].amount_paid,
            "status": invoices.data[0].status,
            "pdf_url": invoices.data[0].invoice_pdf,
        }
    
    return None
```

**Step 4: Add Billing Routes**
```python
# backend/main.py (ADD)

from billing import create_subscription, get_invoice

@app.post("/api/billing/subscribe")
async def subscribe(tier: str, customer_id: str):
    """Subscribe customer to a tier"""
    return await create_subscription(customer_id, tier)

@app.get("/api/billing/invoice/{subscription_id}")
async def get_invoice_route(subscription_id: str):
    """Get invoice for subscription"""
    return await get_invoice(subscription_id)
```

**Step 5: Environment Variables**
```
# In Render production environment:
STRIPE_SECRET_KEY=sk_test_xxx (test mode during pilot)
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

**Step 6: Test Payment**
```bash
# Use Stripe test card: 4242 4242 4242 4242
curl -X POST http://localhost:8000/api/billing/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "pro",
    "customer_id": "cus_xxx"
  }'
```

---

## 8. ✅ Pre-Deployment Verification

### Checklist (Run 1 week before pilot launch)

- [ ] **Secrets**
  - [ ] DATABASE_URL configured in Render
  - [ ] REDIS_URL configured in Render
  - [ ] ADMIN_API_KEY generated and stored
  - [ ] SENTRY_DSN configured
  - [ ] All secrets rotated from development

- [ ] **Database**
  - [ ] Neon database created and tested
  - [ ] Alembic migrations applied (`alembic upgrade head`)
  - [ ] Policies seeded (`python scripts/seed_policies.py`)
  - [ ] Auto-backup enabled (14-day retention)
  - [ ] Manual backup tested (restore procedure verified)

- [ ] **HTTPS & Domain**
  - [ ] Backend HTTPS working (curl https://api.mycompany.com/health)
  - [ ] Frontend HTTPS working (https://dashboard.mycompany.com)
  - [ ] Custom domain DNS configured (CNAME pointing to Render/Vercel)
  - [ ] CORS configured for production domain
  - [ ] SSL certificates auto-renewed

- [ ] **Monitoring**
  - [ ] Sentry DSN configured (errors being tracked)
  - [ ] Grafana dashboard accessible
  - [ ] Alert rules configured (error rate, latency, rate limits)
  - [ ] Slack integration working (#alerts channel receiving alerts)
  - [ ] Uptime monitor running (Uptime Robot or Statuspage)

- [ ] **Legal**
  - [ ] DPA created and reviewed by legal team
  - [ ] Terms of Service created and reviewed
  - [ ] Privacy policy updated (90-day log retention)
  - [ ] Customer has signed DPA and accepted ToS

- [ ] **Support**
  - [ ] Support email configured (support@company.com)
  - [ ] Support ticket template created
  - [ ] Slack #support channel created (internal)
  - [ ] On-call schedule published
  - [ ] Status page deployed (Uptime Robot or Statuspage)

- [ ] **Billing** (if applicable)
  - [ ] Stripe test keys configured (Render environment)
  - [ ] Billing endpoints tested in sandbox
  - [ ] Invoice generation tested
  - [ ] Payment processing tested (with test card 4242...)
  - [ ] Subscription management UI ready

- [ ] **Performance**
  - [ ] Load test run: 1000 req/s for 5 minutes
  - [ ] p95 latency < 500ms
  - [ ] Error rate < 1%
  - [ ] Rate limiting working correctly

- [ ] **Security**
  - [ ] pip-audit run (zero vulnerabilities)
  - [ ] npm audit run (zero vulnerabilities in frontend)
  - [ ] SQL injection tests passed
  - [ ] XSS tests passed
  - [ ] CORS misconfiguration checked

- [ ] **Customer Ready**
  - [ ] Dashboard access link shared
  - [ ] Admin API key provided
  - [ ] Support email provided
  - [ ] On-call contact provided
  - [ ] 30-minute onboarding call scheduled

---

## 9. 🚀 Deployment Timeline

### Week 1: Infrastructure Setup
```
Mon: Neon database created, auto-backup enabled
Tue: RedisCloud created, Render/Vercel projects created
Wed: Secrets configured, migrations applied
Thu: Custom domain DNS configured, SSL certs issued
Fri: Load testing on staging
```

### Week 2: Legal & Support
```
Mon: DPA created, reviewed with legal team
Tue: Terms of Service finalized
Wed: Support channels setup (#support, support@company.com)
Thu: Monitoring alerts configured
Fri: Final security audit (pip-audit, npm audit)
```

### Week 3: Customer Onboarding
```
Mon: Generate pilot customer API key
Tue: Send onboarding email (dashboard URL, support contacts)
Wed: 30-minute kickoff call with customer
Thu: Monitor first requests, verify everything working
Fri: Weekly check-in, gather feedback
```

### Week 4+: Production Operations
```
Ongoing:
- Monitor Sentry errors
- Check Grafana metrics daily
- Weekly backup verification
- Monthly secret rotation
- Bi-weekly customer check-ins
```

---

## 10. 🆘 Troubleshooting

### Common Issues & Fixes

**Issue**: Dashboard shows "API not responding"
```
Fix:
1. Check NEXT_PUBLIC_API_URL in Vercel environment
2. Verify CORS_ORIGINS includes frontend domain
3. Check backend logs in Render → Logs
4. Verify Sentry DSN working (errors should appear)
```

**Issue**: Rate limiting not working
```
Fix:
1. Check REDIS_URL is set (else uses in-memory single-instance)
2. Verify Redis connection: `redis-cli ping`
3. Check rate_limit.py logs for fallback warnings
4. Load test to verify limits enforced
```

**Issue**: Database connection timeout
```
Fix:
1. Check DATABASE_URL is correct
2. Verify Neon database is running (check project status)
3. Check connection pool size (not exceeded max connections)
4. Restart Render backend
```

**Issue**: Sentry not receiving errors
```
Fix:
1. Verify SENTRY_DSN is set correctly
2. Check Sentry project is active
3. Verify error is occurring (check app logs)
4. Re-deploy to pick up SENTRY_DSN change
```

---

## Appendix: Environment Variables Reference

### Backend (Render)

```env
# Database
DATABASE_URL=postgresql://user:pass@host/dbname

# Redis
REDIS_URL=redis://:password@host:port

# Sentry
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# Admin
ADMIN_API_KEY=admin_xxxxxxxxxxxxxx

# CORS
CORS_ORIGINS=https://dashboard.mycompany.com

# General
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Frontend (Vercel)

```env
# Backend API
NEXT_PUBLIC_API_URL=https://api.mycompany.com

# Admin Authentication
NEXT_PUBLIC_ADMIN_KEY=admin_xxxxxxxxxxxxxx

# Monitoring
NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

---

## Sign-Off

**Checklist Owner**: AI Governance Team

**Last Updated**: November 16, 2025

**Status**: 🟢 Ready for pilot deployment (all items actionable)

**Next Step**: Begin infrastructure setup in Week 1

---

## Related Documents

- `PILOT_LAUNCH_CHECKLIST.md` - Customer communication checklist
- `STARTUP_REPORT.md` - System verification results
- `SECURITY_LOAD_TESTING.md` - Performance & security testing
- `OBSERVABILITY.md` - Monitoring setup guide
- `frontend/DASHBOARD_README.md` - Dashboard documentation
