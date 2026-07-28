# Security Policy

## Supported Versions

We actively support and patch security issues in the following versions of AI Agency OS:

| Variant | Supported |
| ------- | --------- |
| Upstream main / releases 1.0.x | :white_check_mark: |
| Your self-hosted fork / deployment | :white_check_mark: |
| < 1.0.0 upstream | :x: |

Security issues in the upstream codebase are patched and released. Because this project is intended to be forked and self-hosted, we also support the security of your deployed instance as long as you follow the minimum hardening steps below.

## Reporting a Vulnerability

We take the security of AI Agency OS seriously. If you believe you have found a security vulnerability, please report it to us responsibly.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by emailing us at **riteshpatilgenaiofficial@gmail.com**.

### What to Include in a Security Report
To help us triage and resolve the issue quickly, please include:
- A clear description of the variant you are running (upstream vs. customized fork).
- A detailed description of the vulnerability.
- Steps to reproduce the issue (including any proof-of-concept scripts or exploit details).
- The potential impact of the vulnerability.
- The environment details (e.g., OS, browser, package versions, deployment target, whether Sentinel or external LLM integrations are enabled).

### Our Response Process
- We will acknowledge receipt of your vulnerability report within 48 hours.
- We will investigate and verify the vulnerability.
- Once verified, we will work on a fix and release a patched version as soon as possible.
- We will keep you updated throughout the process.

## Fork & Self-Host Minimum Hardening

If you are running your own fork or deployment, these are the minimum security requirements:

- **JWT secret key**: Set `BACKEND_SECRET_KEY` to a cryptographically random value, e.g. `openssl rand -hex 32`.
- **Database password**: Set `POSTGRES_PASSWORD` to a strong random value; never use the Docker Compose development default in production.
- **Seed admin**: Set `BACKEND_SEED_ADMIN=false` in production and create the first owner through a secure process.
- **Environment mode**: Set `BACKEND_ENV=cloud` to enforce strict secret key validation and reject weak defaults.
- **CORS**: Set `BACKEND_CORS_ORIGINS` to the exact origins allowed to call the API.
- **Secrets management**: Do not commit `.env` files or credentials to version control. Use AWS Secrets Manager, Docker secrets, or an equivalent secrets store.
- **TLS**: Terminate TLS at a load balancer or reverse proxy in production. Do not expose backend or agents ports directly to the internet.
- **Optional integrations**: If you remove optional components such as Sentinel or external LLM providers, also remove their environment variables, routes, service code, and any associated data tables to reduce attack surface.

## Security Notes

- Run backend/seed scripts only in development environments.
- The default Docker Compose credentials are for local development only and must be overridden in production.
- For AWS deployments, all secrets are stored in AWS Secrets Manager and injected into ECS tasks at runtime.
