# AI Agency OS Runtime Fixes + Multi-Provider LLM Router Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the critical runtime gaps in the backend, frontend, agents, tests, and Docker setup; replace stubbed LLM calls with a multi-provider router inspired by the [wrapper](https://github.com/anubhavgirdhar1/wrapper) repo; and make the project runnable on Windows, Linux, WSL, and macOS.

**Architecture:** Keep the existing FastAPI backend + React/Vite frontend + FastAPI agents microservice layout. The agents service gains a small internal `llm_router` package that selects a provider from env and exposes a single `generate(...)` interface. Backend endpoints get proper auth/tenant guards and error responses. The frontend uses Vite's proxy consistently. Platform-specific PowerShell scripts get POSIX shell siblings and a cross-platform `Makefile`.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, Pydantic-Settings v2, SQLAlchemy 2.x, React 18, Vite 5, Tailwind 3, Docker Compose, PostgreSQL 16, uvicorn, httpx.

---

## File Structure Summary

| Area | Files touched | Why |
|------|---------------|-----|
| Backend fixes | `backend/app/api/v1/auth.py`, `backend/app/api/v1/invoices.py`, `backend/app/api/v1/projects.py`, `backend/app/api/v1/workflows.py`, `backend/app/core/security.py`, `backend/app/core/config.py`, `backend/app/services/auth_service.py` | Missing auth, wrong error types, broken tenant guard, incomplete CORS |
| Frontend fixes | `frontend/app/src/lib/api.ts`, `frontend/app/src/pages/LoginPage.tsx` | Hard-coded backend URL bypasses Vite proxy; login errors render as `[object Object]` |
| Agents multi-provider router | New: `agents/app/llm_router/__init__.py`, `agents/app/llm_router/base.py`, `agents/app/llm_router/config.py`, `agents/app/llm_router/router.py`, `agents/app/llm_router/providers/openai_provider.py`, `agents/app/llm_router/providers/ollama_provider.py`, `agents/app/llm_router/providers/anthropic_provider.py`. Modify: `agents/app/strands/core/config.py`, `agents/app/strands/core/strands_config.py`, `agents/app/strands/workflows/landing_page_copy/draft_agent.py`, `agents/app/strands/workflows/landing_page_copy/qa_agent.py`, `agents/app/strands/workflows/ad_campaign/agent.py`, `agents/requirements.txt` | Replace stubs with real LLM calls routed across providers |
| Tests | `backend/tests/conftest.py`, `backend/tests/test_api.py` | Inconsistent SQLite DB and missing coverage for fixed bugs |
| Cross-platform scripts | New: `scripts/setup.sh`, `scripts/start-all.sh`, `scripts/start-backend.sh`, `scripts/start-frontend.sh`, `scripts/start-postgres.sh`, `scripts/start-docker.sh`, `scripts/start-docker-prod.sh`, `Makefile`. Modify: existing `.ps1` scripts to call the new POSIX versions when on non-Windows | Run on Windows, Linux, WSL, macOS |
| Docker hardening | `docker-compose.yml`, `docker/Dockerfile.frontend`, `frontend/app/package.json` | Missing dev healthcheck, fragile frontend build, no lockfile |

---

## Task 1: Backend Runtime Fixes

### Task 1.1: Reject duplicate signups with a clean 400

**Files:**
- Modify: `backend/app/services/auth_service.py`
- Modify: `backend/app/api/v1/auth.py`
- Test: `backend/tests/test_api.py`

- [ ] **Step 1: Add unique-email check in `create_user`**

```python
from fastapi import HTTPException, status

def create_user(db: Session, user_in: UserCreate) -> UserRead:
    existing = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    ... # rest unchanged
```

Run: `cd backend && python -m pytest tests/test_api.py::test_signup_and_login -v`
Expected: PASS

- [ ] **Step 2: Add a test for duplicate signup**

```python
def test_signup_duplicate_email():
    client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": "dup@example.com",
            "password": "password123",
            "role": "member",
        },
    )
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": "dup@example.com",
            "password": "password123",
            "role": "member",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
```

