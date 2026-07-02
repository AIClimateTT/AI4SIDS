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
FROM base AS final

# Install curl for health checks
RUN apk add --no-cache curl

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

# Copy the entire .output directory (includes server + public assets)
COPY --from=build /usr/src/app/.output ./.output

# TanStack Start with Nitro node-server needs node_modules at runtime
COPY --from=build /usr/src/app/node_modules ./node_modules
COPY --from=build /usr/src/app/package.json ./package.json

# Run as non-root user
USER node

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
