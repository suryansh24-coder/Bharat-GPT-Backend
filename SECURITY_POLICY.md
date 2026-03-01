# Security & Compliance Policy Document

## Privacy Infrastructure
This platform is hard-coded to adhere to generalized global privacy directives including GDPR and SOC2 structural foundations.

### 1. Hardened Perimeters
* **Headers:** All application egress routes through our custom `RequestLoggingMiddleware` modifying runtime headers locking down XSS Vectors and enforcing strict TLS (HSTS Preload).
* **Sanitization:** `bleach` strictly filters user strings destroying hidden scripts.
* **Prompt Engineering Defense:** Custom RegEx-based heuristics trap malicious payload directives such as "ignore previous instructions".

### 2. GDPR Endpoints
The backend explicitly dictates endpoints managing human rights protocols:
- `GET /api/v1/compliance/export`: Returns aggregate metadata surrounding identity ownership.
- `DELETE /api/v1/compliance/delete`: Executes a "Right to erasure" mutating existing database records instantly.

### 3. Rate Limit / DDOS Mitigation
Redis enforces API throttling. Specific structural limits: 
* Standard Endpoint Auth limits: **5 requests per 60 seconds.**

### 4. Backups
Data at rest utilizes Postgres logic wrapped by a localized bash cron script saving 7-day revolving `.sql.gz` snapshots to disk ensuring Zero-Data-Loss mandates.
