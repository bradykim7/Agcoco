#!/usr/bin/env bash
# PreToolUse: Bash — block destructive commands before Claude runs them.

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -er '.tool_input.command // ""') || exit 2

[ -z "$COMMAND" ] && exit 0

block() {
  echo "BLOCKED: $1" >&2
  echo "Command was: $COMMAND" >&2
  exit 2
}

# Commit and push are always manual, including Git global options.
HOOK_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$HOOK_DIR/git-command-guard.py" "$COMMAND" main,master || exit 2

# ─── FILE SYSTEM: rm ─────────────────────────────────────────────────────────

# rm -rf on root or home
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+(-[rRf]+|--recursive|--force).*[[:space:]](/|~)/?([[:space:]]|\*|$)'; then
  block "rm -rf on root or home directory."
fi

# rm -rf . (current directory)
if echo "$COMMAND" | grep -qE 'rm[[:space:]]+(-[rRf]+|--recursive)[[:space:]]+\.([[:space:]]|$)'; then
  block "rm -rf . deletes the entire current directory."
fi

# sudo rm anything
if echo "$COMMAND" | grep -qE 'sudo[[:space:]]+rm'; then
  block "sudo rm is too dangerous to run autonomously. Run manually if intentional."
fi

# ─── FILE SYSTEM: overwrite via redirect ─────────────────────────────────────

# Overwriting known critical files with > redirect
if echo "$COMMAND" | grep -qE '>[[:space:]]*(CLAUDE\.md|AGENTS\.md|settings\.json|\.env|package\.json|composer\.json)'; then
  block "Redirecting output to a critical config file could destroy it. Use Edit tool instead."
fi

# ─── PERMISSIONS ─────────────────────────────────────────────────────────────

if echo "$COMMAND" | grep -qE 'chmod[[:space:]]+(-[rR][[:space:]]+)?777'; then
  block "chmod 777 makes files world-writable. Too permissive to run autonomously."
fi

# ─── REMOTE CODE EXECUTION ───────────────────────────────────────────────────

if echo "$COMMAND" | grep -qE '(curl|wget)[[:space:]].*\|[[:space:]]*(bash|sh|zsh|python|ruby|node)'; then
  block "Piping remote content directly to a shell is a code injection risk."
fi

# ─── DATABASE ────────────────────────────────────────────────────────────────

if echo "$COMMAND" | grep -qiE '(DROP[[:space:]]+(DATABASE|TABLE|SCHEMA)|TRUNCATE[[:space:]]+TABLE)'; then
  block "Destructive SQL (DROP/TRUNCATE) blocked. Run manually if intentional."
fi

# ─── PROCESS KILLING ─────────────────────────────────────────────────────────

if echo "$COMMAND" | grep -qE '(pkill|killall)[[:space:]]+(-9[[:space:]]|-KILL[[:space:]])?[a-zA-Z]'; then
  block "Broad process kill (pkill/killall) blocked. Run manually if intentional."
fi

exit 0
