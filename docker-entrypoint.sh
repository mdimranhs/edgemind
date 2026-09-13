#!/bin/sh
set -e
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers 1 \
  --limit-concurrency 4 \
  --timeout-keep-alive 75 \
  --timeout-graceful-shutdown 5
