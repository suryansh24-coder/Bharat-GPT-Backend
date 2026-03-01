# Production Deployment Guide

## 1. Enterprise On-Premise (Docker)
Ensure Docker Compose is accessible globally.
```bash
docker-compose up --build -d
```
All system services (Redis, PG, Nginx, API) bootstrap instantly.

## 2. Railway / Render / PaaS Cloud
The repository is packed with `railway.json` and `render.yaml`. 
Simply import this repository directly into their platform UX. Wait for the `uvicorn app.main:app` command to execute on their runner.

## 3. CI/CD Operations
GitHub Actions is mapped inside `.github/workflows/ci.yml`. 
Every push to `main` executes PyTest evaluations and runs `Bandit` dynamically scanning Python structural components for low-level security violations implicitly.

## 4. HTTPS Enforcement
Inside production proxy configurations, `nginx.conf` acts as an edge router. Apply your SSL Cert mappings inside the Nginx container targeting `/etc/ssl/certs`.
