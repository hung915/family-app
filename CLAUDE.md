# CLAUDE.md

This file is the source of truth for Claude Code when working in this repository. Read it before doing anything. Re-read it if you've been working for a long time and feel uncertain about conventions.

---

## Project: Family App

A private fullstack web application for our family. It is a digital home for memories, milestones, and day-to-day life — including a pregnancy tracker for our baby on the way.

### The family

- **Father** (the primary developer / account owner)
- **Mother** (currently pregnant)
- **Older sister** (firstborn child)
- **Baby** (in mother's womb — tracked via the `pregnancy` module until birth)

These are the only humans the app needs to serve. There is no public sign-up. Auth is invitation-only and built around magic-link email.

---

## Tech stack

| Layer       | Choice                                                  |
|-------------|---------------------------------------------------------|
| Backend     | FastAPI (async), SQLAlchemy 2.0 async, Alembic, Pydantic v2 |
| Database    | PostgreSQL (Neon in production, local Postgres in dev)  |
| Frontend    | Vite + React 18 + TypeScript                            |
| UI          | Tailwind CSS + shadcn/ui + lucide-react                 |
| Data fetching | TanStack Query + openapi-fetch (typed from FastAPI)   |
| Forms       | react-hook-form + zod                                   |
| Auth        | Passwordless magic-link (email)                         |
| File storage | Cloudflare R2 (signed URLs)                            |
| Python deps | `uv`                                                    |
| JS deps     | `pnpm` (workspaces)                                     |
| Lint/format | `ruff` (Python), `eslint` + `prettier` (JS)             |
| Hosting     | Render (web service for API, static site for frontend)  |
| CI/CD       | GitHub Actions for tests; Render auto-deploys on green main |

---

## Repository layout

```
family-app/
├── .claude/                   # Skills, agents, custom commands for Claude Code
│   ├── skills/
│   ├── agents/
│   └── commands/
├── .github/workflows/         # CI pipelines
├── backend/
│   ├── alembic/
│   ├── src/
│   │   ├── <domain>/          # one folder per domain module
│   │   ├── config.py          # global settings
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   ├── models.py          # CustomModel base
│   │   ├── pagination.py
│   │   └── main.py
│   └── tests/<domain>/
├── frontend/
│   └── src/
│       ├── features/<domain>/ # one folder per UI feature
│       ├── components/ui/     # shadcn primitives — do not edit manually
│       ├── lib/
│       ├── pages/
│       ├── App.tsx
│       └── main.tsx
├── render.yaml                # infrastructure-as-code for Render
└── CLAUDE.md                  # you are here
```

---

## Domain modules (current)

The backend is organized **by domain**, never by file type. Each domain is a self-contained package.

| Module       | Purpose                                                            |
|--------------|--------------------------------------------------------------------|
| `auth`       | Magic-link login, JWT issuance, current-user dependency            |
| `family`     | The household unit; relationships between members                  |
| `members`    | Profiles for father, mother, sister, kids                          |
| `pregnancy`  | Week tracker, kick counter, appointments, ultrasound photos        |
| `milestones` | First words, first steps, birthdays, school events                 |
| `memories`   | Photos, journal entries, voice notes                               |

When the baby is born, the `pregnancy` record graduates into a new `members` row (`role` flips from `UNBORN` to `CHILD`, `due_date` → `birth_date`). This transition lives in `src/pregnancy/service.py::graduate_to_member`.

---

## Backend conventions (non-negotiable)

These follow [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices). When in doubt, that document wins.

### File layout per domain

Every domain module has exactly these files (omit a file only if it would be empty):

```
src/<domain>/
├── __init__.py
├── router.py        # all endpoints for this domain
├── schemas.py       # Pydantic request/response models
├── models.py        # SQLAlchemy ORM models
├── service.py       # business logic, DB queries
├── dependencies.py  # FastAPI Depends(...) — validation, auth, ownership
├── exceptions.py    # domain-specific exceptions (e.g. MemberNotFound)
├── constants.py     # error codes, enums, magic strings
├── config.py        # ONLY if this domain reads its own env vars
└── utils.py         # ONLY for non-business helpers
```

### Routes

- **Default to `async def`** for routes and dependencies.
- Never call blocking I/O inside an `async` route. If you must use a sync SDK, wrap it with `fastapi.concurrency.run_in_threadpool`.
- Document every route: `response_model`, `status_code`, `summary`, `description`, `tags`.
- Hide `/docs` and `/redoc` outside `local` and `staging` environments (see `src/main.py`).

### Pydantic

- All schemas inherit from `src.models.CustomModel`, which standardizes datetime serialization to GMT ISO-8601.
- Use Pydantic features aggressively: `Field(min_length=, max_length=, pattern=)`, `EmailStr`, `AnyUrl`, `StrEnum`. Validate at the schema layer; do not re-validate in services.
- A `ValueError` raised in a `field_validator` becomes a clean 422 — use it.

### Settings

- Each domain that needs env vars has its own `BaseSettings` subclass in `<domain>/config.py`. **Do not put domain-specific vars in `src/config.py`.**
- Global vars live in `src/config.py::Config`.

### Dependencies

- Use dependencies for **validation, not just DI**. `valid_member_id`, `valid_owned_memory`, etc., return the loaded object so routes never refetch.
- Chain dependencies; FastAPI caches them within a request scope.
- Prefer `async def` dependencies even when no `await` happens — avoids the threadpool overhead.

### Database

- Async SQLAlchemy 2.0 only. No sync sessions anywhere.
- Naming convention is set explicitly on `MetaData` (see `src/database.py`). Do not change it.
- Table names: `lower_snake_case`, **singular** (`member`, not `members`; `memory`, not `memories`).
- Column suffixes: `_at` for `datetime`, `_date` for `date`, `_id` for FKs.
- Prefer SQL-side aggregation (`json_build_object`, joins) over Python loops when shaping responses.

### Migrations

- Always autogenerate, then **read the migration before committing it**. Edit if Alembic guessed wrong.
- Migrations must be reversible: `downgrade()` is mandatory.
- File template (set in `alembic.ini`): `%%(year)d-%%(month).2d-%%(day).2d_%%(slug)s`.
- Slug is required and descriptive: `2026-04-30_add_pregnancy_kick_log.py`, not `migration1.py`.

### Tests

- `pytest` + `pytest-asyncio` + async test client (`async-asgi-testclient` or `httpx.AsyncClient`).
- Mirror the source layout: `tests/<domain>/test_router.py`, `test_service.py`.
- Every new endpoint gets at least a happy-path and one validation-error test.

### Lint/format

- Run `uv run ruff check src --fix && uv run ruff format src` before committing. CI will fail on diff.

---

## Frontend conventions

### File layout per feature

```
src/features/<domain>/
├── api.ts           # typed API calls using openapi-fetch
├── hooks.ts         # TanStack Query hooks (useMembers, useCreateMember, ...)
├── schemas.ts       # zod schemas for forms
├── components/      # presentational components for this feature
├── routes.tsx       # route definitions
└── index.ts         # public exports
```

### Conventions

- **Types come from the backend.** Run `pnpm gen:api` after any backend schema change. Never hand-write types that mirror Pydantic schemas.
- All server state goes through TanStack Query. Never `useEffect(fetch)` directly.
- Forms: `react-hook-form` + `zod`. The zod schema in `schemas.ts` should match (or be a subset of) the generated backend type.
- UI primitives come from `components/ui/` (shadcn). Do not edit those files; if a primitive is wrong, override via Tailwind in the consumer.
- Tailwind only. No CSS modules, no styled-components.

---

## Workflow Claude Code should follow

When asked to **add a new backend domain module**:
1. Read this file.
2. Invoke the `fastapi-module` skill at `.claude/skills/fastapi-module/SKILL.md`.
3. Generate the full domain folder per the skill.
4. Generate matching tests under `backend/tests/<domain>/`.
5. Register the router in `src/main.py`.
6. Generate an Alembic migration; read it before committing.

When asked to **add a frontend feature**:
1. Confirm the backend endpoints exist (check `/docs` or the OpenAPI schema).
2. Run `pnpm gen:api` so types are fresh.
3. Invoke the `react-feature` skill.
4. Wire the new route into the router in `src/App.tsx` (or `pages/`).

When asked to **change a database schema**:
1. Edit `models.py` for the relevant domain.
2. Run `alembic revision --autogenerate -m "<descriptive_slug>"`.
3. Open the generated migration. Verify upgrade and downgrade. Edit if needed.
4. Run `alembic upgrade head` locally.
5. Update affected schemas, services, tests.
6. Bump the frontend types: `pnpm gen:api`.

When asked something **vague** ("make it nicer", "add a feature for the kids"):
- Ask one clarifying question. Do not guess and build the wrong thing.

---

## Things that are easy to get wrong

- **Singular table names.** It's `member`, not `members`. The route is `/members/{member_id}` (plural in URL, singular in DB) — that's deliberate REST style.
- **Path variable names must match across chained dependencies.** If `valid_member_id` reads `member_id`, every route that depends on it must use `member_id` in its path — not `user_id` or `id`.
- **Don't put auth checks inside services.** Auth and ownership go in dependencies. Services trust their inputs.
- **Don't use sync DB drivers.** `psycopg2` is forbidden; use `asyncpg`.
- **Don't return ORM objects from routes.** Always serialize via a Pydantic `response_model`.
- **CORS_ORIGINS must include the frontend's exact URL** (with scheme, no trailing slash). A wrong value = silent prod breakage.

---

## Useful commands

```bash
# Backend
cd backend
uv sync                                    # install deps
uv run uvicorn src.main:app --reload       # dev server
uv run alembic revision --autogenerate -m "slug"
uv run alembic upgrade head
uv run pytest
uv run ruff check src --fix && uv run ruff format src

# Frontend
cd frontend
pnpm install
pnpm dev
pnpm gen:api                               # regenerate types from backend
pnpm build
pnpm lint
```

---

## When you're unsure

Prefer the simpler option. This is a family app, not a startup. Ship the version that's easy to maintain in a year when the baby is crawling and there is no time to debug clever code.