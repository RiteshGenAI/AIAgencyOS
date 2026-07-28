<p align="center">
  <img src="frontend/app/public/AIAgencyOS_Logo.png" alt="AI Agency OS Logo" width="650">
</p>

# AI Agency OS - AI-Native Agency Operating System

**AI Agency OS** is a production-ready, AI-native operating system for modern agencies. It orchestrates Strands-style agent workflows, enforces policy checks powered by [Sentinel](https://github.com/RiteshGenAI/Sentinel.git), and provides a multi-tenant backend with JWT authentication, project management, lead tracking, invoicing, and real-time workflow execution.

Built around a FastAPI backend, a React frontend, a dedicated agents microservice, and PostgreSQL, AI Agency OS enables teams to deploy autonomous agent workflows safely with built-in guardrails, audit trails, role-based access control, and cost controls.

> **Ecosystem**: AI Agency OS is designed to work together with [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) as a unified AI infrastructure stack. Sentinel provides the policy, cost-intelligence, and LLM-gateway layer, while AI Agency OS provides the agency workflow, project-management, and execution layer.

---

## Key Features

### Multi-Tenant Agency Backend
*   **JWT-Based Authentication**: Secure user registration and login with access token expiration, JSON-body login, and tenant-scoped access control.
*   **Role-Based Access Control (RBAC)**: Four enforced roles - `owner`, `manager`, `member`, `client` - with per-endpoint permission checks. Owners can manage users, managers can create projects, members can create leads, and clients have read-only access to assigned resources.
*   **Project Management**: Create and manage projects per tenant with full CRUD capabilities and status tracking.
*   **Lead Tracking**: Capture and manage agency leads linked to tenants and projects with lifecycle status tracking.
*   **Invoicing**: Generate and track invoices for agency work and project deliverables, scoped by project.
*   **Sentinel Event Logging**: Record and audit every policy decision made by the internal [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) scanner, including risk scores and issues.

### Strands-Style Agent Workflows
*   **Landing Page Copy Workflow**: A sample end-to-end workflow where research agents, draft agents, and QA agents collaborate to produce production-ready marketing copy.
*   **Ad Campaign Workflow**: Generate structured ad campaign briefs and drafts via multi-agent orchestration.
*   **[Sentinel](https://github.com/RiteshGenAI/Sentinel.git) Policy Scanning**: Every agent output can be routed through the internal `/internal/sentinel/scan` endpoint for automated safety and policy checks before delivery.
*   **Multi-Provider LLM Routing**: The agents service supports Ollama, OpenAI, Anthropic, and other providers via a unified LLM router with configurable base URLs and API keys.
*   **Workflow State Management**: Workflows maintain state across research, draft, and review phases with structured Pydantic outputs and QA scoring.

### Security & Reliability
*   **Secret Key Validation**: The backend rejects default/weak secret keys in production (`BACKEND_ENV=cloud`).
*   **CORS & Security Headers**: Configurable CORS origins and Nginx security headers (X-Frame-Options, X-Content-Type-Options, etc.).
*   **Rate Limiting**: Authentication endpoints are protected by in-memory rate limiting (15 requests per minute per IP).
*   **Request Logging**: All HTTP requests are logged with method, path, status code, and duration.
*   **Centralized Error Handling**: Global middleware returns consistent error responses and logs unhandled exceptions.
*   **Health Checks**: Dedicated `/healthz` and `/api/v1/health/` endpoints for liveness and readiness probes.
*   **Tenant Isolation**: Every data operation is scoped to the authenticated user's tenant to prevent cross-tenant data leaks.
*   **Owner Safeguards**: Admin endpoints prevent the last active owner from being deactivated or demoted, ensuring the system is never orphaned.

### Production Deployment
*   **Single-File Docker Compose**: All services are built inline in `docker-compose.yml` - no separate Dockerfiles required.
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
- Session persistence using localStorage
- Automatic redirect to dashboard on successful login
- Access control based on user roles
- Pre-seeded admin credentials for first-time access

**Access**: Public (no authentication required)

---

### Dashboard Page
**Purpose**: Executive overview of agency projects, workflows, leads, invoices, and recent Sentinel activity.

**Features**:
- KPI cards showing active projects count, total leads, total invoices, and flagged Sentinel events
- Quick navigation to projects and workflow execution
- Recent [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) events and policy decisions with risk-score indicators
- Tenant-scoped data aggregation across all projects
- Real-time data loading with error handling

**Access**: All authenticated users (owner, manager, member, client)

**Key Metrics Displayed**:
- Active projects count
- Total leads in pipeline
- Total invoice amount
- Flagged Sentinel events (risk_score > 50)
- Recent policy scan outcomes

---

### Projects Page
**Purpose**: Browse and create agency projects.

**Features**:
- List all projects for the authenticated user's tenant
- Create new projects with name and description
- Select clients using human-readable reference IDs (e.g., `CID-0001`) via dropdown
- Inline client creation from the project form with auto-generated CID
- Project status badges (e.g., draft, active, scoped)
- Navigation to individual project detail pages
- Empty-state guidance for first-time users

**Access**: All authenticated users

**Client Selection**: The project creation form provides a dropdown of existing clients labeled by their human-readable `reference_id` (e.g., `CID-0001 - Acme Corp`). You can also create a new client inline; the system auto-assigns the next available CID per tenant.

---

### Project Page
**Purpose**: Detailed project workspace for managing invoices, leads, and Sentinel events.

**Features**:
- View project details and status
- Manage associated invoices for the project
- Review [Sentinel](https://github.com/RiteshGenAI/Sentinel.git) events scoped to the project with risk scores and issues
- Quick links back to project list

**Access**: All authenticated users (tenant-scoped)

---

### Leads Page
**Purpose**: Capture and manage agency leads.

**Features**:
- List all leads for the authenticated user's tenant
- Create new leads with name, email, phone, notes, and project association
- Lead status tracking (e.g., new, contacted, qualified)
- Empty-state guidance and creation form

**Access**: All authenticated users

---

### Invoices Page
**Purpose**: Create and track invoices for agency work.

**Features**:
- List all invoices aggregated across the user's projects
- Create new invoices with amount, currency, project binding, due date, and description
- Invoice status tracking (draft, sent, paid, cancelled)
- Currency support (defaults to USD)
- Per-project invoice aggregation

**Access**: All authenticated users

---

### Workflows Page
**Purpose**: Trigger and inspect AI agent workflows.

**Features**:
- Select a project and enter a brief prompt
- Run the **Landing Page Copy** workflow, which orchestrates research, drafting, and QA agents
- Display structured workflow results including hero headlines, sections, QA scores, and Sentinel scan status
- Real-time error feedback during workflow execution
- Loading states during long-running agent operations

**Access**: Owner, manager, and member roles

**Workflow Output Includes**:
- Hero headline and subheadline
- Section copy blocks
- QA evaluation scores (overall, brand voice, clarity, structure)
- Detected issues and suggestions
- Sentinel policy scan result

---

### Sentinel Events Page
**Purpose**: Review all policy scan outcomes across projects.

**Features**:
- Aggregate Sentinel events across all projects for the tenant
- Display scan type (prompt, output, tool_call), entity type, risk score, and issues
- Color-coded risk indicators (low, medium, high risk)
- Empty-state messaging when no events exist
- Timestamps for audit trails

**Access**: All authenticated users

---

### Admin Page
**Purpose**: System administration for user management.

**Features**:
- **User Management Table**:
  - View all registered users with ID, tenant, email, role, and active status
  - Change user roles (owner, manager, member, client) via dropdown - owner-only
  - Deactivate users with confirmation dialog - owner-only
  - Visual indicators for user status (active/inactive) and role badges
  - Current user is protected from self-demotion and self-deactivation
  - Prevents removal of the last active owner to avoid system lockout

**Access**: Owner role only

**Management Capabilities**:
- Full user lifecycle management
- Role assignment via API (`role` field accepted on signup)
- System-wide configuration control

---

## User Journeys & Workflows

### The Agency Admin (Owner) Journey
1.  **Launch the Stack**: Start the production Docker stack with `docker compose up --build -d`.
2.  **Log In**: Use the pre-seeded admin credentials to access the dashboard.
3.  **Create Users**: Sign up additional users via the API or let them self-register with assigned roles (`owner`, `manager`, `member`, `client`).
4.  **Manage Users**: Navigate to **Admin** to change roles, deactivate accounts, and audit the user base.
5.  **Create Projects**: Set up projects representing clients or campaigns.
6.  **Run Workflows**: Trigger agent workflows (e.g., landing page copy, ad campaign) from the backend or the Workflows page.
7.  **Monitor Sentinel**: Review Sentinel events to ensure all agent outputs meet policy requirements.
8.  **Manage Leads & Invoices**: Track leads and generate invoices tied to project work.

### The Project Manager Journey
1.  **View Dashboard**: Review active projects, leads, and invoices at a glance.
2.  **Manage Projects**: Create and update project details.
3.  **Track Leads**: Capture and progress leads through the sales pipeline.
4.  **Generate Invoices**: Create invoices tied to projects for client billing.
5.  **Run Workflows**: Execute landing page or ad campaign workflows against selected projects.
6.  **Review Sentinel Events**: Inspect policy scan results for generated content.

### The Developer/Agent Operator Journey
1.  **Access the API**: Use JWT tokens to call backend workflow and agent endpoints.
2.  **Trigger Workflows**: POST to `/api/v1/workflows/{project_id}/landing-page` with project, brief, and policy details.
3.  **Inspect Agent Output**: Review structured output from research, draft, and QA agents.
4.  **Verify Sentinel Decisions**: Check `/api/v1/sentinel-events/project/{project_id}` for policy scan results.
5.  **Integrate Agents**: Call the agents microservice directly at `http://localhost:9000/agents/landing-page` or `/agents/ad-campaign`.

### The Client (Customer) Journey
1.  **Read-Only Access**: Log in to view projects, leads, and invoices associated with their tenant.
2.  **Monitor Progress**: Track project status and deliverables.
3.  **Review Invoices**: View invoice history and amounts for their projects.

---

## Step-by-Step Setup & Verification Guide

### 1. Launch the Stack
Run the containerized application using Docker Compose (Development mode for local hot-reload):

```bash
docker compose up --build -d
```

The compose file uses development defaults for PostgreSQL and the backend secret key so it starts immediately. See the **Security** section below before deploying to production.

### 2. Access the Applications
*   **Frontend Web UI**: http://localhost:5173/
*   **Backend API Docs (Swagger UI)**: http://localhost:8000/docs
*   **OpenAPI Schema**: http://localhost:8000/openapi.json
*   **Backend API Base URL**: http://localhost:8000/api/v1/
*   **Backend Health**: http://localhost:8000/healthz
*   **Agents Service**: http://localhost:9000/

### 3. Log In as Admin
Navigate to http://localhost:5173/ and log in using the pre-seeded admin credentials (created automatically when `BACKEND_SEED_ADMIN=true`):

*   **Email**: `admin@agency.local`
*   **Password**: `admin1234`

You can also explore and test all authenticated endpoints through the Swagger UI at http://localhost:8000/docs. Click **Authorize**, paste a JWT token from `/api/v1/auth/login`, and execute endpoints directly.

> **Note**: The default admin user is created automatically on first startup because `BACKEND_SEED_ADMIN=true` is set in `docker-compose.yml`. In production, set `BACKEND_SEED_ADMIN=false` and create the first user via the `/api/v1/auth/signup` endpoint or a secure external process.

### 4. Create a Project
1.  Navigate to the **Projects** page in the sidebar.
2.  Click **Create Project**.
3.  Enter a project name and optional description.
4.  Select a client from the dropdown (human-readable IDs like `CID-0001`).
    - If no clients exist, click **+ New Client** to create one inline. The system will auto-assign the next available `CID-XXXX` reference ID.
5.  Click **Create**.

You can also create projects via the API. The `client_id` field accepts either the internal UUID or the human-readable `reference_id` (e.g., `CID-0001`); the backend resolves it automatically:
```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"default","client_id":"CID-0001","name":"My Project"}'
```

### 5. Run a Workflow
Trigger the landing-page copy workflow from the **Workflows** page or via the API:

```bash
curl -X POST http://localhost:8000/api/v1/workflows/PROJECT_ID/landing-page \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "default",
    "client_id": "CID-0001",
    "project_id": "PROJECT_ID",
    "policy_id": "default",
    "brief_text": "Write landing page copy for an AI consulting agency"
  }'
```

Replace `PROJECT_ID` with an actual project ID from your tenant.

### 6. Verify Sentinel Events
Check that the workflow output was scanned by [Sentinel](https://github.com/RiteshGenAI/Sentinel.git):

```bash
curl http://localhost:8000/api/v1/sentinel-events/project/PROJECT_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Track Leads & Invoices
Use the **Leads** and **Invoices** pages (or API endpoints) to create records tied to your projects.

---

## Architecture & Tech Stack

AI Agency OS is built using a clean, decoupled architecture:

```
ai_agency_os/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # Routers (auth, projects, leads, invoices, workflows, sentinel, admin, internal)
│   │   ├── core/             # Configuration, enums, security, middleware, logging
│   │   ├── db/               # PostgreSQL engine, session, migrations, seeding
│   │   ├── models/           # SQLAlchemy database schemas (User, Tenant, Client, Project, Lead, Invoice, SentinelEvent)
│   │   ├── schemas/          # Pydantic validation schemas
│   │   └── services/         # Core business logic (auth, projects, leads, invoices, sentinel, agents)
│   └── tests/                # Pytest suite (API tests, RBAC tests)
├── agents/                   # Strands-style workflow microservice
│   ├── app/
│   │   ├── llm_router/       # Multi-provider LLM router (Ollama, OpenAI, Anthropic)
│   │   ├── models/           # Pydantic models for landing page and ad campaign outputs
│   │   ├── services/         # Workflow runners
│   │   └── strands/          # Agent workflows, tools, and graph definitions
│   └── tests/                # Agent tests
├── frontend/app/             # React SPA (Vite + TypeScript + Tailwind)
│   └── src/
│       ├── components/       # Common visual elements (Sidebar)
│       ├── pages/            # Page layouts (Login, Dashboard, Projects, Project, Leads, Invoices, Workflows, Sentinel Events, Admin)
│       ├── lib/              # Client API wrapper
│       └── types/            # TypeScript type definitions
├── infra/terraform/          # AWS production infrastructure (VPC, ECS Fargate, RDS, ALB, ECR, S3, Secrets Manager)
├── scripts/                  # Local development and deployment scripts
├── docker-compose.yml        # Development compose
├── docker-compose.prod.yml   # Production compose (Nginx reverse proxy)
└── nginx.conf                # Production Nginx configuration
```

*   **Backend**: FastAPI, SQLAlchemy (PostgreSQL driver), Pydantic v2, python-jose, bcrypt, pytest.
*   **Agents**: FastAPI, Strands-style workflows, multi-provider LLM router, httpx.
*   **Frontend**: React 18, Vite, TypeScript, TailwindCSS, React Router, Recharts.
*   **Infrastructure**: Docker, Nginx, PostgreSQL 16, AWS ECS Fargate, RDS, ALB, Terraform.

---

## Quick Start (Docker Deployment)

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
Run the backend test suite against a PostgreSQL database (SQLite is not supported):

```bash
cd backend
export TEST_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/agency_os_test
pytest
```

Or run inside the Docker container:
```bash
docker compose exec -T -e TEST_DATABASE_URL=postgresql+psycopg2://agency_os:agency_os@db:5432/agency_os_test backend pytest backend/tests/ -v
```

### Agents Tests
```bash
cd agents
pytest
```

---

## Database Management

### Schema Migration
Safe migration script for adding missing database columns:

```bash
cd backend
python migrate.py
```

### Initialize Database
The backend runs `init_db()` automatically on startup, creating all tables if they do not exist. It also normalizes legacy `admin` roles to `owner` and seeds the default admin user when `BACKEND_SEED_ADMIN=true`.

### Seeding Admin User
The default admin user is created automatically on first startup:

*   **Email**: `admin@agency.local`
*   **Password**: `admin1234`
*   **Tenant ID**: `default`
*   **Role**: `owner`

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
| `BACKEND_DATABASE_URL` | SQLAlchemy database URL | `postgresql+psycopg2://agency_os:agency_os@db:5432/agency_os` |
| `BACKEND_ENV` | Environment mode (`local` or `cloud`) | `local` |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` (dev), `http://localhost` (prod) |
| `BACKEND_SEED_ADMIN` | Auto-create the default admin user on first startup | `true` (dev), `false` (prod) |
| `BACKEND_SEED_ADMIN_EMAIL` | Default admin email | `admin@agency.local` |
| `BACKEND_SEED_ADMIN_PASSWORD` | Default admin password | `admin1234` |
| `BACKEND_SEED_ADMIN_TENANT_ID` | Default admin tenant ID | `default` |
| `BACKEND_AGENTS_SERVICE_URL` | Agents service base URL | `http://agents:8081` |
| `BACKEND_SENTINEL_URL` | Sentinel proxy base URL | `http://sentinel:8082` |
| `BACKEND_SENTINEL_PROXY_ENABLED` | Enable Sentinel proxy scanning | `False` |
| `LLM_PROVIDER` | LLM provider for agents | `ollama` |
| `LLM_MODEL` | LLM model name | `llama3.2` |
| `LLM_BASE_URL` | LLM provider base URL | `http://host.docker.internal:11434` |
| `LLM_API_KEY` | LLM provider API key | `""` |
| `VITE_API_BASE_URL` | Frontend API base URL (dev only) | `http://localhost:8000/api/v1` |

> **Warning**: Change `POSTGRES_PASSWORD` and `BACKEND_SECRET_KEY` before any production deployment. Set `BACKEND_SEED_ADMIN=false` in production and create the first user through a secure process.

### Security Configuration
- **Secret Key Validation**: The application enforces secure secret key configuration and rejects default/weak keys when `BACKEND_ENV=cloud`.
- **Rate Limiting**: Authentication endpoints are rate-limited to 15 requests per minute per IP.
- **CORS**: Restricted to configured origins.
- **Tenant Scoping**: All data operations enforce tenant isolation.
- **Owner Safeguards**: Admin endpoints validate that the last active owner cannot be deactivated or demoted.

---

## Key API Endpoints

### Authentication & User Management
*   `POST /api/v1/auth/signup` - Register a new user with optional role (`owner`, `manager`, `member`, `client`). Defaults to `member`.
*   `POST /api/v1/auth/login` - Authenticate with JSON body (`email`, `password`) and receive a JWT token
*   `GET /api/v1/admin/users` - List all users (owner only)
*   `PUT /api/v1/admin/users/{user_id}/role` - Change user role (owner only)
*   `DELETE /api/v1/admin/users/{user_id}` - Deactivate user (owner only)

### Clients
*   `POST /api/v1/clients/` - Create a client (owner, manager). Accepts optional `reference_id`; if omitted, a sequential `CID-XXXX` ID is auto-generated per tenant.
*   `GET /api/v1/clients/{tenant_id}` - List clients for a tenant (all roles)

### Projects
*   `POST /api/v1/projects/` - Create a project (owner, manager). The `client_id` field accepts either the internal UUID or the human-readable `reference_id` (e.g., `CID-0001`).
*   `GET /api/v1/projects/{tenant_id}` - List projects for a tenant (all roles)
*   `POST /api/v1/projects/{project_id}/scope` - Scope a project with landing-page workflow output (owner, manager)

### Leads
*   `POST /api/v1/leads/` - Create a lead (owner, manager, member)
*   `GET /api/v1/leads/{tenant_id}` - List leads for a tenant (all roles)

### Invoices
*   `POST /api/v1/invoices/` - Create an invoice (owner, manager, member)
*   `GET /api/v1/invoices/project/{project_id}` - List invoices for a project (all roles)

### Workflows & Agents
*   `POST /api/v1/workflows/{project_id}/landing-page` - Run landing-page copy workflow (owner, manager, member)
*   `POST /agents/landing-page` - Direct agents microservice endpoint for landing-page copy
*   `POST /agents/ad-campaign` - Direct agents microservice endpoint for ad campaign generation
*   `GET /agents/healthz` - Agents service health check

### Sentinel Policy Scanning
*   `POST /internal/sentinel/scan` - Internal policy scan endpoint
*   `GET /api/v1/sentinel-events/project/{project_id}` - List Sentinel events for a project (all roles)

### Health
*   `GET /healthz` - Liveness probe
*   `GET /api/v1/health/` - Readiness + database check

---

## Data Models

### Core Entities
*   **User**: Agency users with tenant scoping, email, hashed password, role (`owner`/`manager`/`member`/`client`), and active status.
*   **Tenant**: Top-level organization unit. All users, projects, leads, and invoices are scoped to a tenant.
*   **Client**: Client record linked to a tenant, used for project and lead attribution. Each client has a human-readable `reference_id` (e.g., `CID-0001`) that is unique within the tenant and can be used in place of the internal UUID in API requests.
*   **Project**: Agency project with name, description, status, and scoped summary for workflow outputs.
*   **Lead**: Sales lead with source, raw text, status, and optional project/client binding.
*   **Invoice**: Financial invoice with amount, currency, status, due date, and project binding.
*   **SentinelEvent**: Audit record of every policy scan with scan type, entity type, risk score, issues, and optional project binding.

---

## RBAC Reference

| Role | Create Project | Create Lead | Create Invoice | Run Workflow | List Users | Change Roles | Deactivate Users |
|------|---------------|-------------|----------------|--------------|------------|--------------|------------------|
| `owner` | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| `manager` | Yes | Yes | Yes | Yes | No | No | No |
| `member` | No | Yes | Yes | Yes | No | No | No |
| `client` | No | No | No | No | No | No | No |

All roles can **read** (list/view) projects, leads, invoices, and Sentinel events within their tenant.

---

## Security

See [SECURITY.md](SECURITY.md) for the security policy and vulnerability reporting process.

Before deploying to production:
- Change `BACKEND_SECRET_KEY` to a cryptographically random value.
- Change `POSTGRES_PASSWORD` to a strong random value.
- Set `BACKEND_ENV=cloud` to enforce strict secret key validation.
- Set `BACKEND_SEED_ADMIN=false` and create the first user via a secure process.
- Do not commit `.env` files or credentials.

---

## Running Your Own Instance

This project is designed to be self-hosted and forked. The defaults assume local development, but production setup requires overriding secrets and disabling auto-seeding.

**Minimum setup for a custom fork:**
1. Copy `backend/.env.example` to `backend/.env` and set `BACKEND_SECRET_KEY` (`openssl rand -hex 32`), `POSTGRES_PASSWORD`, and `BACKEND_ENV=cloud`.
2. Set `BACKEND_SEED_ADMIN=false` in production so no default admin is auto-created.
3. Set `BACKEND_CORS_ORIGINS` to your domain(s).
4. Run `docker compose up --build` for local or `docker compose -f docker-compose.prod.yml up --build -d` for production.
5. Create the first owner via `POST /api/v1/auth/signup`.

**Decoupling from optional infrastructure:**
- **Sentinel**: The backend ships with a Sentinel proxy endpoint (`/internal/sentinel/scan`). Forks that replace Sentinel can remove `sentinel_event_service.py`, the `/internal/sentinel/scan` router, and the `BACKEND_SENTINEL_PROXY_ENABLED` check. The agents service only uses `STRANDS_SENTINEL_BASE_URL` for optional scanning.
- **LLM provider**: Change `LLM_PROVIDER`, `LLM_MODEL`, `LLM_BASE_URL`, and `LLM_API_KEY` to use OpenAI, Anthropic, or a self-hosted model instead of the default Ollama configuration.
- **Branding**: Replace `frontend/app/public/AIAgencyOS_Logo.png` and update the `name` field in `frontend/app/package.json`. Update the title and styling in `frontend/app/index.html`.
- **Multi-tenancy**: The system is tenant-scoped by default. Forks that need single-tenant operation can drop the `tenant_id` column, remove RBAC checks, and simplify the data models.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to AI Agency OS.

---

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for our community standards.

---

## License

AI Agency OS is distributed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---

## Topics

[react](/topics/react "Topic: react") [docker](/topics/docker "Topic: docker") [typescript](/topics/typescript "Topic: typescript") [postgresql](/topics/postgresql "Topic: postgresql") [rbac](/topics/rbac "Topic: rbac") [jwt-auth](/topics/jwt-auth "Topic: jwt-auth") [fastapi](/topics/fastapi "Topic: fastapi") [multi-tenant](/topics/multi-tenant "Topic: multi-tenant") [agent-workflows](/topics/agent-workflows "Topic: agent-workflows") [strands](/topics/strands "Topic: strands") [llm-gateway](/topics/llm-gateway "Topic: llm-gateway") [sentinel](/topics/sentinel "Topic: sentinel") [ai-agency](/topics/ai-agency "Topic: ai-agency") [generative-ai](/topics/generative-ai "Topic: generative-ai") [genai](/topics/genai "Topic: genai") [terraform](/topics/terraform "Topic: terraform") [aws](/topics/aws "Topic: aws") [ecs-fargate](/topics/ecs-fargate "Topic: ecs-fargate") [rds](/topics/rds "Topic: rds")
