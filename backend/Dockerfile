FROM python:3.14-slim

# Copy uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Compile .pyc files at install time so the first request is faster.
# Copy mode avoids symlink issues in Docker.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies first — this layer is cached as long as the lockfile
# doesn't change, so re-builds after code-only edits are fast.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-install-project

# Copy the rest of the source
COPY . .

# Install the project package itself (without re-installing deps)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Drop root privileges
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser /app
USER appuser

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
