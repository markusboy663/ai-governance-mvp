# AI Governance - Pilot Customer Integration Guide

**Quick Start for [CUSTOMER NAME]**

---

## 🚀 Getting Started (5 minutes)

### 1. Your API Key
```
Key ID:     key_xxxxx...
Secret:     (stored securely, never log this)
Status:     ✅ Active
Created:    [Date]
```

### 2. Test the Integration

**Basic Policy Check:**
```bash
curl -X POST https://api.yourdomain.com/v1/check \
  -H "Authorization: Bearer key_xxxxx....(your_key_id).your_secret" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "operation": "classify",
    "metadata": {
      "intent": "spam_detection",
      "is_external_model": false
    }
  }'
```

**Expected Response (Allowed):**
```json
{
  "allowed": true,
  "risk_score": 0,
  "reason": "ok"
}
```

**Expected Response (Blocked):**
```json
{
  "allowed": false,
  "risk_score": 70,
  "reason": "contains_personal_data"
}
```

---

### 3. Dashboard Access

**URL:** https://dashboard.yourdomain.com

**Admin Key:** [provided separately]

**What you can do:**
- ✅ View all API keys and request counts
- ✅ Create new API keys
- ✅ Toggle governance policies (on/off)
- ✅ View audit logs (last 90 days)
- ✅ Rotate or delete keys

---

## ⚠️ Security Memo

### CRITICAL: Never Send Raw Prompts

**❌ DO NOT DO THIS:**
```bash
# WRONG - Contains prompt in request
curl -X POST https://api.yourdomain.com/v1/check \
  -d '{
    "model": "gpt-4",
    "prompt": "Who is John Doe? 123-45-6789"  # ❌ DANGER: Personal data exposed
  }'
```

**✅ DO THIS INSTEAD:**
```bash
# RIGHT - Use metadata only, never send content
curl -X POST https://api.yourdomain.com/v1/check \
  -d '{
    "model": "gpt-4",
    "operation": "classify",
    "metadata": {
      "contains_personal_data": false,  # Let US evaluate this
      "is_external_model": false
    }
  }'
```

### How It Works
1. **You** evaluate your content locally (is there PII? external model?)
2. **You** send metadata flags (true/false) to our API
3. **We** evaluate against policies
4. **We** return allow/block decision
5. **Content stays on your systems** (we never see it)

### Forbidden Fields
These fields are **blocked** at API layer (never logged):
```
prompt, text, input, message, messages, content,
request_body, response_body, user_data, sensitive_info
```

If you accidentally send these, they're automatically redacted.

---

## 🔄 Key Rotation (Every 90 days)

### Online (via Dashboard)
1. Go to https://dashboard.yourdomain.com → Keys
2. Find the key to rotate
3. Click "⟳ Rotate" button
4. New key generated, old key invalidated
5. Update your application with new key
6. Test with new key before deleting old one

### Command Line
```bash
# Generate new key
curl -X POST https://api.yourdomain.com/api/admin/keys/KEY_ID/rotate \
  -H "Authorization: Bearer admin_key"

# Response: New key_id.secret (save this!)
```

### ✅ Rotation Checklist
- [ ] Note old key ID
- [ ] Generate new key
- [ ] Update in your application
- [ ] Test API calls work
- [ ] Wait 5 minutes (allow DNS cache to clear)
- [ ] Delete old key (or mark deprecated)

---

## 📞 Support & SLAs

### Contact Methods

| Channel | Response Time | For |
|---------|---------------|-----|
| **Email** | 24-48 hours | General questions, bugs |
| **Slack** | Real-time (business hours) | Urgent issues (pilots only) |
| **Status Page** | Real-time | System outages |
| **On-Call** | 1 hour | Critical (API down > 15 min) |

### Support Email
```
support@company.com
```

### Slack Channel
```
#ai-governance-support (invite required)
```

### On-Call (Critical Only)
```
+1-XXX-XXX-XXXX
Use ONLY if API completely down + urgent
```

### Status Page
```
https://status.company.com
Subscribe for real-time outage alerts
```

---

## 📋 SLA Guarantees (Pilot Phase)

| Severity | Description | Response | Resolution |
|----------|-------------|----------|-----------|
| **Critical** 🔴 | API down, data loss, security | 1 hour | Best effort |
| **High** 🟠 | Feature broken, policy wrong | 4 hours | 24 hours |
| **Medium** 🟡 | Minor bug, slow response | 12 hours | 3 days |
| **Low** 🟢 | Question, feature request | 48 hours | N/A |

**Important:** During pilot phase, these are **best-effort targets** (not guaranteed SLAs). Production tier gets guaranteed SLAs post-pilot.

---

## 🔐 Common Issues & Fixes

### "API returns 401 Unauthorized"
**Problem:** API key missing or incorrect

**Fix:**
```bash
# Check header format: Bearer KEY_ID.SECRET
curl -X POST https://api.yourdomain.com/v1/check \
  -H "Authorization: Bearer YOUR_KEY_ID.YOUR_SECRET"  # ✅ Format: KEY_ID.SECRET
```

**Verify:**
- Copy key from dashboard exactly (no extra spaces)
- Key format is `key_xxxxx.secret_yyyyy`
- Using full key (both parts after "Bearer ")

