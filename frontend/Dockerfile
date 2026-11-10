# Build context: ./frontend
#
#   docker build -t keychain-frontend ./frontend
#   docker run --rm -v "$PWD/static:/opt/app/static" keychain-frontend
#
# The container builds the bundle into /opt/app/static (vite outDir: ../static) and exits;
# mount a host directory there to collect the output.

FROM node:24-alpine

# Vite+ needs the system CA certificates
RUN apk add --no-cache ca-certificates

ARG VITE_API_PREFIX="/keychain"
ARG VITE_API_HOST=""
ARG VITE_IMAGES_HOST="/static/i"

ENV VITE_API_PREFIX=${VITE_API_PREFIX} \
    VITE_API_HOST=${VITE_API_HOST} \
    VITE_IMAGES_HOST=${VITE_IMAGES_HOST}

WORKDIR /opt/app/frontend

# Install dependencies first so they stay cached until the lockfile changes
COPY package.json package-lock.json ./
RUN npm install -g npm@12.0.1 \
    && npm ci

COPY . .

CMD ["npm", "run", "build"]
