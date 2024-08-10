#!/bin/bash
set -euo pipefail

mkdir -p alembic/versions

alembic upgrade head

alembic revision --autogenerate -m "generated"
