# syntax=docker/dockerfile:1

ARG NODE_VERSION=22.20.0
# pnpm 9: matches our other deployed apps; pnpm 10 blocks dependency
# build scripts (esbuild etc.) which breaks CI builds.
ARG PNPM_VERSION=9.15.9

################################################################################
FROM node:${NODE_VERSION}-alpine AS base
ARG PNPM_VERSION

WORKDIR /usr/src/app

RUN --mount=type=cache,target=/root/.npm \
    npm install -g pnpm@${PNPM_VERSION}

################################################################################
FROM base AS build

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install ALL dependencies (including dev) for build
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Copy source files
COPY . .

# VITE_* vars are baked into the browser bundle at build time.
# These must be the URLs the browser (not Docker) uses to reach the services.
# Override these as build args in docker-compose.
ARG VITE_API_URL=http://localhost:8080
ARG VITE_CHAT_API_BASE_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_CHAT_API_BASE_URL=$VITE_CHAT_API_BASE_URL

# Build with env validation skipped
ENV SKIP_ENV_VALIDATION=1
RUN pnpm run build

################################################################################
FROM nginx:alpine AS final

EXPOSE 3000

RUN printf 'server {\n  listen 3000;\n  server_name _;\n  root /usr/share/nginx/html;\n  index index.html;\n\n  location / {\n    try_files $uri $uri/ /index.html;\n  }\n}\n' > /etc/nginx/conf.d/default.conf

COPY --from=build /usr/src/app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
