#!/bin/bash
set -euo pipefail

alembic upgrade head

python backend/initial_setup.py

uvicorn backend.main:app --host "0.0.0.0" --port 8080