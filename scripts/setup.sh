#!/usr/bin/env bash
set -euo pipefail

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
[ -f .env ] || cp .env.example .env
python -m support_agent.cli reset-db
python -m support_agent.cli inspect-db
pytest
