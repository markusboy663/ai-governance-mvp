# Data Processing Agreement (DPA) - Template

**Between:**
- **Data Controller**: [YOUR COMPANY NAME] ("Company")
- **Data Processor**: AI Governance Team ("Processor")
- **Effective Date**: [DATE]
- **Version**: 1.0

---

## 1. Scope of Data Processing

### 1.1 Data Processed

The Processor processes the following categories of personal data on behalf of the Company:

| Category | Description | Retention |
|----------|-------------|-----------|
| **API Key Identifiers** | UUID-based key IDs (not secrets) | Until key deletion |
| **Audit Logs** | Metadata only: timestamp, model used, operation, risk score, decision | 90 days (auto-purged) |
| **Rate Limiting Data** | Request counts per API key | 60 seconds (ephemeral) |
| **Error Tracking** | Stack traces, request context (no user input) | 30 days (Sentry) |

### 1.2 What is NOT Processed

The Processor explicitly **does not store**:
- User prompts or inputs
- AI model outputs or responses
- Personal data (PII) embedded in requests
- Customer proprietary data
- Raw request/response bodies

**Security by Design**: These fields are blocked at the API layer (see `FORBIDDEN_FIELDS` in auth.py).

### 1.3 Purpose

Data processing is for the following purposes only:
- Governance policy enforcement (real-time evaluation)
- Audit trail generation (compliance)
- Rate limiting (abuse prevention)
- Error monitoring (Sentry integration)
- Performance analytics (latency tracking)

---

## 2. Categories of Data Subjects

- Company employees (API key generators)
- Company customers (API key users)
- End-users of Company's AI systems (indirectly, via metadata)

---

## 3. Data Security Measures

### 3.1 Encryption

| Layer | Method | Status |
|-------|--------|--------|
| **In Transit** | TLS 1.3 (HTTPS) | ✅ Required in production |
| **At Rest** | PostgreSQL encryption (Neon default) | ✅ Enabled |
| **Redis** | RedisCloud encryption | ✅ Enabled |
| **Backups** | Neon encrypted snapshots | ✅ Enabled |

### 3.2 Access Controls

- **Admin Authentication**: API key (bcrypt hashed, never plaintext)
- **Dashboard Access**: Admin key + browser session
- **Database Access**: Restricted to backend service only
- **Redis Access**: Password-protected, internal only
- **No Direct DB Access**: No human SSH access to production database

### 3.3 Authentication & Authorization

- All endpoints require `Authorization: Bearer <api_key>` header
- API keys are bcrypt hashed (bcrypt cost 12)
- Rate limiting prevents brute force attacks (100 req/60 sec)
- Expired keys automatically invalidated

### 3.4 Infrastructure Security

- **Hosting**: Render (SOC 2 compliant, automated backups)
- **Database**: Neon PostgreSQL (encrypted, auto-backup)
- **Redis**: RedisCloud (encrypted, auto-backup)
- **Monitoring**: Sentry (encrypted, compliant with GDPR)
- **HTTPS**: Auto-renewed SSL certificates

### 3.5 Vulnerability Management

- **Dependency Scanning**: pip-audit (Python), npm audit (Node.js) run monthly
- **Patch Management**: Security updates applied within 48 hours
- **Incident Response**: Sentry alerts on errors, on-call escalation for critical issues

---

## 4. Data Processing Activities

### 4.1 Check Request Processing

```
User Request
    ↓
[Authentication] ← Verify API key (metadata only)
    ↓
[Policy Evaluation] ← Check against policies (metadata only)
    ↓
[Risk Scoring] ← Calculate risk (no content processing)
    ↓
[Decision] ← Allow/Block based on risk
    ↓
[Audit Log] ← Store metadata only
    ↓
Response returned to user
```

**Data Retention**: Metadata logged for 90 days, then auto-purged.

### 4.2 Dashboard Access

- Admin views list of API keys (UUIDs, not secrets)
- Admin views policies and violation counts
- Admin views audit logs (metadata only: timestamp, model, status)
- No raw data exposure in UI

---

## 5. Sub-processors (Third Parties)

The Processor uses the following sub-processors for data processing:

| Sub-Processor | Purpose | Location | Compliance |
|---------------|---------|----------|-----------|
| **Neon PostgreSQL** | Database hosting | US (multi-region) | SOC 2, GDPR |
| **RedisCloud** | Cache/rate limiting | US | SOC 2, GDPR |
| **Render** | Backend hosting | US (global CDN) | SOC 2, GDPR |
| **Vercel** | Frontend hosting | Global (multi-region) | SOC 2, GDPR |
| **Sentry** | Error monitoring | US/EU (GDPR compliant) | SOC 2, GDPR |

**Processor Responsibility**: Company is notified of any sub-processor changes 30 days in advance.

---

## 6. Data Subject Rights

### 6.1 Right of Access

**How it Works**:
- Company can request all audit logs for a specific API key
- Logs returned in JSON format
- Response: < 5 business days

**Request Process**:
```bash
GET /api/admin/logs?api_key_id=xxx
Authorization: Bearer <admin_key>
```

### 6.2 Right to Erasure ("Right to Forget")

**What Gets Deleted**:
- API key and all associated audit logs
- Immediately upon deletion request
- Logs auto-purged after 90 days anyway

