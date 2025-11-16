# Support & Operations Guide

**Version**: 1.0
**Last Updated**: November 16, 2025
**Status**: Ready for pilot phase

---

## Overview

This guide defines support channels, response times, escalation procedures, and operational workflows for AI Governance pilot customers.

---

## 1. Support Channels

### 1.1 Email Support (Primary Channel)

**Email**: support@company.com

**Response Time**: 24-48 hours

**For**:
- General questions about policies
- Feature requests
- Bug reports (non-critical)
- Billing inquiries
- Documentation clarifications

**How to Report a Bug**:

Send email to support@company.com with subject line:

```
Subject: [BUG] Short description of issue

Body:
What happened:
[Describe the issue clearly]

Expected behavior:
[What should have happened instead]

Steps to reproduce:
1. [First step]
2. [Second step]
3. [Third step]

Environment:
- Browser: [e.g., Chrome 120]
- OS: [e.g., macOS 14.1]
- Timestamp: [UTC time]
- API Key ID: [key_xxx...]

Logs/Screenshots:
[Paste error message or attach screenshot]
```

---

### 1.2 Slack/Discord (Pilot Phase - Real-Time)

**Channel**: #ai-governance-support (if invited)

**Response Time**: Real-time (during business hours: Mon-Fri, 9 AM - 6 PM UTC)

**For**:
- Urgent issues (dashboard not loading, API errors)
- Live debugging with support team
- Feature questions
- Walkthroughs and demos

**How to Request Slack Access**:

Email support@company.com:
```
Subject: Request Slack access for [COMPANY NAME]

I'd like to join the #ai-governance-support channel for real-time support.

Contact: [Your name]
Email: [Your email]
Phone: [Your phone]
Company: [Your company]
```

---

### 1.3 Status Page (24/7 Incident Notifications)

**URL**: https://status.company.com (or Uptime Robot page)

**For**:
- Real-time uptime status
- Incident notifications
- Maintenance windows
- Post-incident reports

**Subscribe** to status page for email/SMS alerts:
1. Visit https://status.company.com
2. Click "Subscribe to updates"
3. Enter email address
4. Select notification preferences

---

### 1.4 On-Call (Production - Critical Only)

**Phone**: +1-XXX-XXX-XXXX (24/7 for critical incidents)

**When to Use**:
- API completely down (> 15 minutes)
- Data loss or corruption
- Security breach suspected
- Rate limiting not working

**How to Escalate**:
1. Email support@company.com: "CRITICAL: [Issue]"
2. Call on-call number
3. Reference email subject line
4. Describe severity and impact

---

## 2. Response Time SLAs (Pilot Phase)

| Severity | Description | Response Time | Resolution Time |
|----------|-------------|---------------|-----------------|
| **Critical** | API down, data loss, security breach | 1 hour | Best effort |
| **High** | Dashboard not working, rate limit broken | 4 hours | 24 hours |
| **Medium** | Feature not working as expected | 12 hours | 3 days |
| **Low** | Feature request, documentation question | 48 hours | N/A |

**Note**: During pilot phase, response times are "best effort". SLA credits begin post-pilot.

---

## 3. Ticket Triage & Routing

### 3.1 Intake Process

**Step 1**: Email received at support@company.com

**Step 2**: Auto-reply sent within 1 hour
```
Thanks for contacting AI Governance support!

We received your email and assigned ticket #XXX.

We'll respond with next steps within 24-48 hours.

Ticket: https://support.company.com/tickets/XXX
Status: Open
Category: [Auto-detected category]
```

**Step 3**: Support team reviews and assigns
- Categorize (Bug, Feature, Question, Billing)
- Assign severity (Critical, High, Medium, Low)
- Assign to support engineer
- Set response deadline

---

### 3.2 Categorization

| Category | Examples | Typical Resolution |
|----------|----------|-------------------|
| **Bug** | Dashboard crashes, API 500 errors, policy not evaluating | Fix code, deploy, notify customer |
| **Feature Request** | "Can we add IP whitelisting?" | Log for product roadmap |
| **Question** | "How do I create a policy?", "Why was my request blocked?" | Answer in email or video |
| **Billing** | "Why am I charged?", "Can I upgrade?" | Update account, send invoice |
| **Feedback** | "Your dashboard is confusing", "Love the metrics!" | Log for UX improvements |

---

### 3.3 Severity Assignment

**Critical** (Escalate immediately):
- Production API returning 500 errors
- Database connection failing
- Rate limiting broken (all customers blocked)
- Data loss suspected
- Security breach

**High** (Resolve within 24 hours):
- Dashboard showing wrong data
- API slow (p95 > 1000ms)
- Specific customer API key not working
- Policy not evaluating correctly
- Rate limit hitting false positives

