#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Run Alembic migrations
alembic upgrade head

echo "Migrations completed successfully."
