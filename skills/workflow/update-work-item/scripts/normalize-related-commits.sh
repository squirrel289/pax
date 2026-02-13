#!/usr/bin/env bash

set -euo pipefail

BACKLOG_DIR="backlog"
DRY_RUN=0
INCLUDE_ARCHIVE=0

usage() {
  cat <<'USAGE'
Usage: commit-repair.sh [--dry-run] [--backlog-dir <path>] [--include-archive] [--help]

Normalizes `related_commit` / `related_commits` blocks in backlog markdown files by:
- extracting commit hashes
- sorting entries by commit timestamp (oldest to newest)
- rewriting entries as: `- <short-hash>  # <subject>`
- preserving missing commits as `MISSING-COMMIT` markers

Options:
  --dry-run              Show diffs only; do not modify files
  --backlog-dir <path>   Backlog directory to scan (default: backlog)
  --include-archive      Include backlog/archive/*.md files (default: skip)
  --help                 Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --backlog-dir)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --backlog-dir requires a value" >&2
        exit 2
      fi
      BACKLOG_DIR="$2"
      shift 2
      ;;
    --include-archive)
      INCLUDE_ARCHIVE=1
      shift
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

if [[ ! -d "$BACKLOG_DIR" ]]; then
  echo "ERROR: backlog directory not found: $BACKLOG_DIR" >&2
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required but not found in PATH" >&2
  exit 2
fi

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

WARNINGS_FILE="$TMP_DIR/warnings.txt"
: > "$WARNINGS_FILE"

affected_files=0
processed_files=0

extract_related_key() {
  local file="$1"
  if grep -qE '^related_commit:' "$file"; then
    printf 'related_commit\n'
    return 0
  fi
  if grep -qE '^related_commits:' "$file"; then
    printf 'related_commits\n'
    return 0
  fi
  return 1
}

extract_related_block() {
  local file="$1"
  local key="$2"
  awk -v key="$key" '
    $0 ~ "^" key ":" { inblock=1; next }
    inblock && /^[[:space:]]/ { print; next }
    inblock { exit }
  ' "$file"
}

build_replacement_block() {
  local file="$1"
  local key="$2"
  local out_block="$3"
  local has_missing_flag_file="$4"

  local raw_block="$TMP_DIR/raw_block.$$.txt"
  local hashes_raw="$TMP_DIR/hashes_raw.$$.txt"
  local hashes_unique="$TMP_DIR/hashes_unique.$$.txt"
  local summary_map="$TMP_DIR/summary_map.$$.txt"
  local sortable="$TMP_DIR/sortable.$$.txt"
  local sorted_hashes="$TMP_DIR/sorted_hashes.$$.txt"

  : > "$summary_map"
  : > "$sortable"
  : > "$out_block"
  : > "$has_missing_flag_file"

  extract_related_block "$file" "$key" > "$raw_block"

  grep -oE '\b[0-9A-Fa-f]{7,40}\b' "$raw_block" | tr '[:upper:]' '[:lower:]' > "$hashes_raw" || true
  awk '!seen[$0]++' "$hashes_raw" > "$hashes_unique"

  if [[ ! -s "$hashes_unique" ]]; then
    return 1
  fi

  while IFS= read -r line; do
    local hash
    hash=$(printf '%s\n' "$line" | grep -oE '\b[0-9A-Fa-f]{7,40}\b' | head -n1 | tr '[:upper:]' '[:lower:]' || true)
    if [[ -z "$hash" ]]; then
      continue
    fi

    local summary
    summary=$(printf '%s\n' "$line" | sed -E "s/^[[:space:]]*-[[:space:]]*\"?${hash}\"?[[:space:]]*#?[[:space:]]*//I")
    if ! grep -qiE "^${hash}\|" "$summary_map"; then
      printf '%s|%s\n' "$hash" "$summary" >> "$summary_map"
    fi
  done < "$raw_block"

  while IFS= read -r hash; do
    local ts
    ts=$(git show -s --format=%ct "$hash" 2>/dev/null || true)
    if [[ -n "$ts" ]]; then
      printf '%s %s\n' "$ts" "$hash" >> "$sortable"
    else
      printf '1\n' > "$has_missing_flag_file"
      printf '%s %s\n' "9999999999" "$hash" >> "$sortable"
    fi
  done < "$hashes_unique"

  sort -n -k1,1 -k2,2 "$sortable" | awk '{print $2}' > "$sorted_hashes"

  while IFS= read -r hash; do
    local formatted
    formatted=$(git log --oneline "$hash" -n 1 --pretty=format:'  - %h  # %s' 2>/dev/null || true)
    if [[ -n "$formatted" ]]; then
      printf '%s\n' "$formatted" >> "$out_block"
      continue
    fi

    local original_summary
    original_summary=$(grep -iE "^${hash}\|" "$summary_map" | head -n1 | cut -d'|' -f2-)
    if [[ -n "$original_summary" ]]; then
      printf '  - %s  # MISSING-COMMIT: %s\n' "$hash" "$original_summary" >> "$out_block"
    else
      printf '  - %s  # MISSING-COMMIT\n' "$hash" >> "$out_block"
    fi
  done < "$sorted_hashes"

  return 0
}

