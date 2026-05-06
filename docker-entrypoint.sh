#!/bin/sh
set -e

if [ "${API_AUTO_LOAD_DATA:-true}" = "true" ]; then
  echo "Preparing synthetic data and loading PostgreSQL..."
  python -m python.run_pipeline --load-postgres
fi

exec uvicorn api.main:app --host 0.0.0.0 --port 8000