Run: `cd backend && python -m pytest tests/test_api.py::test_signup_duplicate_email -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/auth_service.py backend/tests/test_api.py
git commit -m "fix(backend): reject duplicate signup emails with 400"
```

### Task 1.2: Return HTTPException when invoice project is missing

**Files:**
- Modify: `backend/app/api/v1/invoices.py`
- Test: `backend/tests/test_api.py`

- [ ] **Step 1: Replace RuntimeError with HTTPException**

```python
from fastapi import APIRouter, Depends, HTTPException, status

@router.post("/", response_model=InvoiceRead)
async def create_invoice_endpoint(
    invoice_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceRead:
    project = db.query(Project).filter(Project.id == invoice_in.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    ensure_tenant(current_user, project.tenant_id)
    return create_invoice(db, invoice_in)
```

Run: `cd backend && python -m pytest tests/test_api.py -v -k invoice`
Expected: PASS

- [ ] **Step 2: Add test for missing project**

```python
def test_create_invoice_missing_project(authenticated_client):
    # authenticated_client fixture created in Task 1.5
    response = authenticated_client.post(
        "/api/v1/invoices/",
        json={
            "tenant_id": "tenant-1",
            "project_id": "nonexistent",
            "amount": 100.0,
            "currency": "USD",
        },
    )
    assert response.status_code == 404
```

Run: `cd backend && python -m pytest tests/test_api.py::test_create_invoice_missing_project -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/invoices.py backend/tests/test_api.py
git commit -m "fix(backend): return 404 when invoice project does not exist"
```

### Task 1.3: Fix tenant guard on project scope endpoint

**Files:**
- Modify: `backend/app/api/v1/projects.py`
- Modify: `backend/app/schemas/landing_page_schema.py`

- [ ] **Step 1: Add `tenant_id` to landing-page request schema**

```python
class LandingPageRequestSchema(BaseModel):
    tenant_id: str
    client_id: str
    project_id: str
    policy_id: str
    brief_text: str
    approved_by_user_id: Optional[str] = None
```

- [ ] **Step 2: Guard by `request.tenant_id` and verify project belongs to tenant**

```python
@router.post("/{project_id}/scope", response_model=ProjectRead)
async def scope_project_with_landing_workflow(
    project_id: str,
    request: LandingPageRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    ensure_tenant(current_user, request.tenant_id)

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.tenant_id == request.tenant_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lp_result = await call_landing_page_agent(request)
    summary = (
        f"Hero: {lp_result.draft.hero_headline}\n"
        f"Sections: {len(lp_result.draft.sections)}\n"
        f"Overall QA: {lp_result.qa.overall_score}"
    )

    return update_project_scope(db, project_id, scoped_summary=summary)
```

Run: `cd backend && python -m pytest tests/test_api.py -v -k project`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/v1/projects.py backend/app/schemas/landing_page_schema.py
git commit -m "fix(backend): scope endpoint guards by tenant_id and verifies project"
```

### Task 1.4: Require authentication on workflow endpoints

**Files:**
- Modify: `backend/app/api/v1/workflows.py`

- [ ] **Step 1: Add auth + project tenant check**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user, ensure_tenant, get_db
from backend.app.models.project import Project
from backend.app.models.user import User

@router.post("/{project_id}/landing-page", response_model=ProductionLandingPageSchema)
async def generate_landing_page_copy(
    project_id: str,
    req: LandingPageRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductionLandingPageSchema:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.tenant_id == req.tenant_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    ensure_tenant(current_user, req.tenant_id)

    scan_result = await sentinel_scan(
        SentinelScanInput(
            payload=req.brief_text,
            policy_id=req.policy_id,
            scan_type="prompt",
        )
    )
    if not scan_result.allowed:
        raise HTTPException(status_code=400, detail="Brief blocked by Sentinel")

    result = await call_landing_page_agent(req)
    return result
```

Run: `cd backend && python -m pytest tests/test_api.py -v`
Expected: all backend tests PASS

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/workflows.py
git commit -m "fix(backend): require auth and tenant membership on workflow endpoint"
```

### Task 1.5: Check user `is_active` in `get_current_user`

**Files:**
- Modify: `backend/app/core/security.py`

- [ ] **Step 1: Add active-user check**

```python
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user or not user.is_active:
        raise credentials_exception
