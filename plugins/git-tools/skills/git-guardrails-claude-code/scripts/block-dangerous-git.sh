#!/usr/bin/env bash

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -er '.tool_input.command // ""') || exit 2
[ -z "$COMMAND" ] && exit 0
HOOK_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$HOOK_DIR/git-command-guard.py" "$COMMAND" '*' || exit 2
