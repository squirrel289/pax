#!/usr/bin/env bash
set -euo pipefail

# Collaborative interaction mode: prompt user for decisions.
# Expected environment variables:
# - PROMPT_TEXT
# - OPTIONS (newline-delimited list of: id|label)

prompt_for_choice() {
  local prompt_text="$1"
  local options="$2"
  local custom_label="Other action..."

  echo "$prompt_text"
  echo
  local i=1
  local ids=()
  while IFS= read -r line; do
    local id="${line%%|*}"
    local label="${line#*|}"
    ids+=("$id")
    echo "$i) $label"
    i=$((i+1))
  done <<< "$options"

  echo "$i) $custom_label"
  local custom_index=$i

  echo -n "Select an option: "
  read -r selection

  if [[ "$selection" == "$custom_index" ]]; then
    echo -n "Enter custom action: "
    read -r custom_action
    echo "custom:$custom_action"
    return 0
  fi

  local index=$((selection-1))
  if [[ $index -ge 0 && $index -lt ${#ids[@]} ]]; then
    echo "${ids[$index]}"
    return 0
  fi

  echo "invalid" >&2
  return 1
}

if [[ -z "${OPTIONS:-}" ]]; then
  echo "invalid" >&2
  exit 1
fi

prompt_for_choice "${PROMPT_TEXT:-Select an option}" "${OPTIONS}"