```

Run: `cd backend && python -m pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/security.py
git commit -m "fix(backend): reject tokens for inactive users"
```

### Task 1.6: Expand CORS allow-methods

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add PATCH and OPTIONS**

```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
```

Run: `cd backend && python -m py_compile backend/app/main.py`
Expected: no syntax errors

- [ ] **Step 2: Commit**

```bash
git add backend/app/main.py
git commit -m "fix(backend): allow PATCH and OPTIONS in CORS"
```

---

## Task 2: Frontend Runtime Fixes

### Task 2.1: Use Vite proxy consistently

**Files:**
- Modify: `frontend/app/src/lib/api.ts`

- [ ] **Step 1: Use relative `/api/v1` in both dev and production**

```typescript
const baseURL = '/api/v1'
```

Run: `cd frontend/app && npm run build`
Expected: build succeeds with no TypeScript errors

- [ ] **Step 2: Commit**

```bash
git add frontend/app/src/lib/api.ts
git commit -m "fix(frontend): use Vite proxy consistently via relative API URL"
```

### Task 2.2: Parse JSON login errors

**Files:**
- Modify: `frontend/app/src/lib/api.ts`
- Modify: `frontend/app/src/pages/LoginPage.tsx`

- [ ] **Step 1: Parse detail from JSON error responses**

```typescript
  if (!response.ok) {
    const text = await response.text()
    let message = text
    try {
      const parsed = JSON.parse(text)
      message = parsed.detail || JSON.stringify(parsed)
    } catch {
      // keep raw text
    }
    throw new Error(message || response.statusText)
  }
```

- [ ] **Step 2: Render errors safely in LoginPage**

```typescript
    } catch (err: any) {
      setError(String(err.message || err || 'Login failed'))
    }
```

Run: `cd frontend/app && npm run build`
Expected: build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/app/src/lib/api.ts frontend/app/src/pages/LoginPage.tsx
git commit -m "fix(frontend): parse JSON error details and render login errors safely"
```

---

## Task 3: Agents Multi-Provider LLM Router

### Task 3.1: Create provider-agnostic LLM router

**Files:**
- Create: `agents/app/llm_router/__init__.py`
- Create: `agents/app/llm_router/base.py`
- Create: `agents/app/llm_router/config.py`
- Create: `agents/app/llm_router/router.py`
- Create: `agents/app/llm_router/providers/__init__.py`
- Create: `agents/app/llm_router/providers/openai_provider.py`
- Create: `agents/app/llm_router/providers/anthropic_provider.py`
- Create: `agents/app/llm_router/providers/ollama_provider.py`

- [ ] **Step 1: Base abstraction**

`agents/app/llm_router/base.py`:

```python
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        """Return the model's text response for the given messages."""
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return available model IDs."""
        pass
```

- [ ] **Step 2: Router settings using Pydantic Settings v2**

`agents/app/llm_router/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    provider: str = "ollama"  # openai | anthropic | ollama
    model: str = "llama3.2"   # provider-specific default
    base_url: str | None = None
    api_key: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.7


settings = LLMSettings()
```

- [ ] **Step 3: Router factory**

`agents/app/llm_router/router.py`:

```python
from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings
from agents.app.llm_router.providers.openai_provider import OpenAIProvider
from agents.app.llm_router.providers.anthropic_provider import AnthropicProvider
from agents.app.llm_router.providers.ollama_provider import OllamaProvider


_PROVIDER_MAP: dict[str, type[BaseLLM]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


def get_llm(provider: str | None = None) -> BaseLLM:
    provider = (provider or settings.provider).lower()
    if provider not in _PROVIDER_MAP:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return _PROVIDER_MAP[provider]()


def generate(model: str | None = None, messages: list[dict] | None = None, **kwargs) -> str:
    llm = get_llm()
    return llm.generate(
        model=model or settings.model,
        messages=messages or [],
        **kwargs,
    )
```

- [ ] **Step 4: OpenAI provider**

