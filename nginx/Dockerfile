# Build context: repository root (needs ./frontend, ./scripts and ./.git)
FROM node:24-slim AS frontend

ENV VITE_API_PREFIX="/keychain"
ENV VITE_API_HOST=""
ENV VITE_IMAGES_HOST="/static/i"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

# Install dependencies first so they stay cached until the lockfile changes
COPY ./frontend/package.json ./frontend/package-lock.json ./frontend/
RUN npm install -g npm@12.0.1 \
    && cd frontend \
    && npm ci

COPY ./frontend ./frontend

# Generate the application-level version from git tags
# (the script also writes a backend file, so its directory must exist)
COPY ./.git ./.git
COPY ./scripts/generate-application-version.sh ./scripts/
RUN mkdir -p ./backend/src/keychain \
    && bash ./scripts/generate-application-version.sh

# Build the bundle into /opt/app/static (vite outDir: ../static)
RUN cd frontend && npm run build

FROM nginx:stable-alpine AS production

COPY ./nginx/config/nginx.conf /etc/nginx/nginx.conf
COPY --from=frontend /opt/app/static /usr/share/nginx/html/static
