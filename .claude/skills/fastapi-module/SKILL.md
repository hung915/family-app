---
name: fastapi-module
description: Scaffold a new domain module in the FastAPI backend following zhanymkanov/fastapi-best-practices. Use whenever the user asks to add a new domain (e.g. "add a `meals` module", "create a recipes feature", "scaffold the pregnancy module"). Produces router.py, schemas.py, models.py, service.py, dependencies.py, exceptions.py, constants.py, an Alembic migration, and matching tests.
---

# Skill: fastapi-module

## When to use this skill

Use this skill whenever you are asked to create a new domain module in the backend. Triggers include:

- "Add a `<name>` module/domain/feature."
- "Scaffold the backend for `<thing>`."
- "Create endpoints for `<thing>`."
- A new conceptual area appears in the conversation (e.g. user mentions tracking something the app does not yet model).

Do NOT use this skill for:

- Adding a new endpoint to an existing module (just edit the existing module's `router.py`).
- Pure DB schema changes to an existing module (use the `alembic-migration` skill).
- Frontend work (use the `react-feature` skill).

## Inputs to confirm before scaffolding

If any of these are unclear from the conversation, ask **one** clarifying question that bundles them together. Do not ask multiple rounds.

1. **Module name** — singular noun, lower_snake_case (e.g. `meal`, `appointment`, `kick_log`). The folder is `src/<module_name>/`. The URL prefix is the plural: `/meals`, `/appointments`, `/kick-logs`.
2. **Core entity fields** — minimum: name/title, plus the 2–4 fields that make this domain meaningful. Don't over-design; we can migrate later.
3. **Ownership model** — does a row belong to one family member, the whole family, or is it global? This determines the FK and the auth dependency.
4. **Auth requirement** — read-only for everyone logged in, or restricted to a specific member/role?

## Steps

### 1. Read context first

Before writing anything:

- Read `CLAUDE.md` at the repo root if you haven't already this session.
- Skim `backend/src/main.py` to see how existing routers are registered.
- Skim one existing domain (`backend/src/members/`) as the canonical reference for style. Match it.
- Check `backend/src/database.py` for the `Base` class and naming convention.

### 2. Create the folder and files

Create `backend/src/<module>/` with these files. Omit a file only if it would genuinely be empty (e.g. no `config.py` if the module reads no env vars).

```
backend/src/<module>/
├── __init__.py
├── router.py
├── schemas.py
├── models.py
├── service.py
├── dependencies.py
├── exceptions.py
├── constants.py
└── config.py        # only if needed
```

### 3. File contents

#### `__init__.py`

Empty file. Just create it.

#### `constants.py`

```python
from enum import StrEnum


class ErrorCode(StrEnum):
    NOT_FOUND = "<MODULE>_NOT_FOUND"
    ALREADY_EXISTS = "<MODULE>_ALREADY_EXISTS"
    # add domain-specific codes here
```

Replace `<MODULE>` with the uppercased module name. Add domain-specific codes only if you actually need them — don't speculate.

#### `exceptions.py`

```python
from src.exceptions import NotFound, BadRequest
from src.<module>.constants import ErrorCode


class <Entity>NotFound(NotFound):
    DETAIL = ErrorCode.NOT_FOUND


class <Entity>AlreadyExists(BadRequest):
    DETAIL = ErrorCode.ALREADY_EXISTS
```

`<Entity>` is the singular PascalCase form (e.g. `Meal`, `Appointment`, `KickLog`). The base classes `NotFound` and `BadRequest` come from `src/exceptions.py` — verify they exist there; if not, add them as thin wrappers around `HTTPException` with appropriate status codes.

#### `models.py`

```python
from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class <Entity>(Base):
    __tablename__ = "<module>"   # singular, lowercase

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # ... domain fields here ...
    member_id: Mapped[UUID] = mapped_column(ForeignKey("member.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow)
```

Rules:

- `__tablename__` is **singular**, lowercase, snake_case.
- Datetime columns end in `_at`, date columns end in `_date`.
- FKs end in `_id` and reference the singular table.
- Always include `created_at`. Include `updated_at` if the row is mutable.
- Use SQLAlchemy 2.0 typed `Mapped[]` syntax. Do not use the legacy `Column(...)` style.

#### `schemas.py`

Always define **at least three** schemas: a `Create`, an `Update`, and a `Response`. Never reuse one schema for input and output.

```python
from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import Field

from src.models import CustomModel


class <Entity>Base(CustomModel):
    # shared fields between create/update/response
    title: str = Field(min_length=1, max_length=128)


class <Entity>Create(<Entity>Base):
    # fields the client provides on create
    member_id: UUID


class <Entity>Update(CustomModel):
    # all fields optional for PATCH semantics
    title: str | None = Field(default=None, min_length=1, max_length=128)


class <Entity>Response(<Entity>Base):
    id: UUID
    member_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
```

Rules:

- Inherit from `CustomModel`, never `pydantic.BaseModel` directly.
- Use `Field(min_length=, max_length=, pattern=, ge=, le=)` to validate at the schema layer.
- For optional updates, all fields are `| None = None`. Use `model.model_dump(exclude_unset=True)` in the service.

#### `service.py`

Pure data access + business logic. **No FastAPI imports here.** Services take a session and primitives, return ORM objects or dicts.

```python
from __future__ import annotations
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.<module>.models import <Entity>
from src.<module>.schemas import <Entity>Create, <Entity>Update


async def get_by_id(session: AsyncSession, entity_id: UUID) -> <Entity> | None:
    result = await session.execute(select(<Entity>).where(<Entity>.id == entity_id))
    return result.scalar_one_or_none()


async def list_all(
    session: AsyncSession, *, limit: int = 50, offset: int = 0
) -> list[<Entity>]:
    result = await session.execute(
        select(<Entity>).order_by(<Entity>.created_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def create(session: AsyncSession, data: <Entity>Create) -> <Entity>:
    entity = <Entity>(**data.model_dump())
    session.add(entity)
    await session.flush()
    await session.refresh(entity)
    return entity


async def update(
    session: AsyncSession, entity: <Entity>, data: <Entity>Update
) -> <Entity>:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)
    await session.flush()
    return entity


async def delete(session: AsyncSession, entity: <Entity>) -> None:
    await session.delete(entity)
    await session.flush()
```

Rules:

- All functions are `async`.
- Session is the first argument; keyword-only for pagination params.
- Don't commit inside services. The router's session dependency commits on success.
- Don't raise HTTP exceptions here. Return `None` and let the dependency raise.

#### `dependencies.py`

This is where validation lives.

```python
from __future__ import annotations
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.<module> import service
from src.<module>.exceptions import <Entity>NotFound
from src.<module>.models import <Entity>


async def valid_<module>_id(
    <module>_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> <Entity>:
    entity = await service.get_by_id(session, <module>_id)
    if entity is None:
        raise <Entity>NotFound()
    return entity
```

Add ownership/permission dependencies as needed:

```python
async def valid_owned_<module>(
    entity: <Entity> = Depends(valid_<module>_id),
    current_user: Member = Depends(get_current_user),
) -> <Entity>:
    if entity.member_id != current_user.id:
        raise NotEntityOwner()
    return entity
```

Rules:

- Path variable name (`<module>_id`) **must match the path** in `router.py`.
- Always `async def`.
- Return the loaded object so routes don't refetch.

#### `router.py`

```python
from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.<module> import service
from src.<module>.dependencies import valid_<module>_id
from src.<module>.models import <Entity>
from src.<module>.schemas import <Entity>Create, <Entity>Response, <Entity>Update

router = APIRouter(prefix="/<plural>", tags=["<module>"])


@router.get(
    "",
    response_model=list[<Entity>Response],
    summary="List all <module> entries",
)
async def list_<plural>(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await service.list_all(session, limit=limit, offset=offset)


@router.post(
    "",
    response_model=<Entity>Response,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new <module>",
)
async def create_<module>(
    data: <Entity>Create,
    session: AsyncSession = Depends(get_session),
):
    return await service.create(session, data)


@router.get(
    "/{<module>_id}",
    response_model=<Entity>Response,
    summary="Get a <module> by id",
)
async def get_<module>(entity: <Entity> = Depends(valid_<module>_id)):
    return entity


@router.patch(
    "/{<module>_id}",
    response_model=<Entity>Response,
    summary="Update a <module>",
)
async def update_<module>(
    data: <Entity>Update,
    entity: <Entity> = Depends(valid_<module>_id),
    session: AsyncSession = Depends(get_session),
):
    return await service.update(session, entity, data)


@router.delete(
    "/{<module>_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a <module>",
)
async def delete_<module>(
    entity: <Entity> = Depends(valid_<module>_id),
    session: AsyncSession = Depends(get_session),
):
    await service.delete(session, entity)
```

Rules:

- URL prefix is **plural**.
- Path variable matches the dependency exactly.
- Every route has `response_model`, `status_code` (where non-200), and `summary`.
- Routes are thin: dependency → service → return. No business logic.

#### `config.py` (only if needed)

```python
from pydantic_settings import BaseSettings


class <Module>Config(BaseSettings):
    # only env vars this module needs
    SOME_API_KEY: str


<module>_settings = <Module>Config()
```

### 4. Register the router

Edit `backend/src/main.py` and add:

```python
from src.<module>.router import router as <module>_router
# ...
app.include_router(<module>_router)
```

Place imports alphabetically; place `include_router` calls in the same order.

### 5. Generate tests

Create `backend/tests/<module>/`:

```
tests/<module>/
├── __init__.py
├── conftest.py        # fixtures specific to this module (factory funcs)
├── test_router.py
└── test_service.py
```

Each route must have at minimum:

- One happy-path test (correct input → expected status + body shape).
- One validation-error test (bad input → 422).
- For routes behind `valid_<module>_id`: one 404 test.

Use the project's existing async test client fixture from `tests/conftest.py`. Do not invent a new one.

### 6. Generate the migration

After all files are written:

```bash
cd backend
uv run alembic revision --autogenerate -m "add_<module>_table"
```

Then **open the generated migration file and read it.** Verify:

- `upgrade()` creates the table with the expected columns and FK constraints.
- `downgrade()` drops the table.
- Index/constraint names match the project's naming convention (set in `database.py`).
- No unintended drops of other tables (Alembic sometimes mis-detects).

If the autogenerated migration is wrong, edit it. Do not regenerate blindly.

### 7. Verify

Before declaring done:

```bash
cd backend
uv run ruff check src --fix && uv run ruff format src
uv run alembic upgrade head        # applies the new migration locally
uv run pytest tests/<module>/      # all new tests pass
uv run uvicorn src.main:app --reload    # /docs shows the new endpoints
```

If any of these fail, fix before reporting back.

## Output to the user

After scaffolding, summarize:

1. The list of files created (paths only, no contents — they can read them).
2. The new endpoints (method + path + brief purpose).
3. The migration filename.
4. Any decisions you had to make that the user didn't specify (e.g. "I made `title` required and `notes` optional — change in `schemas.py` if wrong.").
5. Suggested next step (usually: "Run `pnpm gen:api` in the frontend, then ask me to scaffold the matching feature.").

## Common mistakes to avoid

- Writing `Column(...)` instead of `Mapped[...] = mapped_column(...)`. Use SQLAlchemy 2.0 syntax.
- Plural table names. It's `meal`, not `meals`.
- Putting auth checks in services. Auth lives in dependencies.
- Forgetting to register the router in `main.py`. The endpoints will silently 404.
- Path variable name mismatch between `router.py` and `dependencies.py`.
- Generating a migration before reading the existing migrations folder — sometimes a similar table already exists under a different name.
- Adding speculative fields ("we might want a `tags` array later"). Only what was asked for.
