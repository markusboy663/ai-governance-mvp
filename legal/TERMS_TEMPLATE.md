# Terms of Service - Template

**Effective Date**: [DATE]
**Version**: 1.0

---

## 1. Service Description

### 1.1 What is AI Governance?

AI Governance is a governance platform that enforces policies on AI operations. The platform:

- **Evaluates** every AI request in real-time against configurable policies
- **Blocks** requests that violate policy (e.g., personal data detection, unauthorized models)
- **Logs** all decisions for audit trails (metadata only, never content)
- **Rates limits** requests to prevent abuse (100 requests per 60 seconds per API key)

### 1.2 Pilot Phase

**Important**: This service is in **pilot phase** for early customers. 

**What this means**:
- Service is provided "as-is" with no uptime guarantee (though we target 99.5%)
- Features may change during the pilot phase
- We actively gather feedback for improvements
- Support is provided on a best-effort basis

### 1.3 Service Levels (SLA)

During pilot phase:

| Metric | Target | Status |
|--------|--------|--------|
| **Availability** | 99.5% (< 3.6 hours downtime/month) | Best effort |
| **API Latency** | p95 < 500ms | Best effort |
| **Error Rate** | < 1% of requests | Best effort |
| **Recovery Time** | < 1 hour (critical incidents) | Best effort |

**No SLA credits** are issued during pilot phase. Credits begin post-pilot (if moving to production).

---

## 2. Acceptable Use Policy

### 2.1 You MUST NOT Use the Service To:

- **Harassment or Abuse**: Send threats, harassment, or abusive content
- **Malicious Testing**: Conduct security testing without explicit written permission
- **Data Exfiltration**: Attempt to extract other customers' data or logs
- **Denial of Service**: Flood the API with requests beyond rate limits to disrupt service
- **Reverse Engineering**: Attempt to reverse engineer the policy evaluation logic
- **Resale**: Re-sell or redistribute the service to third parties without authorization

### 2.2 Violation Consequences

Violation of this policy may result in:
- Immediate API key revocation
- Termination of service without refund
- Legal action if applicable
- Reporting to law enforcement (for criminal activity)

---

## 3. Limitations of Liability

### 3.1 Disclaimers

**THE SERVICE IS PROVIDED "AS-IS" WITHOUT ANY WARRANTIES**, EXPRESS OR IMPLIED, INCLUDING:

- No warranty of **availability** (we target 99.5% but do not guarantee it)
- No warranty of **accuracy** (policy evaluations may have false positives/negatives)
- No warranty of **fitness for particular purpose** (you choose to use it, not us)
- No warranty of **data protection** (encryption in place but no 100% guarantee)

### 3.2 Liability Cap

**MAXIMUM LIABILITY**: Refund of fees paid for the service during the preceding month.

**NO LIABILITY FOR**:
- Lost profits
- Lost data or logs
- Business interruption
- Indirect or consequential damages
- Reputational harm
- Third-party claims

### 3.3 Exception

The above disclaimers do not limit liability for:
- Data breaches caused by Processor's gross negligence
- Violations of applicable law (GDPR, CCPA, etc.)
- Indemnification obligations

---

## 4. Termination

### 4.1 Termination by Either Party

**Either you or we can terminate this service for any reason with 30 days' written notice.**

### 4.2 Termination Effective Immediately

We may terminate immediately (without 30 days' notice) if you:
- Violate the Acceptable Use Policy
- Fail to pay invoices (if applicable)
- Pose a security risk to the platform

### 4.3 Upon Termination

1. You stop sending requests to our API
2. We stop processing your data
3. **Your API keys are revoked immediately**
4. Audit logs deleted after 90 days (or immediately if requested)
5. Backups retained for 14 days, then deleted
6. Final data deletion confirmation within 10 days

### 4.4 Fees

During pilot phase: **No fees** (free to use)

Post-pilot (if transitioning to production):
- Fees accrued until effective termination date
- Fees are **non-refundable** for pilot users

---

## 5. Privacy & Data Protection

### 5.1 What Data We Collect

We collect and store **metadata only**:
- API request timestamps
- Model name (e.g., "gpt-4")
- Operation type (e.g., "classify")
- Risk score (0-100)
- Decision (allowed/blocked)
- Reason (why blocked, if applicable)
- Latency in milliseconds

### 5.2 What Data We DO NOT Collect

We **explicitly do not store**:
- User prompts or inputs
- AI model outputs or responses
- Personal data (PII) in requests
- Your proprietary data or secrets
- Full request/response bodies

**How this works**: Fields like `prompt`, `text`, `input`, `content` are blocked at the API layer and never logged.

### 5.3 Data Retention

- **Audit logs**: 90 days (auto-purged weekly)
- **API key records**: Until deletion
- **Error logs** (Sentry): 30 days
- **Backups**: 14 days (encrypted, then deleted)

### 5.4 GDPR Compliance

If you're subject to GDPR (processing EU residents' data):

- **DPA Required**: You must sign our Data Processing Agreement
- **Data Subject Rights**: You can request access, deletion, portability
- **Sub-processors**: We use Neon (DB), Render (hosting), Sentry (errors) - all GDPR compliant
- **Data Transfers**: Data may be stored in US, processed in EU/US

**To request DPA**: Contact legal@yourcompany.com

---

## 6. Payment & Billing (Post-Pilot)

### 6.1 Pricing Model

**During Pilot**: FREE

**Post-Pilot Options** (TBD based on pilot feedback):

