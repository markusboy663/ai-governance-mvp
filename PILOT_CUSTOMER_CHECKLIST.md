# Pilot Customer Setup Checklist

**Customer:** [Company Name]  
**Pilot Start Date:** [Date]  
**Primary Contact:** [Name, Email, Phone]  
**Secondary Contact:** [Name, Email, Phone]

---

## Pre-Onboarding (Internal)

### Week -1 (Before Customer Kickoff)

**Infrastructure Readiness:**
- [ ] API deployed to production (Render)
- [ ] Dashboard deployed (Vercel)
- [ ] Database migrated (Neon)
- [ ] Backups enabled
- [ ] Monitoring configured (Sentry, Grafana)
- [ ] Status page live
- [ ] CORS configured for customer domain (if applicable)

**Customer Preparation:**
- [ ] Generate pilot API key: `python scripts/generate_api_key.py [customer_email]`
- [ ] Generate admin key: `python scripts/generate_api_key.py [customer_admin_email]`
- [ ] Add to DPA (DPA_TEMPLATE.md customized)
- [ ] Add to Terms (TERMS_TEMPLATE.md customized)
- [ ] Prepare onboarding email
- [ ] Prepare PILOT_CUSTOMER_INTEGRATION.md (customize with customer name/key ID)
- [ ] Schedule 30-min kickoff call

**Documentation:**
- [ ] Send this checklist to support team
- [ ] Brief support team on common issues (SUPPORT_OPERATIONS.md)
- [ ] Add customer to Slack #ai-governance-support (if invited)
- [ ] Create ticket in support system for customer

---

## Onboarding Phase (Weeks 1-2)

### Day 1: Send Onboarding Package

**Deliverables to Customer:**
- [ ] Welcome email (template in PROD_LAUNCH_QUICK_REF.md)
- [ ] PILOT_CUSTOMER_INTEGRATION.md (1-pager quick start)
- [ ] Dashboard login credentials
- [ ] API key (key_id.secret)
- [ ] DPA for signature
- [ ] Terms of Service
- [ ] Status page URL (for monitoring)
- [ ] Support contacts (email, Slack, on-call)

**Email Subject Line:**
```
🎉 Welcome to AI Governance Pilot - Quick Start Guide
```

**Include:**
```
Hi [Customer Name],

Congratulations on joining the AI Governance pilot program!

Attached:
- PILOT_CUSTOMER_INTEGRATION.md (1-page quick start)
- Your API keys (store securely!)
- Dashboard login
- Legal docs (DPA, Terms)

Next step: Schedule 30-minute kickoff call
→ [Calendar link]

Questions? Reply to this email or Slack #ai-governance-support

Welcome aboard! 🚀
```

---

### Day 2-3: Monitor for Issues

**Daily Checks:**
- [ ] Monitor customer API calls (check metrics dashboard)
- [ ] Watch for errors in Sentry (any customer-related errors?)
- [ ] Verify dashboard accessible (test login if needed)
- [ ] Check support email for questions (respond within 24h)

**If No API Calls After 24h:**
- [ ] Send follow-up email: "Any questions getting started?"
- [ ] Offer 15-min troubleshooting call
- [ ] Check dashboard login works

---

### Day 4-5: Kickoff Call

**30-Minute Agenda:**
1. **Welcome** (2 min)
   - Quick intro of support team
   - Overview of call agenda

2. **Platform Overview** (8 min)
   - How AI Governance works (policy check flow)
   - Request/response cycle
   - Security guarantees (metadata only, no prompts)

3. **Dashboard Walkthrough** (10 min)
   - Show API Keys page (create, rotate, delete)
   - Show Policies page (toggle, view violations)
   - Show Logs page (filter, pagination)
   - Show their test API key and first requests

4. **Integration Details** (5 min)
   - Explain metadata vs content (security critical!)
   - Show curl example
   - Answer: What should they send? (metadata flags)
   - Answer: What stays on their servers? (content/prompts)

5. **Q&A & Next Steps** (5 min)
   - "Any questions?"
   - "When do you plan to go live?"
   - "Any concerns about security/privacy?"
   - "Want weekly check-ins?"

