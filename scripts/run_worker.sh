#!/bin/sh
set -e

uv run celery -A config worker --loglevel=info