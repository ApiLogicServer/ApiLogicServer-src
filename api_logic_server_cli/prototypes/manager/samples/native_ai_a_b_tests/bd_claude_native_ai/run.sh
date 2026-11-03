#!/bin/bash
set -e
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
