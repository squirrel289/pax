#!/usr/bin/env bash
set -euo pipefail

# YOLO interaction mode: execute default actions without prompts.
# Expected environment variables:
# - DEFAULT_ACTION (preferred default)
# - OPTIONS (newline-delimited list of: id|label)
# - CONTEXT_JSON (placeholder, for future use)

if [[ -n "${DEFAULT_ACTION:-}" ]]; then
  echo "${DEFAULT_ACTION}"
  exit 0
fi

if [[ -n "${OPTIONS:-}" ]]; then
  first_line="${OPTIONS%%$'\n'*}"
  first_id="${first_line%%|*}"
  if [[ -n "$first_id" ]]; then
    echo "$first_id"
    exit 0
  fi
fi

# Safe default: do not proceed when no defaults are provided.
echo "abort"