**Medium** (Resolve within 3 days):
- Minor UI bug (typo, layout issue)
- Feature working but slower than expected
- Policy question or clarification needed
- Feature request

**Low** (Resolve within 1 week):
- Documentation typo
- Feature request (nice-to-have)
- General inquiry
- Feedback or suggestions

---

## 4. Common Issues & Resolutions

### Issue 1: "Dashboard not loading"

**Diagnosis**:
1. Check status page for outages
2. Ask customer for error message/screenshot
3. Check if API key is correct
4. Try in incognito mode (clear cookies)

**Resolutions**:
- [ ] Browser cache cleared
- [ ] Try different browser
- [ ] Verify API key in NEXT_PUBLIC_ADMIN_KEY environment variable
- [ ] Backend API responding (curl https://api.domain.com/health)
- [ ] CORS configured for dashboard domain

**If still broken**:
→ Escalate to engineering (likely backend issue)

---

### Issue 2: "API key not working"

**Diagnosis**:
1. Verify key_id format (should be UUID)
2. Check key is not expired/deleted
3. Verify Authorization header format: `Bearer key_id.secret`
4. Check if rate limited (429 status)

**Resolutions**:
- [ ] Regenerate API key: `python scripts/generate_api_key.py`
- [ ] Update in dashboard: Keys → Create New
- [ ] Add 5 minute delay (DB replication)
- [ ] Verify curl request format:
  ```bash
  curl -H "Authorization: Bearer YOUR_KEY_ID.SECRET" \
       https://api.domain.com/v1/check
  ```

**If still broken**:
→ Check backend logs in Render dashboard

---

### Issue 3: "Rate limiting too strict"

**Diagnosis**:
1. Customer hitting 100 req/60 sec limit
2. Check actual request rate
3. Ask if burst traffic expected

**Options**:
- [ ] Increase rate limit (update rate_limit.py)
- [ ] Implement request queuing on customer side
- [ ] Deploy multiple API keys (distribute across keys)
- [ ] Batch requests on customer's backend

**For production customers**:
- Custom rate limits per key (post-pilot feature)

---

### Issue 4: "Policy blocking legitimate requests"

**Diagnosis**:
1. Ask what request was blocked
2. Check policy configuration
3. Review risk score (in audit logs)

**Common Causes**:
- Policy set too strict (toggle off temporarily to test)
- False positive in risk detection
- Legitimate field name triggering filter (e.g., "prompt" field)

**Resolution**:
- Review policy settings with customer
- Adjust if needed
- Test with sample requests
- Document decision

---

### Issue 5: "Can't see audit logs"

**Diagnosis**:
1. Verify admin API key is correct
2. Check /api/admin/logs endpoint
3. Verify CORS configured
4. Check date range (logs only retained 90 days)

**Resolutions**:
```bash
# Test API endpoint directly
curl -H "Authorization: Bearer YOUR_ADMIN_KEY" \
     https://api.domain.com/api/admin/logs

# Specify date range if needed
curl -H "Authorization: Bearer YOUR_ADMIN_KEY" \
     https://api.domain.com/api/admin/logs?page=1&page_size=50
```

**If returning 401**:
→ Admin API key incorrect (regenerate if needed)

**If returning 403**:
→ API key not marked as admin (update in database)

---

## 5. Escalation Path

### Level 1: Support Engineer (You Read This First)

- Respond to customer within 24 hours
- Troubleshoot using guides above
- Gather logs and error messages
- Document resolution steps

**Escalation Criteria**:
- Cannot reproduce issue
- Need database access
- Suspected code bug
- Security concern

**Action**: Create internal ticket, tag @engineering

---

### Level 2: Engineering Team

**When to Escalate**:
- API returning 500 errors (not customer error)
- Policy evaluation producing wrong results
- Database connection issues
- Redis not responding
- Sentry showing new errors

**Info to Provide**:
```
Customer: [Company name]
Issue: [One-line summary]
Severity: [Critical/High/Medium/Low]
Ticket: #XXX

Reproduction Steps:
1. [Step]
2. [Step]

Expected: [What should happen]
Actual: [What happens instead]

Logs:
- Backend logs: [URL to Render logs]
- Sentry errors: [Link to Sentry issue]
- Customer curl request: [Exact command]
```

---

### Level 3: On-Call (Critical Only)

**When to Escalate**:
- API down for > 15 minutes
- Data loss or corruption
- Security breach
- Major component failure

**How to Contact**:
1. Call +1-XXX-XXX-XXCK
2. Provide: Severity, impact, reproducibility
3. Prepare logs and commands to run
4. Stay on call for coordination

**Expected Response**: 1 hour

---

## 6. Communication Templates

### Template 1: Initial Response (Bug Report)

```
Subject: RE: [BUG] Your dashboard issue - Ticket #XXX

Hi [Customer Name],

Thanks for reporting this! I've received your ticket and started investigating.

Summary:
- Issue: [One-line summary of their problem]
- Severity: [Medium/High/Critical]
- Current Status: Investigating

Next Steps:
1. I'll reproduce the issue locally
2. Check our logs (Sentry and backend)
3. Provide update within 24 hours

If you have additional info (screenshots, timestamps), please reply to this email.

Best,
[Your Name]
Support Team
support@company.com
```

---

### Template 2: Found Root Cause

```
Subject: RE: [BUG] Your dashboard issue - Found cause - Ticket #XXX

Hi [Customer Name],

I found the issue! Here's what happened:

Root Cause:
[Explain what went wrong clearly]

Why It Happened:
[2-3 sentences explaining the reason]

Fix:
- [Already deployed / Will deploy in X hours / Workaround: ...]

Your Action (if needed):
[What the customer needs to do]

We apologize for the inconvenience. If you have questions, let me know.

Best,
[Your Name]
Support Team
```

---

### Template 3: Unable to Reproduce

```
Subject: RE: [BUG] Your dashboard issue - Need more info - Ticket #XXX

Hi [Customer Name],

I've tried to reproduce the issue but couldn't get the same result.

To help me debug, can you provide:
1. Exact browser/OS (e.g., "Chrome 120 on macOS 14.1")
2. Screenshot of the error (if any)
3. Timestamp (UTC) when it occurred
4. Steps to reproduce (very detailed)

Once I have this info, I can dig deeper.

Thanks!
[Your Name]
Support Team
```

---

### Template 4: Resolution Confirmation

```
Subject: RE: [BUG] Your dashboard issue - RESOLVED - Ticket #XXX

Hi [Customer Name],

Good news! I've deployed the fix and verified it works.

What Changed:
[Describe the fix]

How to Verify:
[Steps for customer to confirm fix]

Please let me know if the issue is resolved on your end. If you run into anything else, just reply to this ticket.

Best,
[Your Name]
Support Team
```

---

### Template 5: Feature Request Response

```
Subject: RE: Feature request - [Feature name] - Ticket #XXX

Hi [Customer Name],

Thanks for the suggestion! [Feature request] is great feedback.

Current Status:
- Priority: [High/Medium/Low]
- Timeline: [Q1 2026 / Post-pilot / Backlog]

We're tracking this in our product roadmap. I've marked your vote for this feature, which helps prioritization.

Would you be open to a brief call to discuss this in more detail?

Best,
[Your Name]
Support Team
```

---

## 7. Knowledge Base (Self-Service)

### Documentation to Create

**For Customers** (publish on website):
- [ ] FAQ: Common questions about policies, API keys, rate limiting
- [ ] Quickstart: Get your first API key in 5 minutes
- [ ] Policy guide: How to configure policies (by type)
- [ ] Troubleshooting: Common errors and solutions
- [ ] Dashboard guide: How to use the admin dashboard (link to frontend/DASHBOARD_README.md)

**For Support Team** (internal):
- [ ] Runbook: Step-by-step procedures for common issues
- [ ] Debugging guide: How to read logs, use Sentry, check metrics
- [ ] Escalation guide: When and how to escalate (this document)
- [ ] Database guide: Common SQL queries for support
- [ ] Deployment guide: How to push an urgent fix

---

## 8. Incident Response

### Critical Incident Playbook

**Step 1: Confirm Incident** (Immediately)
```
Check:
- [ ] API /health endpoint responding
- [ ] Dashboard loading
- [ ] Sentry showing errors
- [ ] Grafana showing metrics
- [ ] Calculate impact (how many customers affected)
```

**Step 2: Notify Stakeholders** (Within 15 minutes)
```
To: #incidents Slack channel
Subject: INCIDENT: [Component] down - Severity [Critical/High]

Timeline:
- 14:30 UTC: Customer reported 500 errors
- 14:35 UTC: Confirmed API down
- Impact: 3 customers, ~2% of requests failing

Current Status: Investigating
Next Update: 15:05 UTC (every 15 min during incident)
```

**Step 3: Investigate Root Cause** (Parallel)
```
Check these immediately:
- [ ] Render backend logs (any error messages?)
- [ ] Database connection (can backend reach Postgres?)
- [ ] Redis connection (can backend reach Redis?)
- [ ] Recent deployments (anything deployed in last hour?)
- [ ] Disk space (Render disk full?)
- [ ] Memory (consuming too much RAM?)
```

**Step 4: Implement Fix** (Depends on cause)
```
If database down:
  → Check Neon dashboard, restart if needed
  
If Redis down:
  → Check RedisCloud, scale if needed
  
If backend code bug:
  → Revert last deployment or apply hotfix
  → Test locally first
  → Deploy to production
  
If rate limiting too aggressive:
  → Temporarily increase limit or disable
  → Test before rolling back
```

**Step 5: Communication** (Every 15 minutes)
```
Update stakeholders on:
- Progress so far
- Next steps
- Expected resolution time
- Any customer action needed
```

**Step 6: Recovery** (Once fixed)
```
1. Verify API responding normally
2. Run quick smoke tests (curl API, load dashboard)
3. Monitor metrics for 30 minutes
4. When stable → Send all-clear message

All-Clear Message:
  ✅ Issue: [What happened]
  ✅ Root Cause: [Why it happened]
  ✅ Fix: [What we did]
  ✅ Status: Fully recovered, monitoring
  ✅ Post-mortem: [Link to incident review]
  ✅ Impact: [15 min downtime, X customers affected]
```

**Step 7: Post-Incident Review** (Within 24 hours)
```
Document:
- [ ] What happened and when
- [ ] Impact (customers, revenue, data)
- [ ] Root cause analysis
- [ ] How to prevent in future
- [ ] Action items (code changes, alerting, runbooks)
- [ ] Lessons learned
- [ ] Apology/explanation to customers

Share with:
- Engineering team (prevent recurrence)
- Product team (prioritize fixes)
- Customers (transparency)
```

---

## 9. Monitoring & Health Checks

### Daily Checklist (Start of shift)

```
□ Check status page (any open incidents)
□ Review Sentry (new error counts)
□ Check Grafana dashboard (metrics normal?)
□ Review Slack #alerts channel (any alerts overnight?)
□ Skim support email (new critical issues?)
□ Verify API health: curl https://api.domain.com/health
□ Verify dashboard: open https://dashboard.domain.com
```

### Weekly Checklist (Friday before EOD)

```
□ Review all open support tickets (any stale?)
□ Check backup status (Neon snapshots created)
□ Review metrics trends (any degradation?)
□ Check security alerts (anything suspicious?)
□ Prepare incident summary (if any occurred)
□ Schedule on-call for next week
```

### Monthly Checklist

```
□ Security audit (pip-audit, npm audit)
□ Dependency updates available (check for patches)
□ Database size check (growing too fast?)
□ Backup test (restore to test DB and verify)
□ SLA review (how many 99.5% uptime incidents?)
□ Customer satisfaction check-in (brief surveys)
□ Runbook update (any new procedures?)
```

---

## 10. Pilot Phase Specifics

### Pilot Support Differences

| Aspect | Pilot | Production |
|--------|-------|-----------|
| **Response Time** | 24-48 hours best-effort | Guaranteed SLA |
| **Uptime Target** | 99.5% best-effort | 99.9% guaranteed |
| **On-Call** | Email/Slack only | 24/7 phone on-call |
| **Features** | May change | Backward compatible |
| **Pricing** | Free | Paid tiers |
| **Support** | Email + Slack (if invited) | Email + phone + chat |

### Feedback Collection

**Goal**: Gather feedback to improve product

**How**:
- Weekly Slack check-in: "Any feedback this week?"
- Monthly survey: 5 questions about satisfaction
- Quarterly review: Deeper conversation about roadmap

**Questions to Ask**:
1. Is the dashboard easy to use? (1-5 scale)
2. Are policies working as expected? (Yes/No)
3. What's missing or could be better?
4. Would you upgrade to paid post-pilot? (Yes/No)
5. Can we use your feedback in case study? (Yes/No)

---

## Contacts

### Internal

| Role | Name | Email | Phone |
|------|------|-------|-------|
| Support Lead | [Name] | [Email] | [Phone] |
| Engineering Lead | [Name] | [Email] | [Phone] |
| On-Call | [Rotation] | [Email] | [Phone] |

### External

| Channel | Contact | Hours |
|---------|---------|-------|
| Support Email | support@company.com | 24/7 (responded 24-48h) |
| Slack | #ai-governance-support | Mon-Fri 9am-6pm UTC |
| Status Page | https://status.company.com | 24/7 (automated) |
| On-Call (Critical) | +1-XXX-XXX-XXXX | 24/7 |

---

**END OF SUPPORT & OPERATIONS GUIDE**

**Next Steps**:
1. Share this document with support team
2. Update template placeholders (names, phone, email)
3. Create Slack channel (#ai-governance-support) for pilot customers
4. Set up support email inbox + ticketing system
5. Share FAQ/documentation links with first pilot customer
