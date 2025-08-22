#!/bin/bash
set -e

# Function to wait for database
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL', ''))
    conn.close()
    print('Database is ready!')
    exit(0)
except:
    exit(1)
    "; do
        echo "Database not ready, waiting..."
        sleep 2
    done
}

# Wait for database if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    wait_for_db
fi

# Run database migrations if requested
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    flask db upgrade
fi

# Execute the main command
exec "$@"