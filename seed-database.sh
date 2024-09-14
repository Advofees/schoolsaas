#!/bin/bash
set -euo pipefail

# Set PYTHONPATH to the parent directory of the current script
export PYTHONPATH=$(pwd)

# Run the seed script
python dev/seeds/seed.py