**Post-Call:**
- [ ] Send call summary email with action items
- [ ] Schedule follow-up (1 week if they're integrating)

---

### Days 5-7: Testing Phase

**Customer Should Be Testing:**
- [ ] Ran curl examples successfully
- [ ] Created test API key
- [ ] Tested basic policy check
- [ ] Tested rate limiting (intentionally hit 100 req/60 sec)
- [ ] Verified block/allow responses work
- [ ] Reviewed audit logs in dashboard

**Our Checks:**
- [ ] Monitor their API usage (should see test requests)
- [ ] Verify logs appearing in dashboard
- [ ] No errors in Sentry
- [ ] Response times < 500ms p95

**If Testing Blocked:**
- [ ] Check for 401 errors (API key issue) → help regenerate
- [ ] Check for 429 errors (rate limited) → explain limits
- [ ] Check for all requests blocked (policy too strict) → suggest toggle off policy temporarily
- [ ] Check dashboard not loading → clear cache, try incognito mode

**If Tests Pass:**
- [ ] Schedule production deployment call
- [ ] Discuss monitoring/alerting strategy
- [ ] Discuss rollout plan (gradual vs immediate)

---

## Production Phase (Weeks 3-4)

### Pre-Production Checklist (1 week before go-live)

**Customer Confirmation:**
- [ ] Integration complete and tested
- [ ] Error handling implemented
- [ ] Monitoring/alerting set up (on their side)
- [ ] Rollout plan finalized
- [ ] Team trained on new flow

**Our Preparation:**
- [ ] Verified no issues in testing period
- [ ] Increased monitoring for customer in first week
- [ ] Alert thresholds tuned (know baseline)
- [ ] Support team briefed on customer use case
- [ ] On-call prepared for potential issues

**Customer Communications:**
- [ ] Sent go-live announcement
- [ ] Confirmed deployment date/time
- [ ] Shared rollback procedure (if needed)
- [ ] Provided emergency contact info
- [ ] Scheduled 24-hour monitoring call (day after go-live)

---

### Go-Live Day

**Before (2 hours before):**
- [ ] Verify everything still working
- [ ] Check metrics baseline (normal traffic patterns)
- [ ] Alert team in Slack (#alerts)
- [ ] Have on-call ready (first incident contact)

**During (deployment):**
- [ ] Customer deploys (we monitor)
- [ ] Check for errors in Sentry (watch closely)
- [ ] Monitor latency (any spikes?)
- [ ] Monitor error rate (should stay < 1%)
- [ ] Check rate limit hits (expected or suspicious?)

**After (first 24 hours):**
- [ ] Schedule daily check-in calls (or Slack updates)
- [ ] Monitor metrics every 2 hours
- [ ] Proactively reach out if any issues
- [ ] Collect feedback: "How's it going?"
- [ ] Celebrate! 🎉

**Checklist:**
- [ ] First request successfully processed
- [ ] Logs appearing in dashboard
- [ ] No errors > 1% of requests
- [ ] Latency p95 < 500ms
- [ ] Customer confirms policy decisions are correct

---

### Post-Launch Monitoring (Days 2-7)

**Daily:**
- [ ] Check Sentry for new errors
- [ ] Review Grafana dashboard (metrics normal?)
- [ ] Respond to any support requests same-day
- [ ] Customer touchpoint (email or Slack)

**Weekly (starting week 2 of production):**
- [ ] Review usage metrics (requests/day, errors/day)
- [ ] Analyze audit logs for patterns
- [ ] Collect feedback: Working as expected?
- [ ] Look for improvements (policy tweaks?)

**Monthly (starting month 2):**
- [ ] Full usage report (requests, blocks, latency)
- [ ] Feedback survey: satisfaction 1-10
- [ ] Feature requests documented
- [ ] Discuss: Ready to upgrade tier? (post-pilot)

---

## Issue Escalation

### If Customer Reports Issue

**Step 1: Triage (same day)**
- [ ] Ask for: Error message, timestamps, curl command
- [ ] Ask for: What were you trying to do?
- [ ] Severity: Is this blocking production?
- [ ] Impact: How many requests affected?

**Step 2: Investigate (within 24h)**
- [ ] Check Sentry for errors during timestamp
- [ ] Check Grafana metrics (spike or normal?)
- [ ] Check database logs (any queries failing?)
- [ ] Test API locally with their curl command
- [ ] Check customer's API key status (expired? revoked?)

**Step 3: Respond (within 24-48h)**
- [ ] Root cause identified
- [ ] Solution or workaround provided
- [ ] ETA if fix needed (if code change required)
- [ ] Offer troubleshooting call if needed

**Step 4: Follow-up (after fix)**
- [ ] Verify customer tested fix
- [ ] Ask if working now
- [ ] Document for knowledge base
- [ ] If pattern emerges: add to runbook

### If We Detect Issue (Before Customer Reports)

**Proactive Support:**
- [ ] Monitor Sentry - if error spike → email customer
- [ ] Monitor latency - if p95 > 1s → send status page update
- [ ] Monitor rate limits - if spike → ask what's happening
- [ ] Send email: "We noticed [issue]. Here's what we're doing."

**Example Email:**
```
Subject: Status Update - Latency Investigation

Hi [Customer Name],

We noticed higher latency for your requests today (p95 ~800ms).
This is above our usual targets (< 500ms).

What we're doing:
1. Investigating database query performance
2. Checking if there's a Redis bottleneck
3. Reviewing recent deployments

Next update: Within 2 hours
Status page: https://status.company.com

Will fix within 24 hours (likely sooner).
Sorry for the disruption!

[Support Team]
```

---

## Pilot Success Criteria

### Technical Metrics (Week 1-4)
- [ ] API uptime > 99.5%
- [ ] Response time p95 < 500ms (normal) or < 1s (peak)
- [ ] Error rate < 1%
- [ ] No data loss or corruption
- [ ] Backups working

### Customer Adoption
- [ ] Customer made first API call (Day 1)
- [ ] Customer created test API key (Day 2)
- [ ] Customer deployed to staging (Week 2)
- [ ] Customer deployed to production (Week 3-4)
- [ ] Customer actively using (> 100 requests/day)

### Customer Satisfaction
- [ ] Customer answered "platform works as expected" ✅
- [ ] Customer answered "security is good" ✅
- [ ] Customer answered "support is responsive" ✅
- [ ] Customer willing to provide case study ✅
- [ ] Customer willing to upgrade post-pilot ✅
- [ ] NPS score: [Target: 7+/10]

### Feedback Collected
- [ ] What's working well? (document)
- [ ] What could be better? (document)
- [ ] Feature requests? (prioritize for roadmap)
- [ ] Bugs found? (fix for GA)
- [ ] Documentation gaps? (update)

---

## End-of-Pilot Evaluation

### Week 12 (End of 6-Month Pilot)

**Customer Feedback Session (1 hour):**
- [ ] Usage review (total requests, patterns)
- [ ] What worked? What didn't?
- [ ] Would recommend to peers? (NPS)
- [ ] Want to upgrade to paid? (decision point)
- [ ] Can we use as case study?

**Our Decision:**
- [ ] Pilot successful? ✅ or ❌
- [ ] Known issues to fix before GA? (list)
- [ ] Customer upgraded? (yes/no)
- [ ] Case study approved? (yes/no)
- [ ] Lessons learned? (document)

---

## Customer Contact Log

| Date | Topic | Initiated By | Action | Status |
|------|-------|--------------|--------|--------|
| | | | | |
| | | | | |
| | | | | |

---

## Issues Log

| Date | Issue | Severity | Resolution | Status |
|------|-------|----------|-----------|--------|
| | | | | |
| | | | | |
| | | | | |

---

## Sign-Off

**Completed By:** [Your Name]  
**Date:** [Date]  
**Manager Approval:** [Name]

**Notes/Comments:**
```
[Space for notes]
```

---

**Next Step:** Print this checklist, assign to support person, start pre-onboarding!
