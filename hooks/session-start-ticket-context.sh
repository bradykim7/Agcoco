#!/usr/bin/env bash
# SessionStart — when the current branch names a Jira-style ticket, surface that
# ticket's existing docs so the session starts with them already in context.
#
# Two layouts are tried, in order:
#   1. A shared docs root holding one directory per ticket. Point
#      $TICKET_DOCS_ROOT at it, or let the hook find a sibling `issue/` by
#      walking up from the repo.
#   2. This repo's own .plans/, .handoffs/, .research/ files naming the ticket.
#
# stdout is appended to Claude's session context; stderr is shown to the user.

MAX_DOCS=12

git rev-parse --git-dir > /dev/null 2>&1 || exit 0

branch=$(git symbolic-ref --short HEAD 2>/dev/null)
[ -z "$branch" ] && exit 0

ticket=$(echo "$branch" | grep -oE '[A-Z]+-[0-9]+' | head -1)
[ -z "$ticket" ] && exit 0

# --- 1. shared ticket-docs root ---------------------------------------------

if [ -n "${TICKET_DOCS_ROOT:-}" ]; then
  docs_root="$TICKET_DOCS_ROOT"
else
  # Repos often sit beside a shared docs dir under one workspace root — climb
  # until it shows up. $HOME is the ceiling so a stray ~/issue can never match.
  docs_root=""
  d=$(git rev-parse --show-toplevel 2>/dev/null) || d="$PWD"
  [ -z "$d" ] && d="$PWD"
  while [ "$d" != "/" ] && [ "$d" != "$HOME" ]; do
    if [ -d "$d/issue" ]; then
      docs_root="$d/issue"
      break
    fi
    d=$(dirname "$d")
  done
fi

dir=""
if [ -d "$docs_root" ]; then
  # Dir names don't always follow the branch's spelling (FOO-123 vs foo123), so
  # try both case-insensitively. Top level first — sub-tickets sit one level
  # under their parent and must not shadow a top-level match.
  compact=$(echo "$ticket" | tr '[:upper:]' '[:lower:]' | tr -d '-')
  dir=$(find "$docs_root" -mindepth 1 -maxdepth 1 -type d \( -iname "$ticket" -o -iname "$compact" \) 2>/dev/null | head -1)
  if [ -z "$dir" ]; then
    dir=$(find "$docs_root" -mindepth 2 -maxdepth 2 -type d \( -iname "$ticket" -o -iname "$compact" \) 2>/dev/null | head -1)
  fi
fi

if [ -n "$dir" ]; then
  # Each .html is a rendered twin of the .md beside it — list the .md only.
  docs=()
  while IFS= read -r f; do
    [ "${f##*.}" = "html" ] && [ -f "${f%.html}.md" ] && continue
    docs+=("$(basename "$f")")
  done < <(find "$dir" -maxdepth 1 -type f 2>/dev/null | sort)

  subs=()
  while IFS= read -r sub; do
    subs+=("$(basename "$sub")")
  done < <(find "$dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)

  echo "## Ticket docs for $ticket (branch: $branch)"
  echo ""
  echo "$dir"
  echo ""

  shown=0
  if [ ${#docs[@]} -gt 0 ]; then
    for name in "${docs[@]}"; do
      [ "$shown" -ge "$MAX_DOCS" ] && break
      echo "- $name"
      shown=$((shown + 1))
    done
  fi

  if [ ${#docs[@]} -gt "$shown" ]; then
    echo "- ... (+$(( ${#docs[@]} - shown )) more)"
  fi

  if [ ${#subs[@]} -gt 0 ]; then
    echo ""
    echo "Subdirs: ${subs[*]}"
  fi

  exit 0
fi

# --- 2. fall back to this repo's own plan/handoff/research files -------------

found=()
for d in .plans .handoffs .research; do
  [ -d "$d" ] || continue
  while IFS= read -r f; do
    found+=("$f")
  done < <(find "$d" -maxdepth 2 -name "*${ticket}*" -type f 2>/dev/null | head -3)
done

if [ ${#found[@]} -gt 0 ]; then
  echo "## Existing artifacts for ticket $ticket (branch: $branch)"
  echo ""
  for item in "${found[@]}"; do
    echo "- $item"
  done
fi

exit 0