---

### "All requests blocked with risk_score > 50"
**Problem:** Policy too strict

**Fix:**
1. Go to Dashboard → Policies
2. Review which policy is triggering blocks
3. Check metadata you're sending (e.g., `contains_personal_data: true`)
4. For testing: Toggle policy off temporarily
5. Message us if you think it's a false positive

---

### "Rate limit exceeded (429 error)"
**Problem:** More than 100 requests per 60 seconds

**Response header shows:**
```
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
```

**Fix:**
- Wait 60 seconds, then retry
- Implement exponential backoff (wait 1s, 2s, 4s...)
- Or contact us to increase limit: support@company.com

---

### "Dashboard shows blank screen"
**Problem:** Browser cache or CORS issue

**Fix:**
1. Try incognito/private mode
2. Clear browser cache (Ctrl+Shift+Del)
3. Check admin key in environment
4. Try different browser
5. If still broken, email support@company.com

---

## 📊 Monitoring Your Usage

### Dashboard Metrics
1. **Keys Page:** Total requests per key
2. **Policies Page:** Violations per policy (last 7 days)
3. **Logs Page:** Full audit trail (paginated, filterable)

### Example Queries
```bash
# Get all logs for today
curl https://api.yourdomain.com/api/admin/logs?page=1 \
  -H "Authorization: Bearer admin_key"

# Filter by policy violation
curl https://api.yourdomain.com/api/admin/logs?operation=blocked \
  -H "Authorization: Bearer admin_key"

# Filter by model
curl https://api.yourdomain.com/api/admin/logs?model=gpt-4 \
  -H "Authorization: Bearer admin_key"
```

---

## 🛟 Incident Reporting

### Security Breach Suspected
**Immediately email:** security@company.com

**Include:**
- What happened (in plain English)
- When it happened (timestamp)
- Affected API key ID
- Your company name + contact

**Response:** Within 24 hours

---

### API Integration Bug
**Email:** support@company.com

**Include:**
- What you were trying to do
- Error message (exact text)
- Request you sent (sanitized, no secrets)
- Expected vs actual response
- Your API key ID (we'll look up logs)

**Response:** Within 24-48 hours

---

## 📅 Pilot Program Details

### Duration
- **Start:** [Date]
- **Duration:** 6 months (or until feedback collected)
- **Free Cost:** No charges during pilot

### What Happens After Pilot
1. **Evaluation:** We review usage patterns + feedback
2. **Pricing Decision:** Choose tier (Free/Pro/Enterprise)
3. **Production Launch:** Move to paid tier with guaranteed SLA
4. **Support Upgrade:** Move from Slack to email/phone/on-call

### Pricing Post-Pilot (Estimate)
| Tier | Requests/Month | Price | Best For |
|------|----------------|-------|----------|
| Free | 10,000 | $0 | Testing, small teams |
| Pro | Unlimited | $49/month | Production use |
| Enterprise | Unlimited | Custom | Large deployments |

---

## 📞 Key Contacts

### Technical Support
```
Email:  support@company.com
Slack:  #ai-governance-support
Status: https://status.company.com
```

### Security Issues
```
Email:   security@company.com
Phone:   +1-XXX-XXX-XXCK (on-call for critical)
Hours:   24/7
```

### Commercial / Account Questions
```
Email:   sales@company.com
Hours:   Mon-Fri, 9am-6pm UTC
```

### Feedback / Feature Requests
```
Email:   product@company.com
Form:    https://company.com/feedback
```

---

## ✅ Pre-Integration Checklist

Before going to production:

- [ ] **Testing**
  - [ ] Created test API key
  - [ ] Ran curl examples (confirmed allow/block)
  - [ ] Tested with your actual models
  - [ ] Verified rate limiting works

- [ ] **Security**
  - [ ] Never sending prompts in requests (metadata only)
  - [ ] API key stored securely (env var, not hardcoded)
  - [ ] HTTPS enforced (no HTTP)
  - [ ] Authorization header in all requests

- [ ] **Monitoring**
  - [ ] Dashboard access verified
  - [ ] Can view API keys and logs
  - [ ] Subscribed to status page
  - [ ] Added support email to contacts

- [ ] **Setup**
  - [ ] Key rotation procedure documented (for team)
  - [ ] SLA expectations understood (24-48h response)
  - [ ] Escalation contacts saved
  - [ ] Have schedule of production deployment

---

## 🎓 Next Steps

1. **This Week:** Test integration (run curl examples above)
2. **Next Week:** Configure policies (toggle on/off in dashboard)
3. **Week 3:** Deploy to production (with monitoring)
4. **Ongoing:** Weekly check-in calls with our team

### 30-Minute Kickoff Call

**Agenda:**
1. Platform overview (10 min)
2. Your use case walkthrough (10 min)
3. Q&A + next steps (10 min)

**When?** [Schedule link]

---

## Legal & Terms

- **Privacy:** We store metadata only (never prompts/content)
- **Retention:** Logs kept 90 days, then auto-deleted
- **DPA:** Data Processing Agreement [link]
- **Terms:** Terms of Service [link]
- **Support:** Best-effort during pilot phase

---

**Questions?** Reply to this email or Slack #ai-governance-support 💬

**Welcome to the pilot!** 🚀