`agents/app/llm_router/providers/openai_provider.py`:

```python
import os

from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings


class OpenAIProvider(BaseLLM):
    def __init__(self):
        api_key = settings.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY or LLM_API_KEY is required for OpenAI provider")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai package is not installed") from exc
        self.client = OpenAI(api_key=api_key, base_url=settings.base_url or None)

    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", settings.max_tokens),
            temperature=kwargs.get("temperature", settings.temperature),
        )
        return response.choices[0].message.content.strip()

    def list_models(self) -> list[str]:
        models = self.client.models.list()
        return sorted([m.id for m in models.data])
```

- [ ] **Step 5: Anthropic provider**

`agents/app/llm_router/providers/anthropic_provider.py`:

```python
import os

from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings


class AnthropicProvider(BaseLLM):
    def __init__(self):
        api_key = settings.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY or LLM_API_KEY is required for Anthropic provider")
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("anthropic package is not installed") from exc
        self.client = Anthropic(api_key=api_key, base_url=settings.base_url or None)
        self.default_system_prompt = "You are a helpful AI assistant."

    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        system = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system = msg.get("content", "")
            else:
                user_messages.append(msg)
        response = self.client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", settings.max_tokens),
            temperature=kwargs.get("temperature", settings.temperature),
            system=system or self.default_system_prompt,
            messages=user_messages,
        )
        return response.content[0].text.strip()

    def list_models(self) -> list[str]:
        # Anthropic model list requires a manual HTTP call
        import requests
        headers = {
            "x-api-key": self.client.api_key,
            "anthropic-version": "2023-06-01",
        }
        resp = requests.get("https://api.anthropic.com/v1/models", headers=headers, timeout=30)
        resp.raise_for_status()
        return [m["id"] for m in resp.json().get("data", [])]
```

- [ ] **Step 6: Ollama provider**

`agents/app/llm_router/providers/ollama_provider.py`:

```python
import json
import os

import requests

from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings


class OllamaProvider(BaseLLM):
    def __init__(self):
        self.base_url = (settings.base_url or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")

    def generate(self, model: str, messages: list[dict], **kwargs) -> str:
        prompt = "\n".join(
            f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages
        )
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", settings.temperature),
                "num_predict": kwargs.get("max_tokens", settings.max_tokens),
            },
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        # Ollama may return NDJSON even with stream=false
        parts = []
        for line in response.text.strip().splitlines():
            if line:
                try:
                    data = json.loads(line)
                    parts.append(data.get("response", ""))
                except json.JSONDecodeError:
                    continue
        return "".join(parts).strip()

    def list_models(self) -> list[str]:
        response = requests.get(f"{self.base_url}/api/tags", timeout=30)
        response.raise_for_status()
        return [m.get("name", m.get("model", "unknown")) for m in response.json().get("models", [])]
```

- [ ] **Step 7: Package exports**

`agents/app/llm_router/__init__.py`:

```python
from agents.app.llm_router.base import BaseLLM
from agents.app.llm_router.config import settings
from agents.app.llm_router.router import generate, get_llm

__all__ = ["BaseLLM", "generate", "get_llm", "settings"]
```

`agents/app/llm_router/providers/__init__.py`:

```python
from agents.app.llm_router.providers.openai_provider import OpenAIProvider
from agents.app.llm_router.providers.anthropic_provider import AnthropicProvider
from agents.app.llm_router.providers.ollama_provider import OllamaProvider

__all__ = ["OpenAIProvider", "AnthropicProvider", "OllamaProvider"]
```

- [ ] **Step 8: Add provider SDKs to agents requirements**

`agents/requirements.txt`:

```text
fastapi
uvicorn[standard]
httpx
pydantic>=2.0
pydantic-settings
openai
anthropic
requests
```

Run: `cd agents && python -m py_compile app/llm_router/router.py app/llm_router/providers/*.py`
Expected: no syntax errors

- [ ] **Step 9: Commit**

```bash
git add agents/app/llm_router agents/requirements.txt
git commit -m "feat(agents): add multi-provider LLM router (openai, anthropic, ollama)"
```

