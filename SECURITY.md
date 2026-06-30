# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.5.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security issue, please report it privately rather than opening a public issue.

Email: security@example.com with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact

We aim to acknowledge reports within 48 hours.

## Security Notes

- Change `BACKEND_SECRET_KEY` before any non-local deployment.
- Do not commit `.env` files or credentials.
- Run `backend/seed_for_run.py` only in development environments.
