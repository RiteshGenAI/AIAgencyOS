# AI Agency OS — Production-Ready Fullstack

AI-native Agency OS built around Strands-style agent workflows, Sentinel policy checks, FastAPI, React, and PostgreSQL.

## Key Features

- Multi-tenant backend with JWT auth
- Landing page copy workflow (backend → agents → Sentinel scan)
- Docker dev stack with hot reload
- Production compose with Nginx reverse proxy
- Health checks, request logging, auth rate limiting
- Database init, incremental migrations, and seed scripts

## Architecture

```
frontend (React/Vite) ──► backend (FastAPI) ──► PostgreSQL
                              │
                              ├──► agents service
                              └──► internal Sentinel scan (/internal/sentinel)
```

## Quick Start (Docker — recommended)

```powershell
.\scripts\setup.ps1
.\scripts\start-docker.ps1
```

Services:

| Service  | URL                     |
|----------|-------------------------|
| Frontend | http://localhost:5173   |
| Backend  | http://localhost:8000   |
| Agents   | http://localhost:8081   |
| Postgres | localhost:5432          |

Seed demo data after the stack is up:

```powershell
docker compose exec backend python backend/seed_for_run.py
```

Demo login: `admin@agency.local` / `admin1234`

## Production Mode

Build and run the production stack (Nginx on port 80):

```powershell
docker compose -f docker-compose.prod.yml up --build -d
```

Open http://localhost — the frontend proxies `/api/` to the backend.

Set a strong secret before cloud deployment:

```powershell
$env:BACKEND_SECRET_KEY = "your-random-secret"
$env:BACKEND_ENV = "cloud"
docker compose -f docker-compose.prod.yml up --build -d
```

## Local Development (without Docker)

```powershell
.\scripts\setup.ps1
.\scripts\start-all.ps1
```

Or start services individually:

```powershell
.\scripts\start-postgres.ps1
.\scripts\start-backend.ps1
.\scripts\start-frontend.ps1
```

Copy env templates first:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item agents\.env.example agents\.env
```

Seed the database:

```powershell
cd backend
python seed_for_run.py
```

## Running Tests

```powershell
cd backend
pip install -r requirements.txt
pytest
```

## Database Management

- Schema is created on backend startup via `init_db()`
- Incremental migrations: `python backend/migrate.py`
- Demo seed data: `python backend/seed_for_run.py`

## Configuration

| Variable | Description |
|----------|-------------|
| `BACKEND_DATABASE_URL` | PostgreSQL connection string |
| `BACKEND_SECRET_KEY` | JWT signing key (required for cloud) |
| `BACKEND_ENV` | `local` or `cloud` |
| `BACKEND_AGENTS_SERVICE_URL` | Agents microservice URL |
| `BACKEND_SENTINEL_PROXY_ENABLED` | Proxy scans to external Sentinel |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed origins |
| `STRANDS_SENTINEL_BASE_URL` | Agents → backend internal Sentinel URL |

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/api/v1/health/` | Readiness + DB check |
| POST | `/api/v1/auth/signup` | Register user |
| POST | `/api/v1/auth/login` | Login (OAuth2 form) |
| GET | `/api/v1/projects/{tenant_id}` | List projects |
| POST | `/internal/sentinel/scan` | Internal policy scan |

## Project Structure

```
ai_agency_os/
├── backend/           FastAPI API + models + services
├── agents/            Strands-style workflow microservice
├── frontend/app/      React SPA (Vite + Tailwind)
├── docker/            Dockerfiles
├── scripts/           PowerShell setup/start helpers
├── infra/             Terraform + Jenkins (AWS skeleton)
├── docker-compose.yml         Dev stack
└── docker-compose.prod.yml    Production stack
```

## AWS Deployment

Terraform and Jenkins skeletons live under `infra/`. Use `scripts/deploy_to_aws.py` as a starting point for ECR + ECS deployment.

## Security

See [SECURITY.md](SECURITY.md). Change default secrets before any non-local deployment.