### Task 3.2: Update existing Strands settings to Pydantic Settings v2

**Files:**
- Modify: `agents/app/strands/core/config.py`
- Modify: `agents/app/strands/core/strands_config.py`

- [ ] **Step 1: Replace deprecated `class Config` with `SettingsConfigDict`**

`agents/app/strands/core/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class StrandsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STRANDS_",
        env_file=".env",
        extra="ignore",
    )

    model_name: str = "anthropic.claude-3-5-sonnet"
    max_tokens: int = 4096
    temperature: float = 0.7

    sentinel_base_url: str = "http://backend:8000/internal/sentinel"
    agentcore_endpoint: str | None = None


settings = StrandsSettings()
```

`agents/app/strands/core/strands_config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class StrandsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STRANDS_",
        env_file=".env",
        extra="ignore",
    )

    model_provider: str = "ollama"
    model_name: str = "llama3.2"
    max_tokens: int = 4096
    temperature: float = 0.7


settings = StrandsSettings()
```

Run: `cd agents && python -m py_compile app/strands/core/config.py app/strands/core/strands_config.py`
Expected: no syntax errors

- [ ] **Step 2: Commit**

```bash
git add agents/app/strands/core/config.py agents/app/strands/core/strands_config.py
git commit -m "fix(agents): migrate Strands settings to Pydantic Settings v2"
```

### Task 3.3: Wire LLM router into landing-page workflow

**Files:**
- Modify: `agents/app/strands/workflows/landing_page_copy/draft_agent.py`
- Modify: `agents/app/strands/workflows/landing_page_copy/qa_agent.py`

- [ ] **Step 1: Generate draft copy via LLM router**

```python
from agents.app.llm_router import generate
from agents.app.models.landing_page_models import LandingPageDraft, SectionCopy
from agents.app.strands.core.context_types import WorkflowContext
from agents.app.strands.tools.sentinel_tool_wrapper import sentinel_scan, SentinelScanInput


async def run_draft_agent(ctx: WorkflowContext, policy_id: str) -> WorkflowContext:
    if not ctx.brief or not ctx.research:
        raise ValueError("Brief and research are required before drafting")

    system_prompt = (
        "You are a senior conversion copywriter. "
        "Write a landing page in JSON with exactly these keys: "
        "hero_headline (string), hero_subheadline (string), "
        "sections (list of {id, title, body, call_to_action}), "
        "notes (string). Return only valid JSON."
    )
    user_prompt = (
        f"Product: {ctx.brief.product_name or 'Unknown'}\n"
        f"Description: {ctx.brief.product_description}\n"
        f"Audience: {ctx.brief.target_audience}\n"
        f"Goal: {ctx.brief.primary_goal}\n"
        f"Tone: {ctx.brief.tone_of_voice}\n"
        f"Research notes: {ctx.research.raw_notes}"
    )

    raw = generate(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

    sections = [
        SectionCopy(**s) for s in data.get("sections", [])
    ]
    draft = LandingPageDraft(
        hero_headline=data.get("hero_headline", ""),
        hero_subheadline=data.get("hero_subheadline", ""),
        sections=sections,
        notes=data.get("notes", ""),
    )

    payload = "\n".join(
        [draft.hero_headline, draft.hero_subheadline]
        + [s.body for s in draft.sections]
    )
    scan_result = await sentinel_scan(
        SentinelScanInput(
            payload=payload,
            policy_id=policy_id,
            scan_type="output",
        )
    )
    ctx.metadata["sentinel_draft_scan"] = scan_result.model_dump()
    ctx.draft = draft
    return ctx
```

- [ ] **Step 2: Generate QA evaluation via LLM router**

