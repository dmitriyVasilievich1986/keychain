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

# Create an unprivileged user to run the application
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd --gid ${APP_GID} keychain \
    && useradd --uid ${APP_UID} --gid keychain --no-create-home --shell /usr/sbin/nologin keychain

WORKDIR /opt/backend

# Add application
COPY --from=build /opt/backend/.venv ./.venv
COPY --from=build /opt/backend/src ./src
COPY --from=build /opt/backend/pyproject.toml ./
COPY --from=build /opt/app/backend/src/keychain/application_version.py ./src/keychain/application_version.py

# Add configurations
COPY ./backend/configurations ./configurations

# Add the startup script
COPY --chmod=755 ./backend/scripts/start_app.sh ./scripts/start_app.sh

# Add binaries for run inside container
ENV PYTHONPATH="/opt/backend/src"
ENV PATH="/opt/backend/.venv/bin:${PATH}"

USER keychain

EXPOSE 8080

ENTRYPOINT ["/opt/backend/scripts/start_app.sh"]
