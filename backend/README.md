# Telusko Backend

FastAPI backend for the Telusko Workflow Engine Kanban board. Managed with
[uv](https://docs.astral.sh/uv/) — never use `pip` or `python` directly.

## Setup

```bash
cd backend
uv sync                 # create .venv and install all deps (incl. dev group)
```

## Running

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API is served on `http://localhost:8000`. Health check: `GET /health`.

## Common commands

```bash
uv add <package>            # add a runtime dependency
uv add --dev <package>      # add a dev dependency
uv run pytest               # run the test suite
uv run python <script.py>   # run a script in the project env
```

## Migrations (Alembic)

The Alembic env reads the database URL from `app.core.config.settings`
(`.env`), so no URL is hardcoded in `alembic.ini`. Always create a migration
when changing models.

```bash
uv run alembic revision --autogenerate -m "describe change"   # generate
uv run alembic upgrade head                                   # apply
uv run alembic downgrade -1                                   # roll back one
uv run alembic current                                        # show current rev
```

Autogenerate needs `target_metadata` wired in `alembic/env.py`. Once a shared
declarative `Base` exists under `app/models/`, uncomment the `Base.metadata`
lines there.

## Layout

```
app/
  main.py          FastAPI entrypoint (CORS + health)
  core/config.py   Settings via pydantic-settings
  models/          SQLAlchemy models
  schemas/         Pydantic schemas (camelCase aliases per specs/api-contract.md)
  services/        Business logic (routes stay thin)
  api/             Route handlers
alembic/           Migration environment (async); versions/ holds revisions
alembic.ini        Alembic config (URL injected from settings at runtime)
tests/             pytest (asyncio_mode = auto)
```

See `../specs/api-contract.md` for the exact request/response shapes the frontend expects.