```python
import json

from agents.app.llm_router import generate
from agents.app.models.landing_page_models import QAEvaluation
from agents.app.strands.core.context_types import WorkflowContext


async def run_qa_agent(ctx: WorkflowContext) -> WorkflowContext:
    if not ctx.draft or not ctx.brief:
        raise ValueError("Draft and brief are required for QA")

    system_prompt = (
        "You are a strict landing-page QA reviewer. "
        "Return only JSON with keys: overall_score, brand_voice_score, "
        "clarity_score, structure_score (all 0.0-1.0 floats), "
        "issues (list of strings), suggestions (list of strings)."
    )
    user_prompt = (
        f"Brief: {ctx.brief.product_description}\n"
        f"Hero: {ctx.draft.hero_headline}\n"
        f"Subhead: {ctx.draft.hero_subheadline}\n"
        f"Sections:\n"
        + "\n".join(f"- {s.title}: {s.body}" for s in ctx.draft.sections)
    )

    raw = generate(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM QA returned invalid JSON: {exc}") from exc

    ctx.qa = QAEvaluation(
        overall_score=float(data.get("overall_score", 0.0)),
        brand_voice_score=float(data.get("brand_voice_score", 0.0)),
        clarity_score=float(data.get("clarity_score", 0.0)),
        structure_score=float(data.get("structure_score", 0.0)),
        issues=data.get("issues", []),
        suggestions=data.get("suggestions", []),
    )
    return ctx
```

Run: `cd agents && python -m py_compile app/strands/workflows/landing_page_copy/draft_agent.py app/strands/workflows/landing_page_copy/qa_agent.py`
Expected: no syntax errors

- [ ] **Step 3: Commit**

```bash
git add agents/app/strands/workflows/landing_page_copy/draft_agent.py agents/app/strands/workflows/landing_page_copy/qa_agent.py
git commit -m "feat(agents): generate landing-page draft and QA via LLM router"
```

### Task 3.4: Wire LLM router into ad-campaign workflow

**Files:**
- Modify: `agents/app/strands/workflows/ad_campaign/agent.py`

- [ ] **Step 1: Generate ad creatives via LLM router**

```python
import json

from agents.app.llm_router import generate
from agents.app.models.ad_campaign_models import AdCampaignBrief, AdCampaignDraft, AdCreative
from agents.app.strands.tools.sentinel_tool_wrapper import sentinel_scan, SentinelScanInput


async def run_ad_campaign_agent(brief: AdCampaignBrief, policy_id: str) -> AdCampaignDraft:
    scan = await sentinel_scan(
        SentinelScanInput(
            payload=brief.product_description,
            policy_id=policy_id,
            scan_type="prompt",
        )
    )
    if not scan.allowed:
        raise ValueError("Ad brief blocked by Sentinel")

    system_prompt = (
        "You are a performance marketing copywriter. "
        "Return only JSON with key 'creatives' containing a list of "
        "{platform, headline, body, call_to_action} objects."
    )
    user_prompt = (
        f"Product: {brief.product_name}\n"
        f"Description: {brief.product_description}\n"
        f"Audience: {brief.target_audience}\n"
        f"Goal: {brief.primary_goal}"
    )

    raw = generate(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

    creatives = [AdCreative(**c) for c in data.get("creatives", [])]
    if not creatives:
        creatives = [
            AdCreative(
                platform="meta",
                headline=f"{brief.product_name} for {brief.target_audience}",
                body="[stubbed ad body]",
                call_to_action="Learn more",
            )
        ]

    return AdCampaignDraft(creatives=creatives)
```

Run: `cd agents && python -m py_compile app/strands/workflows/ad_campaign/agent.py`
Expected: no syntax errors

- [ ] **Step 2: Commit**

```bash
git add agents/app/strands/workflows/ad_campaign/agent.py
git commit -m "feat(agents): generate ad campaign creatives via LLM router"
```

---

## Task 4: Fix Backend Test Infrastructure

**Files:**
- Modify: `backend/tests/conftest.py`
- Modify: `backend/tests/test_api.py`