rewrite_file_block() {
  local file="$1"
  local key="$2"
  local block_file="$3"
  local output_file="$4"

  awk -v key="$key" -v block_file="$block_file" '
    BEGIN {
      inblock = 0
      inserted = 0
    }
    {
      if ($0 ~ "^" key ":") {
        print
        inblock = 1
        next
      }

      if (inblock && /^[[:space:]]/) {
        next
      }

      if (inblock && !inserted) {
        while ((getline line < block_file) > 0) {
          print line
        }
        close(block_file)
        inserted = 1
        inblock = 0
      }

      print
    }
    END {
      if (inblock && !inserted) {
        while ((getline line < block_file) > 0) {
          print line
        }
        close(block_file)
      }
    }
  ' "$file" > "$output_file"
}

while IFS= read -r -d '' file; do
  if [[ "$INCLUDE_ARCHIVE" -ne 1 && "$file" == *"/archive/"* ]]; then
    continue
  fi

  key=$(extract_related_key "$file" || true)
  if [[ -z "${key:-}" ]]; then
    continue
  fi

  processed_files=$((processed_files + 1))

  block_file="$TMP_DIR/new_block.$$.txt"
  missing_flag_file="$TMP_DIR/missing_flag.$$.txt"

  if ! build_replacement_block "$file" "$key" "$block_file" "$missing_flag_file"; then
    continue
  fi

  file_tmp="$TMP_DIR/updated.$$.md"
  rewrite_file_block "$file" "$key" "$block_file" "$file_tmp"

  if ! diff -q "$file" "$file_tmp" >/dev/null 2>&1; then
    affected_files=$((affected_files + 1))
    if [[ "$DRY_RUN" -eq 1 ]]; then
      echo "=== $file ==="
      diff -u "$file" "$file_tmp" || true
    else
      cp "$file_tmp" "$file"
      echo "updated: $file"
    fi
  fi

  if [[ -s "$missing_flag_file" ]]; then
    echo "$file" >> "$WARNINGS_FILE"
  fi

done < <(find "$BACKLOG_DIR" -type f -name '*.md' -print0)

files_with_warnings=$(sort -u "$WARNINGS_FILE" | wc -l | awk '{print $1}')

if [[ "$files_with_warnings" -gt 0 ]]; then
  echo "WARN: files with missing commit references:" >&2
  sort -u "$WARNINGS_FILE" >&2
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "SUMMARY(dry-run): processed=$processed_files changed=$affected_files warnings=$files_with_warnings"
else
  echo "SUMMARY(write): processed=$processed_files changed=$affected_files warnings=$files_with_warnings"
fi
