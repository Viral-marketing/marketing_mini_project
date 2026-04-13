#!/bin/sh
set -e

uv run celery -A config beat info