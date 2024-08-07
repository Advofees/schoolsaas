#!/bin/bash
set -euo pipefail

uvicorn backend.main:app --host "0.0.0.0" --reload