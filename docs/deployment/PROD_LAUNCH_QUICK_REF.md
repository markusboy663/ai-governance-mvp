# Production Launch Checklist - Quick Reference

**Status**: ✅ All documentation complete | 🚀 Ready to begin deployment

**Timeline**: 4 weeks from today (target mid-December 2025)

---

## Week 1: Infrastructure Setup (Infrastructure Team)

### Database & Cache
- [ ] Create Neon PostgreSQL database
  - [ ] Copy connection string
  - [ ] Enable auto-backup (14-day retention)
  - [ ] Run migrations: `alembic upgrade head`
  - [ ] Seed policies: `python scripts/seed_policies.py`
  
- [ ] Create RedisCloud instance
  - [ ] Copy connection string  
  - [ ] Enable auto-backup

### Hosting
- [ ] Create Render project for backend
  - [ ] Connect GitHub repository
  - [ ] Set build/start commands (see PROD_READINESS_CHECKLIST.md section 1)
  - [ ] Configure environment variables (DATABASE_URL, REDIS_URL, ADMIN_API_KEY, SENTRY_DSN)
  - [ ] Deploy and test

- [ ] Create Vercel project for frontend
  - [ ] Connect GitHub repository
  - [ ] Set root directory to `frontend`
  - [ ] Configure environment variables (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_ADMIN_KEY)
  - [ ] Deploy and test

### Domain & HTTPS
- [ ] Configure custom domain (optional but recommended)
  - [ ] Add CNAME record to DNS
  - [ ] Wait for propagation (up to 24 hours)
  - [ ] Verify SSL certificate auto-provisioned
  
- [ ] Update CORS configuration (backend/main.py)
  - [ ] Set CORS_ORIGINS environment variable
  - [ ] Test from frontend domain

### Testing
- [ ] [ ] Test /health endpoint: `curl https://api.yourdomain.com/health`
- [ ] Test dashboard: `https://dashboard.yourdomain.com` loads
- [ ] Test API authentication works
- [ ] Run load test: `python load_test.py` (verify < 500ms p95)

---

## Week 2: Legal & Compliance (Legal + Operations)

### Legal Documents
- [ ] Review DPA template (legal/DPA_TEMPLATE.md)
  - [ ] Customize for your company
  - [ ] Have legal team review and approve
  - [ ] Prepare for customer signature

- [ ] Review Terms of Service (legal/TERMS_TEMPLATE.md)
  - [ ] Customize for your company
  - [ ] Have legal team review and approve
  - [ ] Publish on website