| Tier | Requests/Month | Price | Best For |
|------|----------------|-------|----------|
| **Free** | 10,000 | Free | Testing, small teams |
| **Pro** | Unlimited | $49/month | Production use |
| **Enterprise** | Unlimited | Custom | Large-scale deployments |

### 6.2 Billing Cycle

- Monthly billing (charged on 1st of month)
- Auto-renewal unless cancelled 30 days before renewal
- Invoices emailed in PDF format
- Payment methods: Credit card, ACH (if enterprise)

### 6.3 Non-Refundable

**Pilot users**: Free to use, no refunds applicable
**Paid users** (post-pilot): Fees are non-refundable. Unused services in a month are non-refundable.

---

## 7. Support & Contact

### 7.1 Support Channels

| Channel | Response Time | For |
|---------|---------------|-----|
| **Email** | 24-48 hours | General questions, feature requests |
| **Slack** | Real-time (pilot phase) | Urgent issues (pilot only) |
| **Status Page** | Real-time | Incident notifications |
| **On-Call** | 1 hour | Critical outages (production only) |

**Support Email**: support@company.com
**On-Call (Production)**: +1-XXX-XXX-XXXX

### 7.2 What Support Covers

- ✅ Technical troubleshooting
- ✅ API documentation clarifications
- ✅ Dashboard access issues
- ✅ Feature questions

**What support does NOT cover**:
- ✗ Custom development (use professional services)
- ✗ Integration into your architecture (your responsibility)
- ✗ Policy configuration advice (you define policies)

---

## 8. Intellectual Property

### 8.1 Your Content

**You retain all rights** to:
- API keys and secrets (manage them carefully)
- Policies you configure
- Audit logs generated by your requests

### 8.2 Our Content

We retain all rights to:
- The platform code and architecture
- Documentation
- Trademarks and logos
- Improvements and feedback

**You cannot**:
- Copy or reverse-engineer our code
- Claim ownership of the platform
- Re-distribute the service

---

## 9. Indemnification

### 9.1 Your Indemnification

You indemnify and hold us harmless from:
- Claims by your customers that your use of the platform is improper
- Violation of your own privacy policies
- Breach of applicable law (GDPR, CCPA, etc.)
- Unauthorized use of API keys

### 9.2 Our Indemnification

We indemnify and hold you harmless from:
- Infringement claims related to the platform
- Violations of data protection law (if we breach the DPA)
- Claims related to our platform infrastructure

---

## 10. Changes to Terms

### 10.1 Right to Change

**We may change these terms at any time with 30 days' notice.**

**How we notify you**:
- Email to primary contact
- In-app notification
- Blog post
- Email newsletter

### 10.2 Continued Use = Acceptance

If you continue using the service after 30 days, you accept the new terms.

**If you don't accept**: Terminate the service (you have 30 days to do so)

---

## 11. Governing Law & Dispute Resolution

### 11.1 Governing Law

These terms are governed by the laws of **[STATE/COUNTRY]**, without regard to conflict of law provisions.

### 11.2 Dispute Resolution

**Before litigation**, both parties agree to:
1. Good faith negotiation (30 days)
2. Mediation (30 days, if negotiation fails)
3. Binding arbitration (if mediation fails)

**Arbitration Details**:
- Location: [CITY, STATE]
- Arbitrator: Single neutral arbitrator
- Cost: Split equally
- Confidential proceedings

### 11.3 Exceptions to Arbitration

Either party may seek injunctive relief in court for:
- Breach of Acceptable Use Policy
- Intellectual property infringement
- Confidential information misuse

---

## 12. Entire Agreement

These Terms of Service, together with the Data Processing Agreement (if applicable), constitute the entire agreement between you and us.

**Prior agreements**: Any prior agreements, proposals, or understandings are superseded by these terms.

---

## 13. Severability

If any provision of these terms is found invalid or unenforceable:
- That provision is severed
- Remaining provisions remain in full force
- The invalid provision is enforced to the maximum extent allowed by law

---

## 14. Contact

### 14.1 For Support

```
support@company.com
Response: 24-48 hours
```

### 14.2 For Legal Issues

```
legal@company.com
Response: 5 business days
```

### 14.3 For Security/Breach Reports

```
security@company.com
Response: 24 hours (24/7)
Phone: +1-XXX-XXX-XXXX
```

### 14.4 For DPA or Contract Issues

```
contracts@company.com
Response: 3 business days
```

---

## Acknowledgments

**You acknowledge that**:
- ✅ You have read and understand these terms
- ✅ You agree to be bound by these terms
- ✅ You have the authority to enter into this agreement
- ✅ You will use the service only for lawful purposes
- ✅ You understand the pilot phase limitations

---

**END OF TERMS OF SERVICE TEMPLATE**

**Note to Company Legal**: This template must be reviewed and customized by your legal team before publishing. Replace `[DATE]`, `[STATE/COUNTRY]`, `[CITY, STATE]`, and contact information with actual values.

**Customization Checklist**:
- [ ] Replace [DATE] with effective date
- [ ] Replace [STATE/COUNTRY] with your jurisdiction
- [ ] Replace [CITY, STATE] with arbitration location
- [ ] Replace support@company.com with your support email
- [ ] Replace legal@company.com with your legal email
- [ ] Replace security@company.com with your security email
- [ ] Replace +1-XXX-XXX-XXXX with your on-call number
- [ ] Update SLA targets if different from 99.5% / p95 500ms / < 1%
- [ ] Update pricing tiers (post-pilot)
- [ ] Add company name and address footer
- [ ] Have legal team review for compliance with local laws
- [ ] Publish on website and send to pilot customers