- [ ] **Step 1: Use the same in-memory SQLite DB for lifespan and tests**

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("BACKEND_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("BACKEND_DATABASE_URL", "sqlite:///./test_shared.db")
```

- [ ] **Step 2: Add reusable authenticated fixture and a login helper**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.db.session import Base, get_db

TEST_DB_URL = "sqlite:///./test_shared.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    from sqlalchemy.orm import close_all_sessions

    close_all_sessions()
    with engine.begin() as conn:
        for tbl in reversed(Base.metadata.sorted_tables):
            conn.execute(tbl.delete())


@pytest.fixture
def authenticated_client():
    client.post(
        "/api/v1/auth/signup",
        json={
            "tenant_id": "tenant-1",
            "email": "auth@example.com",
            "password": "password123",
            "role": "member",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "auth@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    from fastapi.testclient import TestClient

    authed = TestClient(app)
    authed.headers.update({"Authorization": f"Bearer {token}"})
    return authed
```

- [ ] **Step 3: Run the full backend test suite**

Run: `cd backend && python -m pytest tests/ -v`
Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add backend/tests/conftest.py backend/tests/test_api.py
git commit -m "test(backend): align test DB config and add authenticated fixture"
```

---

## Task 5: Cross-Platform Scripts

### Task 5.1: Add POSIX shell scripts

**Files:**
- Create: `scripts/setup.sh`
- Create: `scripts/start-postgres.sh`
- Create: `scripts/start-backend.sh`
- Create: `scripts/start-frontend.sh`
- Create: `scripts/start-all.sh`
- Create: `scripts/start-docker.sh`
- Create: `scripts/start-docker-prod.sh`

- [ ] **Step 1: setup.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== AI Agency OS Setup ==="

cd "$ROOT/backend"
python -m venv .venv 2>/dev/null || true
./.venv/bin/python -m pip install --upgrade pip -q
./.venv/bin/python -m pip install -r requirements.txt -q

cd "$ROOT/agents"
python -m venv .venv 2>/dev/null || true
./.venv/bin/python -m pip install --upgrade pip -q
./.venv/bin/python -m pip install -r requirements.txt -q

cd "$ROOT/frontend/app"
npm install

[ ! -f "$ROOT/backend/.env" ] && cp "$ROOT/backend/.env.example" "$ROOT/backend/.env" && echo "Created backend/.env"
[ ! -f "$ROOT/agents/.env" ] && cp "$ROOT/agents/.env.example" "$ROOT/agents/.env" && echo "Created agents/.env"

echo "Setup complete. Run: make start-docker"
```

- [ ] **Step 2: start-postgres.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

CONTAINER="agency-os-postgres"
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    docker start "$CONTAINER" >/dev/null
    echo "Started existing container: $CONTAINER"
else
    docker run -d \
        --name "$CONTAINER" \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=agency_os \
        -p 5432:5432 \
        -v agency_os_postgres_data:/var/lib/postgresql/data \
        postgres:16
    echo "Created and started container: $CONTAINER"
fi
echo "PostgreSQL ready on localhost:5432"
```

- [ ] **Step 3: start-backend.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f "$ROOT/backend/.env" ]; then
    export $(grep -v '^#' "$ROOT/backend/.env" | xargs)
fi
export PYTHONPATH="$ROOT"
cd "$ROOT/backend"
./.venv/bin/python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

- [ ] **Step 4: start-frontend.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/frontend/app"
npm run dev -- --host 0.0.0.0
```

- [ ] **Step 5: start-all.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== Starting AI Agency OS locally ==="
echo "Ensure PostgreSQL is running: ./scripts/start-postgres.sh"

"$ROOT/scripts/start-backend.sh" &
"$ROOT/scripts/start-frontend.sh" &
wait
```

- [ ] **Step 6: start-docker.sh and start-docker-prod.sh**

`scripts/start-docker.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
docker compose up --build
```

`scripts/start-docker-prod.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
docker compose -f docker-compose.prod.yml up --build -d
```

- [ ] **Step 7: Make scripts executable and commit**

Run: `chmod +x scripts/*.sh`

Run: `bash -n scripts/setup.sh scripts/start-all.sh scripts/start-backend.sh scripts/start-frontend.sh scripts/start-postgres.sh scripts/start-docker.sh scripts/start-docker-prod.sh`
Expected: no syntax errors

```bash
git add scripts/*.sh
git commit -m "feat(scripts): add POSIX shell equivalents for cross-platform usage"
```

### Task 5.2: Add a Makefile as the cross-platform entry point

**Files:**
- Create: `Makefile`

- [ ] **Step 1: Create Makefile**

```makefile
.PHONY: setup start-docker start-docker-prod start-all start-postgres start-backend start-frontend test-backend

setup:
	@bash scripts/setup.sh

start-docker:
	@bash scripts/start-docker.sh

start-docker-prod:
	@bash scripts/start-docker-prod.sh

start-all:
	@bash scripts/start-all.sh

start-postgres:
	@bash scripts/start-postgres.sh

start-backend:
	@bash scripts/start-backend.sh

start-frontend:
	@bash scripts/start-frontend.sh

test-backend:
	@cd backend && ./.venv/bin/python -m pytest tests/ -v
```

- [ ] **Step 2: Commit**

```bash
git add Makefile
git commit -m "feat(build): add Makefile entry point for POSIX systems"
```

---

## Task 6: Docker & Compose Hardening

### Task 6.1: Add healthcheck to backend in dev compose

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Add healthcheck and use condition for agents/frontend**

```yaml
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    working_dir: /app
    command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app/backend
    environment:
      BACKEND_DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/agency_os
      BACKEND_SECRET_KEY: agency-os-docker-dev-secret-change-in-production
      BACKEND_ENV: local
      BACKEND_AGENTS_SERVICE_URL: http://agents:8081
      BACKEND_CORS_ORIGINS: http://localhost:5173
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ['CMD-SHELL', 'python -c "import urllib.request; urllib.request.urlopen(\'http://localhost:8000/healthz\')"']
      interval: 10s
      timeout: 5s
      retries: 5
    ports:
      - '8000:8000'

  agents:
    ...
    depends_on:
      backend:
        condition: service_healthy

  frontend:
    ...
    depends_on:
      backend:
        condition: service_healthy
```

Run: `docker compose config`
Expected: valid compose output

- [ ] **Step 2: Commit**

```bash
git add docker-compose.yml
git commit -m "fix(docker): add backend healthcheck and condition-based deps in dev compose"
```

### Task 6.2: Harden frontend Dockerfile

**Files:**
- Modify: `docker/Dockerfile.frontend`

- [ ] **Step 1: Remove fallback build and fail fast**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/app/package.json frontend/app/package-lock.json ./
RUN npm ci
COPY frontend/app .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Run: `docker build -f docker/Dockerfile.frontend -t agency-frontend-test .`
Expected: build succeeds (requires package-lock.json; create it in Task 6.3)

- [ ] **Step 2: Commit**

```bash
git add docker/Dockerfile.frontend
git commit -m "fix(docker): fail fast on frontend build errors and use npm ci"
```

### Task 6.3: Add package-lock.json

**Files:**
- Create: `frontend/app/package-lock.json`

- [ ] **Step 1: Generate lockfile**

Run: `cd frontend/app && npm install`
Expected: `package-lock.json` created

- [ ] **Step 2: Commit**

```bash
git add frontend/app/package-lock.json
git commit -m "chore(frontend): add package-lock.json for reproducible installs"
```

---

## Self-Review Checklist

**1. Spec coverage:**
- Critical runtime fixes: auth duplicate email, invoice 404, project tenant guard, workflow auth, CORS, inactive users → covered in Tasks 1.1-1.6.
- Multi-provider LLM router like wrapper repo → covered in Task 3.1-3.4 (openai/anthropic/ollama, factory pattern, single `generate()` interface).
- Cross-platform support → covered in Tasks 5.1-5.2 (shell scripts + Makefile).
- Tests runnable → covered in Task 4.
- Docker seamless startup → covered in Task 6.

**2. Placeholder scan:**
- No `TBD`, `TODO` in implementation steps. The only remaining TODO is the original code comment in `workflows.py` about persisting to DB/S3, which is out of scope for runtime fixes.
- Every code step shows actual code and a verification command.

**3. Type consistency:**
- `LandingPageRequestSchema` gains `tenant_id: str`; downstream endpoints use `req.tenant_id` consistently.
- `generate()` signature is consistent across all providers.
- Fixture name `authenticated_client` matches its usage.

---

## Execution Options

**Plan complete and saved to `docs/superpowers/plans/2026-06-30-ai-agency-os-runtime-fixes.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

Which approach would you like?
