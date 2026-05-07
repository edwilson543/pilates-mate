#!/usr/bin/env bash
set -e

COMMAND=${1}

case "$COMMAND" in
  api)
    exec uvicorn src.pilates.interfaces.api.app:app \
      --port 8000 \
      --host 0.0.0.0
    ;;
  worker)
    echo "Celery worker command not yet implemented"
    exit 1
    ;;
  migrate)
    echo "Migrate command not yet implemented"
    exit 1
    ;;
  *)
    echo "Unknown command: $COMMAND"
    echo "Available commands: api, worker, migrate"
    exit 1
    ;;
esac
