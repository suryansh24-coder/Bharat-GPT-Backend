# Software Requirements Specification (SRS) - Phase 2

## 1. Core Requirements
The system must handle synchronous and strictly isolated data transmission between external intelligence nodes (OpenAI) and secure storage nodes (Postgres). 

## 2. Functional Requirements
* **F1**: System must support JWT-based login, auto-rotating access profiles.
* **F2**: System must enforce brute-force validation blocking repeated access tokens within a 1-minute window constraint.
* **F3**: User Data must be available for dynamic export (GDPR / Right to Portability).
* **F4**: User Data must have deterministic soft/hard deletion endpoints (`/api/v1/compliance/delete`).

## 3. Non-Functional Requirements
* **Scalability**: Ability to boot horizontally behind docker swarm / k8s scaling Nginx upstream targets.
* **Observability**: Expose `/metrics` standard formatted for Prometheus scraping within 2 seconds.
* **Security**: Inject Government-grade CSP, HSTS, X-Frame-Options on all egress traffic frames.
