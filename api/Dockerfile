# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# Need curl for healthcheck 
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy the source code into the container.
COPY . .

# Create the db directory and give appuser ownership so SQLite can write there.
# This must happen as root (before USER appuser) so the volume mount point exists
# and is writable when Docker mounts the named volume at runtime.
RUN mkdir -p /app/db && chown appuser /app/db

# Switch to the non-privileged user to run the application.
USER appuser

# Expose the port that the application listens on.
EXPOSE 8080

# Run the application (Railway uses PORT environment variable)
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