### Support Setup
- [ ] Create support email: support@company.com (forwarding or mailbox)
- [ ] Create Slack workspace or channel: #ai-governance-support
- [ ] Invite pilot customer to Slack (if they're interested)
- [ ] Set up on-call rotation (see SUPPORT_OPERATIONS.md)
- [ ] Create status page (Uptime Robot or Statuspage.io)

### Monitoring & Alerts
- [ ] Configure Sentry
  - [ ] Copy DSN to Render environment variable
  - [ ] Test error tracking (trigger a test error)
  - [ ] Create Slack integration for #alerts channel
  
- [ ] Configure Grafana alerts
  - [ ] Set thresholds (error rate > 1%, latency > 500ms)
  - [ ] Configure Slack notifications
  - [ ] Test alert firing

- [ ] Set up uptime monitoring
  - [ ] Configure Uptime Robot: `https://api.yourdomain.com/health`
  - [ ] Enable email + Slack notifications

### Billing (if applicable)
- [ ] Set up Stripe sandbox
  - [ ] Create Stripe account
  - [ ] Generate test API keys
  - [ ] Add to Render environment variables
  - [ ] Test payment processing with test card 4242...

---

## Week 3: Customer Onboarding Prep (Product/Sales)

### Documentation
- [ ] Prepare customer onboarding email (template below)
- [ ] Create API key for pilot customer: `python scripts/generate_api_key.py customer@company.com`
- [ ] Document dashboard URL
- [ ] Document support contact and response times

### Customer Kick-off
- [ ] Schedule 30-minute onboarding call
  - [ ] 10 min: Platform overview
  - [ ] 10 min: Dashboard walkthrough
  - [ ] 10 min: Q&A, concerns, feedback
  
- [ ] Send customer onboarding email with:
  - [ ] Dashboard URL
  - [ ] Admin API key (regenerate new one, don't reuse)
  - [ ] Support email
  - [ ] On-call contact (for critical issues)
  - [ ] DPA & Terms of Service for signature
  - [ ] Sample curl command to test API

### Pre-Launch Testing
- [ ] [ ] Run full end-to-end test
  - [ ] Dashboard loads and shows empty state
  - [ ] Create test API key
  - [ ] Make test request to /v1/check endpoint
  - [ ] Verify log appears in dashboard
  - [ ] Test rate limiting (send 101 requests, verify 429 on 101st)

---

## Week 4: Go-Live & Operations (Full Team)

### Launch Day
- [ ] Send customer welcome email (morning of launch)
- [ ] Hold kick-off call (confirm everything working)
- [ ] Monitor metrics closely (first 24 hours)
  - [ ] Watch error rate in Sentry
  - [ ] Watch latency in Grafana
  - [ ] Watch rate limit hits
  - [ ] Check customer questions in support email

### Post-Launch
- [ ] Daily check-in with customer (first week)
  - [ ] "Any issues today?"
  - [ ] "What feedback do you have?"
  - [ ] Gather feature requests

- [ ] Weekly operational review (ongoing)
  - [ ] Check backup status
  - [ ] Review Sentry errors
  - [ ] Check metrics dashboard
  - [ ] Rotate secrets if needed

---

## Document References

| Document | Purpose | Owner | Link |
|----------|---------|-------|------|
| **PROD_READINESS_CHECKLIST.md** | Detailed infrastructure setup | Infrastructure | Root |
| **SUPPORT_OPERATIONS.md** | Support workflow & incident response | Operations | Root |
| **legal/DPA_TEMPLATE.md** | Data Processing Agreement | Legal | legal/ |
| **legal/TERMS_TEMPLATE.md** | Terms of Service | Legal | legal/ |
| **frontend/DASHBOARD_README.md** | Dashboard user guide | Product | frontend/ |
| **SECURITY_LOAD_TESTING.md** | Performance benchmarks | Engineering | Root |
| **PILOT_LAUNCH_CHECKLIST.md** | Customer communication checklist | Product | Root |

---

## Customer Onboarding Email Template

```
Subject: Welcome to AI Governance Pilot Program! 🚀

Hi [Customer Name],

Congratulations on joining the AI Governance pilot program! We're excited to work with you.

Below is everything you need to get started:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 GETTING STARTED (5 minutes)

1. Dashboard Access
   URL: https://dashboard.yourdomain.com
   Admin Key: [XXXX] (generated just for you)
   
   Log in and explore:
   - Create API keys
   - Toggle policies
   - View audit logs

2. Generate Your First API Key
   In dashboard: Keys → Create New Key
   Name it: "Production" or "Development"
   
   You'll see the secret once - save it safely!
   Format: key_id.secret

3. Test the API
   Copy this curl command and run it:
   
   curl -X POST https://api.yourdomain.com/v1/check \
     -H "Authorization: Bearer YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-4",
       "operation": "classify",
       "metadata": {}
     }'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 SUPPORT & CONTACT

Questions? We're here to help!

- Email: support@company.com (response: 24-48 hours)
- Slack: Join #ai-governance-support for real-time chat
- Status Page: https://status.company.com (uptime info)
- Critical Issues: +1-XXX-XXX-XXXX (on-call)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 LEGAL & COMPLIANCE

Please review and sign:
- Data Processing Agreement (DPA): [Link]
- Terms of Service: [Link]

We need signed DPA before going production.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 NEXT STEPS

1. Accept Terms & Sign DPA
2. Log into dashboard at https://dashboard.yourdomain.com
3. Create your first API key
4. Test the API with curl command above
5. Schedule onboarding call (optional, highly recommended!)

Onboarding Call Time Slots (pick one):
- [Time 1]
- [Time 2]
- [Time 3]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 PILOT BENEFITS

During the pilot phase (6 months):
✅ Free access (no charges)
✅ Real-time support (Slack channel)
✅ Feature feedback (you shape the roadmap)
✅ Case study opportunity (optional)

After pilot (production):
→ Move to paid tier (Pro: $49/month or custom pricing)
→ Commercial SLA (99.9% uptime)
→ 24/7 phone support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We're excited to work with you! Let's build something great together.

Questions? Reply to this email or reach out on Slack.

Best,
[Your Name]
AI Governance Team
support@company.com
```

---

## Go/No-Go Criteria (Pre-Launch Review)

**Before launching, verify ALL of these are ✅**:

### Infrastructure
- [ ] ✅ API responds to health check (< 200ms)
- [ ] ✅ Dashboard loads in browser
- [ ] ✅ Database connects and migrations applied
- [ ] ✅ Redis cache working
- [ ] ✅ Backups automated and tested (restore succeeded)

### Security
- [ ] ✅ pip-audit: zero vulnerabilities
- [ ] ✅ npm audit: zero vulnerabilities
- [ ] ✅ HTTPS certificates valid
- [ ] ✅ CORS configured (no `allow_origins=['*']`)
- [ ] ✅ Admin API key generated and secured

### Monitoring
- [ ] ✅ Sentry receiving errors (test error sent)
- [ ] ✅ Prometheus metrics collecting
- [ ] ✅ Grafana dashboard displays data
- [ ] ✅ Alerts configured (error rate, latency, rate limits)
- [ ] ✅ Status page showing green

### Legal & Compliance
- [ ] ✅ DPA reviewed by legal team
- [ ] ✅ Terms of Service reviewed by legal team
- [ ] ✅ Customer signed DPA
- [ ] ✅ Privacy policy updated (90-day log retention)

### Operations
- [ ] ✅ Support email configured
- [ ] ✅ Slack #support channel created
- [ ] ✅ On-call schedule published
- [ ] ✅ Runbooks documented (common issues & fixes)
- [ ] ✅ Customer contact info confirmed

### Performance
- [ ] ✅ Load test: 1000 req/s for 5 min (p95 < 500ms, error rate < 1%)
- [ ] ✅ Rate limiting works (429 returned after 100 req/60 sec)
- [ ] ✅ Latency < 200ms (p50), < 500ms (p95)

**Decision**: ⭕ GO / 🛑 NO-GO (defer if anything is 🔴)

---

## Critical Path Timeline

```
Week 1: Infrastructure (Parallel)
├─ Database setup (Neon)
├─ Cache setup (RedisCloud)
├─ Backend deployment (Render)
├─ Frontend deployment (Vercel)
└─ Domain & HTTPS config

Week 2: Legal & Ops (Parallel)
├─ Legal docs reviewed
├─ Support setup
├─ Monitoring configured
└─ Billing setup (if applicable)

Week 3: Customer Prep
├─ Docs finalized
├─ API key generated
├─ Onboarding email drafted
└─ Kick-off call scheduled

Week 4: Go-Live
├─ Final testing
├─ Launch email sent
├─ Kick-off call (confirm live)
└─ Monitor 24/7 for issues
```

---

## Success Metrics (Post-Launch)

**Track these numbers for first 30 days**:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Uptime** | > 99.5% | Status page + Sentry |
| **API Latency (p95)** | < 500ms | Grafana dashboard |
| **Error Rate** | < 1% | Sentry error count / total requests |
| **Rate Limiting Accuracy** | 100% | Manual test + logs |
| **Customer Response Time** | 24-48 hours | Support ticket timestamps |
| **Bug Resolution Time** | < 72 hours | Support ticket tracking |
| **Customer Satisfaction** | > 8/10 | Weekly survey (1-10 scale) |

---

## Sign-Off

**Document Owner**: DevOps/Operations Lead

**Last Updated**: November 16, 2025

**Approval**:
- [ ] Eng Lead: _______  Date: _____
- [ ] Ops Lead: _______  Date: _____
- [ ] Legal Lead: _______  Date: _____
- [ ] Product Lead: _______  Date: _____

**Status**: 🟢 Ready for deployment (no blockers)

---

**Next Step**: Start Week 1 infrastructure setup!