**Request Process**:
```bash
DELETE /api/admin/keys/{key_id}
Authorization: Bearer <admin_key>
```

**Confirmation**: Deletion confirmation sent within 24 hours.

### 6.3 Right to Data Portability

**What Can Be Exported**:
- Audit logs (CSV format)
- Policy settings (JSON format)
- API key metadata (JSON format)

**Request Process**:
```bash
GET /api/admin/export?format=csv&date_range=90days
Authorization: Bearer <admin_key>
```

---

## 7. Data Breach Notification

### 7.1 Breach Definition

A breach is:
- Unauthorized access to database (confidentiality)
- Unauthorized modification of audit logs (integrity)
- Loss of audit logs (availability)

### 7.2 Notification Timeline

- **Processor discovers breach**: Notify Company within 24 hours
- **Company notifies authorities**: Within 72 hours (GDPR requirement)
- **Company notifies end-users**: Without undue delay

### 7.3 Breach Response

1. Isolate affected systems
2. Assess scope and severity
3. Notify Company immediately
4. Implement remediation
5. Document incident
6. Conduct post-breach audit

**Contact for Breach Reports**:
```
security@yourcompany.com
Phone: +1-XXX-XXX-XXXX (24/7 on-call)
```

---

## 8. Term & Termination

### 8.1 Term

- **Start Date**: [EFFECTIVE DATE]
- **Duration**: Until terminated by either party
- **Renewal**: Automatic unless notice given 30 days prior

### 8.2 Termination

**Either party may terminate with 30 days' notice for any reason.**

Upon termination:
1. Company stops sending requests to Processor
2. Processor stops processing data
3. Audit logs deleted after 90 days (or immediately if requested)
4. Backups retained for 14 days, then deleted
5. Final data deletion confirmation within 10 days

---

## 9. Liability & Indemnification

### 9.1 Data Controller Responsibilities

Company is responsible for:
- Ensuring data is lawfully collected
- Ensuring customer consent for data processing
- Notifying data subjects about processing (privacy policy)
- Implementing privacy by design
- Managing API key security

### 9.2 Data Processor Responsibilities

Processor is responsible for:
- Processing data only as instructed
- Implementing agreed security measures
- Notifying Company of breaches
- Assisting with data subject rights requests
- Sub-processor management

### 9.3 Limitation of Liability

Neither party's liability shall exceed:
- **Direct damages**: Fees paid in the past 12 months
- **Indirect damages**: No liability for lost profits, data loss, business interruption
- **Exception**: Data breaches caused by gross negligence (unlimited liability)

---

## 10. Compliance & Audit

### 10.1 Compliance Certifications

The Processor maintains:
- ✅ ISO 27001 (Information Security Management) - via Render/Neon
- ✅ SOC 2 Type II (Security, Availability, Processing Integrity)
- ✅ GDPR Compliance (Art. 28-30)
- ✅ CCPA Compliance (if applicable)

### 10.2 Audit Rights

Company has the right to:
- Audit Processor's security practices (with 15 days' notice)
- Request audit reports (annually)
- Review sub-processor security (upon request)
- Conduct penetration testing (with 30 days' notice, coordinated)

**Audit Scope**:
- Infrastructure security
- Access controls
- Encryption implementation
- Backup procedures
- Incident response plan

---

## 11. Amendments

Any amendments to this DPA require:
- Written agreement from both parties
- 30 days' notice for non-material changes
- Mutual consent for material changes

---

## Signatures

**For the Company**:

Name: ______________________

Title: ______________________

Date: ______________________

Signature: ______________________

---

**For the Processor (AI Governance)**:

Name: ______________________

Title: ______________________

Date: ______________________

Signature: ______________________

---

## Appendix A: Technical Measures

### Data Encryption

```python
# At rest (database)
PostgreSQL: 256-bit AES (Neon default)
Redis: 256-bit AES (RedisCloud default)

# In transit
TLS 1.3 (all API endpoints)
HTTPS enforced in production
```

### Access Control

```python
# Authentication
API keys: bcrypt hashing (cost 12)
Admin access: Bearer token in Authorization header
Rate limiting: 100 req/60 sec per key

# Authorization
Database: Restricted to backend service
Redis: Password protected, internal only
Backups: Encrypted, AWS S3 access restricted
```

### Audit Trail

```python
# What's logged
- Timestamp (UTC)
- API key ID (UUID, not secret)
- Model used
- Operation
- Risk score
- Allow/Block decision
- Latency in milliseconds

# What's NOT logged
- Request content
- Response content
- User input
- Personal data
```

---

## Appendix B: Data Deletion Procedure

### Automatic Deletion (90 days)

1. Cron job runs daily (2 AM UTC)
2. Finds logs older than 90 days
3. Deletes from database
4. Logs to Sentry for audit trail
5. Snapshot created before deletion (for recovery if needed)

### Manual Deletion (On Request)

```bash
# Request deletion of specific API key
DELETE /api/admin/keys/{key_id}

# Processor deletes:
- API key record
- All associated audit logs (immediate)
- Backup snapshots (within 14 days)

# Confirmation sent to Company within 24 hours
```

---

**END OF DPA TEMPLATE**

**Note to Company Legal**: This template must be reviewed and customized by your legal team before use. Replace `[YOUR COMPANY NAME]`, dates, and contact information with actual values.
