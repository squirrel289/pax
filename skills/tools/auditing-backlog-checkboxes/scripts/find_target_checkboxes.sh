#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="."
STATUS_CSV="closed,completed,ready-for-review"
BACKLOG_DIRS=()

usage() {
  cat <<'USAGE'
Usage: find_target_checkboxes.sh [options]

Find markdown checklist entries (`[ ]`) inside backlog work items whose
frontmatter `status` is one of the selected target statuses.

Options:
  --root <path>          Repository root to search from (default: .)
  --backlog-dir <path>   Backlog directory to scan (repeatable). If omitted,
                         script auto-discovers directories named "backlog".
  --status <csv>         Comma-separated status list (default:
                         closed,completed,ready-for-review)
  --help                 Show this help text

Output format (TSV):
  FILE<TAB>STATUS<TAB>LINE<TAB>CHECKBOX_TEXT
USAGE
}

normalize() {
  tr '[:upper:]' '[:lower:]' \
    | sed -E 's/^["'"'"']?//; s/["'"'"']?$//; s/[[:space:]]+//g'
}

contains_status() {
  local status="$1"
  local needle=",${status},"
  local haystack=",${STATUS_CSV_NORMALIZED},"
  [[ "$haystack" == *"$needle"* ]]
}

extract_frontmatter_status() {
  local file="$1"
  awk '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm && $0 ~ /^[[:space:]]*status:[[:space:]]*/ {
      line = $0
      sub(/^[[:space:]]*status:[[:space:]]*/, "", line)
      sub(/[[:space:]]+#.*/, "", line)
      print line
      exit
    }
  ' "$file"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      [[ $# -ge 2 ]] || { echo "ERROR: --root requires a value" >&2; exit 2; }
      ROOT_DIR="$2"
      shift 2
      ;;
    --backlog-dir)
      [[ $# -ge 2 ]] || { echo "ERROR: --backlog-dir requires a value" >&2; exit 2; }
      BACKLOG_DIRS+=("$2")
      shift 2
      ;;
    --status)
      [[ $# -ge 2 ]] || { echo "ERROR: --status requires a value" >&2; exit 2; }
      STATUS_CSV="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$ROOT_DIR" ]]; then
  echo "ERROR: root directory not found: $ROOT_DIR" >&2
  exit 2
fi

STATUS_CSV_NORMALIZED=$(
  printf '%s' "$STATUS_CSV" \
    | tr ',' '\n' \
    | normalize \
    | awk 'NF > 0 { print }' \
    | paste -sd, -
)

if [[ -z "${STATUS_CSV_NORMALIZED:-}" ]]; then
  echo "ERROR: --status produced an empty target set" >&2
  exit 2
fi

if [[ ${#BACKLOG_DIRS[@]} -eq 0 ]]; then
  while IFS= read -r dir; do
    BACKLOG_DIRS+=("$dir")
  done < <(find "$ROOT_DIR" -type d -name backlog | sort)
fi

if [[ ${#BACKLOG_DIRS[@]} -eq 0 ]]; then
  echo "ERROR: no backlog directories found (use --backlog-dir)" >&2
  exit 1
fi

printf 'FILE\tSTATUS\tLINE\tCHECKBOX_TEXT\n'

matches=0
for backlog_dir in "${BACKLOG_DIRS[@]}"; do
  [[ -d "$backlog_dir" ]] || continue

  while IFS= read -r -d '' file; do
    raw_status=$(extract_frontmatter_status "$file" || true)
    [[ -n "${raw_status:-}" ]] || continue

    status=$(printf '%s' "$raw_status" | normalize)
    contains_status "$status" || continue

    while IFS= read -r match; do
      line_no=${match%%:*}
      checkbox_text=${match#*:}
      printf '%s\t%s\t%s\t%s\n' "$file" "$status" "$line_no" "$checkbox_text"
      matches=$((matches + 1))
    done < <(rg --line-number --no-heading --color never '\[ \]' "$file" || true)
  done < <(find "$backlog_dir" -type f -name '*.md' -print0 | sort -z)
done

echo "Found $matches unchecked checklist entries in target statuses." >&2
