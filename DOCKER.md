# IoT Dashboard Docker Setup

This document explains how to use the Docker setup for the IoT Dashboard Flask application.

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (can be started with the included docker-compose.yml)

## Quick Start with Docker Compose

1. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your database and application settings.

3. **Start the application with database:**
   ```bash
   docker-compose up -d
   ```

4. **The application will be available at:** http://localhost:5000

## Manual Docker Build

1. **Build the Docker image:**
   ```bash
   docker build -t iot-dashboard .
   ```

2. **Run with environment variables:**
   ```bash
   docker run -p 5000:5000 \
     -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
     -e FLASK_ENV=development \
     iot-dashboard
   ```

## Database Migrations

The Docker setup can automatically run database migrations if you set:
```
RUN_MIGRATIONS=true
```

## Environment Variables

Key environment variables for the Docker container:

- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: development/production
- `RUN_MIGRATIONS`: Set to "true" to auto-run migrations
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Google Cloud Storage credentials (if used)

## Development Mode

For development, uncomment the volumes section in docker-compose.yml to mount your local code:

```yaml
volumes:
  - .:/app
```

## Health Checks

The Dockerfile includes health checks. Check container health with:
```bash
docker ps
```

## Security Features

- Non-root user execution
- Minimal system dependencies
- Production-ready defaults
- Health monitoring