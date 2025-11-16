# Pilot Customer Documentation

Integration guides, setup checklists, and resources for onboarding pilot customers.

## Quick Navigation

### Customer-Facing Document (Send to Pilot)
**[PILOT_CUSTOMER_INTEGRATION.md](PILOT_CUSTOMER_INTEGRATION.md)** - 1-pager quick start guide
- Getting started in 5 minutes
- API endpoint and authentication
- Curl examples (policy check, expected responses)
- Security memo (what NOT to do)
- Key rotation procedure (dashboard + CLI methods)
- Support channels and response times (SLAs)
- Common troubleshooting (5 issues)
- Pre-integration checklist

### Internal Setup Checklist
**[PILOT_CUSTOMER_CHECKLIST.md](PILOT_CUSTOMER_CHECKLIST.md)** - Complete onboarding workflow
- Pre-onboarding (API key generation, documentation prep)
- Week 1-2: Onboarding phase
  - Send documentation package
  - Conduct kickoff call with customer
  - Provide testing environment access
  - Verify integration with customer
- Week 3-4: Production phase
  - Schedule production go-live
  - Monitor customer usage
  - Verify SLA compliance
- Month 1-12: Evaluation
  - Track technical metrics
  - Customer satisfaction surveys
  - Usage analytics
  - Renewal decision

### Documentation Package Index
**[PILOT_LAUNCH_CHECKLIST.md](PILOT_LAUNCH_CHECKLIST.md)** - Master documentation index
- What documents to send (3 required, optional resources)
- When to send each document (timeline)
- Customization checklist (7-point verification)
- Team training guide (what each team should know)
- Success indicators by phase (day 1 through month 2+)

## Integration Workflow

### Phase 1: Pre-Onboarding (Week -1)
- [ ] Generate API key for customer
- [ ] Prepare documentation package
- [ ] Verify monitoring infrastructure
- [ ] Prepare support team

### Phase 2: Onboarding (Weeks 1-2)
- [ ] Send PILOT_CUSTOMER_INTEGRATION.md to customer
- [ ] Conduct kickoff call
- [ ] Customer runs curl examples from documentation
- [ ] Support team monitors first calls
- [ ] Address questions/issues

### Phase 3: Production (Weeks 3-4)
- [ ] Customer moves to production endpoint
- [ ] Monitoring for unusual patterns
- [ ] Verify SLA compliance
- [ ] Go-live checklist

### Phase 4: Evaluation (Month 1+)
- [ ] Track usage metrics
- [ ] Customer satisfaction
- [ ] Identify improvement areas
- [ ] Renewal discussion

## Key Resources

### For Customers
- **Quick Start**: PILOT_CUSTOMER_INTEGRATION.md (1 page, 5-minute setup)
- **Support Contacts**: Email, Slack, on-call for critical issues
- **API Reference**: API endpoint, authentication, policy check endpoint
- **Security Guide**: What NOT to send in requests

### For Internal Teams
- **Onboarding**: PILOT_CUSTOMER_CHECKLIST.md (week-by-week tasks)
- **Documentation**: PILOT_LAUNCH_CHECKLIST.md (customization steps)
- **Success Criteria**: Technical metrics + adoption metrics

## SLA & Support Commitments

### Response Times
- **Email**: 24-48 hours during business days
- **Slack**: Real-time during business hours (9-17 CET)
- **Critical Issues**: On-call engineer responds within 15-30 min

### Availability Guarantee
- Pilot phase: Best-effort (target 99% uptime)
- Production phase: 99% uptime SLA

## Customization Checklist

Before sending to customer, verify:
- [ ] API key correctly configured
- [ ] Customer name personalized in docs
- [ ] Support contact information accurate
- [ ] SLA terms agree with customer contract
- [ ] Example curl commands use correct endpoint
- [ ] Monitoring dashboard accessible to customer
- [ ] Security memo reviewed by customer

## Success Metrics

### Technical Success (Day 1-7)
- Customer API key working
- At least 1 successful policy check
- No authentication errors

### Integration Success (Week 2-3)
- 10+ policy checks successfully processed
- No rate limiting issues
- Customer confirms expected behavior

### Production Success (Month 1+)
- Usage aligns with forecast
- Response times acceptable (<200ms p99)
- <0.1% error rate
- Customer actively using (>100 checks/month)

## Related Resources

- **Deployment**: See `docs/deployment/` for production setup
- **Support**: See `docs/troubleshooting/SUPPORT_OPERATIONS.md` for incident response
- **Architecture**: See `docs/architecture/` for technical details
- **Policies**: See `backend/` for policy engine implementation

## Questions?

Refer to:
1. PILOT_CUSTOMER_INTEGRATION.md for quick answers
2. PILOT_CUSTOMER_CHECKLIST.md for onboarding steps
3. SUPPORT_OPERATIONS.md for incident procedures
