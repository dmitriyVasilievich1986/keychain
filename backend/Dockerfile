FROM python:3.13-slim-bookworm AS build

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

WORKDIR /opt/backend

# Install dependencies from pyproject.toml
COPY ./pyproject.toml ./
COPY ./uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project --link-mode=copy --no-editable

FROM python:3.13-slim-bookworm AS development

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/backend/.venv /opt/backend/.venv

WORKDIR /opt/backend

# Add application
COPY ./src ./src
COPY ./pyproject.toml ./

# Add configurations
COPY ./configurations ./configurations

ENV PYTHONPATH="/opt/backend/src"
ENV PATH="/opt/backend/.venv/bin:${PATH}"

FROM python:3.13-slim-bookworm AS production

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/backend

COPY --from=development /opt/backend /opt/backend

# Add binaries for run inside container
ENV PYTHONPATH="/opt/backend/src"
ENV PATH="/opt/backend/.venv/bin:${PATH}"

EXPOSE 8000

ENTRYPOINT ["python", "-m", "uvicorn", "keychain.modules.app:get_app", "--host", "0.0.0.0", "--port", "8000"]