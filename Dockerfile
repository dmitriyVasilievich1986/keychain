FROM node:24-slim AS frontend

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/frontend

COPY ./frontend ./

RUN npm install -g npm@12.0.1 \
    && npm ci \
    && npm run build

FROM python:3.13-slim-bookworm AS build

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

WORKDIR /opt/backend

# Install dependencies from pyproject.toml
COPY ./backend/pyproject.toml ./
COPY ./backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project --link-mode=copy --no-editable

# Install the project itself so its console scripts (the `keychain` CLI) are available
COPY ./backend/README.md ./backend/LICENSE ./
COPY ./backend/src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --link-mode=copy --no-editable

# Generate the application-level version from git tags
COPY ./.git /opt/app/.git
COPY ./scripts /opt/app/scripts
COPY ./backend/src/keychain/application_version.py /opt/app/backend/src/keychain/application_version.py
COPY ./frontend/src/utils/application-version.json /opt/app/frontend/src/utils/application-version.json
RUN bash /opt/app/scripts/generate-application-version.sh

FROM python:3.13-slim-bookworm AS production

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/backend

# Add application
COPY --from=build /opt/backend/.venv ./.venv
COPY --from=build /opt/backend/src ./src
COPY --from=build /opt/backend/pyproject.toml ./
COPY --from=build /opt/app/backend/src/keychain/application_version.py ./src/keychain/application_version.py

# Add configurations
COPY ./backend/configurations ./configurations

# Add frontend bundle
COPY --from=frontend /opt/static ./static

# Add binaries for run inside container
ENV PYTHONPATH="/opt/backend/src"
ENV PATH="/opt/backend/.venv/bin:${PATH}"

EXPOSE 8000

ENTRYPOINT ["python", "-m", "keychain"]
