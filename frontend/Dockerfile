# syntax=docker/dockerfile:1

ARG NODE_VERSION=22.20.0
ARG PNPM_VERSION=10.17.1

################################################################################
FROM node:${NODE_VERSION}-alpine AS base
WORKDIR /usr/src/app
RUN npm install -g pnpm@${PNPM_VERSION}

################################################################################
FROM base AS build
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile
ENV NITRO_PRESET=node-server
ARG VITE_API_URL
ARG VITE_CHAT_API_BASE_URL
ARG VITE_BASE_URL

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_CHAT_API_BASE_URL=$VITE_CHAT_API_BASE_URL
ENV VITE_BASE_URL=$VITE_BASE_URL
ENV SKIP_ENV_VALIDATION=1

COPY . .
RUN pnpm run build

################################################################################
FROM base AS final

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

# Install a lightweight static file server
RUN npm install -g serve

ENV NODE_ENV=production
# Copy the 'dist' folder which your logs showed was being created
COPY --from=build /usr/src/app/dist ./dist

USER node
EXPOSE 3000

# Serve the static files
CMD ["serve", "-s", "dist", "-l", "3000"]