<p align="center">
  <img src="frontend/app/public/logo.svg" alt="AI Agency OS Logo" width="200">
</p>

# AI Agency OS — AI-Native Agency Operating System

**AI Agency OS** is a production-ready, AI-native operating system for modern agencies. It orchestrates Strands-style agent workflows, enforces policy checks powered by [Sentinel](https://github.com/RiteshGenAI/Sentinel.git), and provides a multi-tenant backend with JWT authentication, project management, lead tracking, invoicing, and real-time workflow execution.

Built around a FastAPI backend, a React frontend, a dedicated agents microservice, and PostgreSQL, AI Agency OS enables teams to deploy autonomous agent workflows safely with built-in guardrails, audit trails, and cost controls.

> **Ecosystem**: AI Agency OS is designed to work together with [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) as a unified AI infrastructure stack. Sentinel provides the policy, cost-intelligence, and LLM-gateway layer, while AI Agency OS provides the agency workflow, project-management, and execution layer.

---

## Key Features

### Multi-Tenant Agency Backend
*   **JWT-Based Authentication**: Secure user registration and login with access token expiration and tenant-scoped access control.
*   **Project Management**: Create and manage projects per tenant with full CRUD capabilities.
*   **Lead Tracking**: Capture and manage agency leads linked to projects and workflows.
*   **Invoicing**: Generate and track invoices for agency work and project deliverables.
*   **Sentinel Event Logging**: Record and audit every policy decision made by the internal [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) scanner.

### Strands-Style Agent Workflows
*   **Landing Page Copy Workflow**: A sample end-to-end workflow where research agents, draft agents, and review agents collaborate to produce marketing copy.
*   **[Sentinel](https://github.com/RiteshGenAI/Sentinel.git) Policy Scanning**: Every agent output can be routed through the internal `/internal/sentinel/scan` endpoint for automated safety and policy checks.
*   **Multi-Provider LLM Routing**: The agents service supports Ollama, OpenAI, Anthropic, and other providers via a unified LLM router.
*   **Workflow State Management**: Workflows maintain state across research, draft, and review phases with structured Pydantic outputs.

### Security & Reliability
*   **Secret Key Validation**: The backend rejects default/weak secret keys in production (`BACKEND_ENV=cloud`).
*   **CORS & Security Headers**: Configurable CORS origins and Nginx security headers (X-Frame-Options, X-Content-Type-Options, etc.).
*   **Rate Limiting**: Authentication endpoints are protected by in-memory rate limiting (15 requests per minute per IP).
*   **Request Logging**: All HTTP requests are logged with method, path, status code, and duration.
*   **Centralized Error Handling**: Global middleware returns consistent error responses and logs unhandled exceptions.
*   **Health Checks**: Dedicated `/healthz` and `/api/v1/health/` endpoints for liveness and readiness probes.

### Production Deployment
*   **Single-File Docker Compose**: All services are built inline in `docker-compose.yml` — no separate Dockerfiles required.
*   **AWS Terraform Templates**: Production-ready infrastructure (VPC, ECS Fargate, RDS PostgreSQL, ALB, ECR, Secrets Manager, S3) under `infra/terraform/`.
*   **Database Migrations**: Safe incremental migration script (`backend/migrate.py`) for adding missing schema changes.
*   **Nginx Reverse Proxy**: The frontend container serves the built React app and proxies `/api/*` traffic to the backend.

---

## Application Pages & Features

### Login Page
**Purpose**: Secure authentication gateway for agency users.

**Features**:
- Email and password-based authentication
- JWT token management with automatic attachment to API requests
- Redirect to dashboard on successful login

**Access**: Public

---

### Dashboard Page
**Purpose**: Executive overview of agency projects, workflows, and recent activity.

**Features**:
- KPI cards showing active projects, leads, invoices, and workflow runs
- Quick navigation to projects and workflow execution
- Recent [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) events and policy decisions

**Access**: All authenticated users

---

### Project Page
**Purpose**: Detailed project workspace for managing leads, invoices, and workflow history.

**Features**:
- View project details and status
- Manage associated leads and track their lifecycle
- Create and view invoices for the project
- Review workflow execution history and [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) outcomes

**Access**: All authenticated users (tenant-scoped)

---

## User Journeys & Workflows

### The Agency Admin Journey
1.  **Deploy the Stack**: Start the production Docker stack with `docker compose up --build -d`.
2.  **Log In**: Use the seeded admin credentials to access the dashboard.
3.  **Create Projects**: Set up projects representing clients or campaigns.
4.  **Run Workflows**: Trigger agent workflows (e.g., landing page copy) from the backend or API.
5.  **Monitor [Sentinel](https://github.com/RiteshGenAI/Sentinel.git)**: Review [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) events to ensure all agent outputs meet policy requirements.
6.  **Manage Leads & Invoices**: Track leads and generate invoices tied to project work.

### The Project Manager Journey
1.  **View Dashboard**: Review active projects, leads, and invoices at a glance.
2.  **Manage Projects**: Create and update project details.
3.  **Track Leads**: Capture and progress leads through the sales pipeline.
4.  **Generate Invoices**: Create invoices tied to projects for client billing.

### The Developer/Agent Operator Journey
1.  **Access the API**: Use JWT tokens to call backend workflow and agent endpoints.
2.  **Trigger Workflows**: POST to `/api/v1/workflows/run` with project and prompt details.
3.  **Inspect Agent Output**: Review the structured output from research, draft, and review agents.
4.  **Verify [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) Decisions**: Check `/api/v1/sentinel-events/` for policy scan results.

---

## Step-by-Step Setup & Verification Guide

### 1. Launch the Stack
Run the containerized application using Docker Compose:

```bash
docker compose up --build -d
```

The compose file uses development defaults for PostgreSQL and the backend secret key so it starts immediately. See the **Security** section below before deploying to production.

### 2. Access the Applications
*   **Frontend Web UI**: http://localhost/
*   **Backend API Docs (Swagger UI)**: http://localhost/docs
*   **OpenAPI Schema**: http://localhost/openapi.json
*   **Backend API Base URL**: http://localhost/api/v1/
*   **Backend Health**: http://localhost/healthz

### 3. Log In as Admin
Use the pre-seeded admin credentials:
*   **Email**: `admin@agency.local`
*   **Password**: `admin1234`

You can also explore and test all authenticated endpoints through the Swagger UI at http://localhost/docs. Click **Authorize**, paste a JWT token from `/api/v1/auth/login`, and execute endpoints directly.

> **Note**: The default admin user is created automatically on first startup because `BACKEND_SEED_ADMIN=true` is set in `docker-compose.yml`. In production, set `BACKEND_SEED_ADMIN=false` and create the first user via the `/api/v1/auth/signup` endpoint or a secure external process.

### 4. Create a Project
1.  Navigate to the **Dashboard**.
2.  Use the project creation flow (or call `POST /api/v1/projects/`).
3.  Enter project name and tenant details.

### 5. Run a Workflow
Trigger the landing-page copy workflow:

```bash
curl -X POST http://localhost/api/v1/workflows/run \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "your-project-id",
    "prompt": "Write landing page copy for an AI consulting agency"
  }'
```

### 6. Verify [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) Events
Check that the workflow output was scanned by [Sentinel](https://github.com/RiteshGenAI/Sentinel.git):

```bash
curl http://localhost/api/v1/sentinel-events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Track Leads & Invoices
Use the project page or API endpoints to create leads and invoices for the project.

---

## Architecture & Tech Stack

```
ai_agency_os/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/              # API routers (auth, projects, leads, invoices, workflows, sentinel)
│   │   ├── core/             # Config, security, middleware, logging
│   │   ├── db/               # SQLAlchemy models, session, init
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   └── tests/                # Pytest suite
├── agents/                   # Strands-style workflow microservice
│   ├── app/
│   │   ├── strands/          # Agent workflows and tools
│   │   └── main.py           # FastAPI entrypoint
│   └── tests/                # Agent tests
├── frontend/app/             # React SPA (Vite + TypeScript + Tailwind)
│   └── src/
│       ├── pages/            # Dashboard, Login, Project pages
│       └── lib/              # API client
└── infra/terraform/          # AWS production infrastructure
```

*   **Backend**: FastAPI, SQLAlchemy, Pydantic v2, PostgreSQL, python-jose, bcrypt.
*   **Agents**: FastAPI, Strands-style workflows, multi-provider LLM router.
*   **Frontend**: React 18, Vite, TypeScript, TailwindCSS.
*   **Infrastructure**: Docker, Nginx, PostgreSQL 16, AWS ECS Fargate, RDS, ALB.

---

## Quick Start (Docker)

### Development Mode (Recommended for Local Development)
This mode runs the frontend Vite dev server, backend with hot-reload, and agents with hot-reload. Each service is exposed on its own port.

1.  **Build and run**:
    ```bash
    docker compose up --build -d
    ```

2.  **Access**:
    *   **Frontend**: http://localhost:5173/
    *   **Backend API**: http://localhost:8000/api/v1/
    *   **Backend Swagger UI**: http://localhost:8000/docs
    *   **Agents Service**: http://localhost:9000/
    *   **PostgreSQL**: localhost:5432

### Production Mode
This mode builds production images inline, serves the frontend via Nginx on port 80, and does not expose the backend or agents publicly.

1.  **Set strong secrets**:
    ```bash
    export POSTGRES_PASSWORD=$(openssl rand -hex 32)
    export BACKEND_SECRET_KEY=$(openssl rand -hex 32)
    ```

2.  **Build and run**:
    ```bash
    docker compose -f docker-compose.prod.yml up --build -d
    ```

3.  **Access**:
    *   **Frontend**: http://localhost/
    *   **Backend API** (proxied through Nginx): http://localhost/api/v1/
    *   **Backend Swagger UI** (proxied through Nginx): http://localhost/docs

### Cloud Deployment (AWS)
See [`infra/terraform/README.md`](infra/terraform/README.md) for a complete AWS production deployment guide.

---

## Running Tests

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Agents Tests
```bash
cd agents
pip install -r requirements.txt
pytest
```

---

## Database Management

### Schema Migration
```bash
cd backend
python migrate.py
```

### Initialize Database
The backend runs `init_db()` automatically on startup, creating all tables if they do not exist.

---

## Configuration

### Environment Variables
Configure the stack via environment variables or a `.env` file in the project root:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `agency_os` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `agency_os` |
| `POSTGRES_DB` | PostgreSQL database | `agency_os` |
| `BACKEND_SECRET_KEY` | JWT signing key | `agency-os-docker-dev-secret-key-change-in-production` |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` (dev), `http://localhost` (prod) |
| `BACKEND_SEED_ADMIN` | Auto-create the default admin user on first startup | `true` (dev), `false` (prod) |
| `BACKEND_SEED_ADMIN_EMAIL` | Default admin email | `admin@agency.local` |
| `BACKEND_SEED_ADMIN_PASSWORD` | Default admin password | `admin1234` |
| `BACKEND_SEED_ADMIN_TENANT_ID` | Default admin tenant ID | `default` |
| `LLM_PROVIDER` | LLM provider for agents | `ollama` |
| `LLM_MODEL` | LLM model name | `llama3.2` |
| `LLM_BASE_URL` | LLM provider base URL | `http://host.docker.internal:11434` |
| `VITE_API_BASE_URL` | Frontend API base URL (dev only) | `http://localhost:8000/api/v1` |

> **Warning**: Change `POSTGRES_PASSWORD` and `BACKEND_SECRET_KEY` before any production deployment. Set `BACKEND_SEED_ADMIN=false` in production and create the first user through a secure process.

### Security Configuration
- **Secret Key Validation**: Weak/default keys are rejected when `BACKEND_ENV=cloud`.
- **Rate Limiting**: Auth endpoints limited to 15 requests/minute per IP.
- **CORS**: Restricted to configured origins.

---

## Key API Endpoints

### Authentication
*   `POST /api/v1/auth/signup` — Register a new user
*   `POST /api/v1/auth/login` — Authenticate and receive a JWT token

### Projects
*   `POST /api/v1/projects/` — Create a project
*   `GET /api/v1/projects/` — List projects
*   `GET /api/v1/projects/{project_id}` — Get project details

### Leads
*   `POST /api/v1/leads/` — Create a lead
*   `GET /api/v1/leads/` — List leads
*   `GET /api/v1/leads/{lead_id}` — Get lead details

### Invoices
*   `POST /api/v1/invoices/` — Create an invoice
*   `GET /api/v1/invoices/` — List invoices

### Workflows
*   `POST /api/v1/workflows/run` — Trigger an agent workflow
*   `GET /api/v1/workflows/` — List workflow definitions/runs

### [Sentinel](https://github.com/RiteshGenAI/Sentinel.git)
*   `POST /internal/sentinel/scan` — Internal policy scan endpoint
*   `GET /api/v1/sentinel-events/` — List [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) events

### Health
*   `GET /healthz` — Liveness probe
*   `GET /api/v1/health/` — Readiness + DB check

---

## Security

See [SECURITY.md](SECURITY.md) for the security policy and vulnerability reporting process.

Before deploying to production:
- Change `BACKEND_SECRET_KEY` to a cryptographically random value.
- Change `POSTGRES_PASSWORD` to a strong random value.
- Do not commit `.env` files or credentials.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to AI Agency OS.

---

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for our community standards.

---

## License

AI Agency OS is distributed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
