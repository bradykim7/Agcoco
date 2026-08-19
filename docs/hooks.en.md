# Hooks

Bash scripts under [`hooks/`](../hooks/) wired into Claude Code's hook system. Each script runs at a specific lifecycle moment and can:

- **block** an action (non-zero exit on a blocking hook),
- **annotate** Claude's context (stdout on Stop / SessionStart hooks),
- **warn the user** (stderr surfaces to the operator).

Linked into `~/.claude/hooks/` by `install.sh`; the actual hook registration lives in `~/.claude/settings.json`.

> 한국어: [hooks.kr.md](./hooks.kr.md)

## Inventory

| Script | Event | Type | Purpose |
|--------|-------|------|---------|
| [`block-dangerous-git.sh`](../hooks/block-dangerous-git.sh) | PreToolUse: Bash | **Blocking** | Refuses `git commit`, `git push`, `git filter-repo`, `git reset --hard`, etc. — human approval required |
| [`session-start-ticket-context.sh`](../hooks/session-start-ticket-context.sh) | SessionStart | Annotates context | When the branch matches a Jira-style ticket pattern, surfaces that ticket's docs. Prefers a shared ticket-docs root — set `$TICKET_DOCS_ROOT`, or let it find a sibling `issue/` by walking up — and otherwise falls back to matching files in `.plans/`, `.handoffs/`, `.research/` |

## Hook event model (quick reference)

| Event | Fires when | Stdout goes to | Blocking? |
|-------|-----------|----------------|-----------|
| `PreToolUse` | Before a tool runs | (ignored unless `exit ≠ 0`) | Yes — non-zero exit cancels the tool call |
| `Stop` | After Claude's turn ends | Appended to Claude's next context | No |
| `SessionStart` | Start of a new session | Appended to session context | No |

## Conventions

- Shebang: `#!/usr/bin/env bash`.
- `PreToolUse: Bash` hooks read the tool input as JSON on stdin — use `jq -r '.tool_input.command'` to extract the command.
- Keep hooks fast (< ~100ms). They run on every matched tool call.
- Guard against missing dependencies (`command -v jq >/dev/null || exit 0`) so a missing tool can't break the session.
- Echo Claude-facing hints to **stdout**; echo operator-facing warnings to **stderr**.

## Adding a new hook

1. Drop `your-hook.sh` in [`hooks/`](../hooks/); `chmod +x`.
2. Re-run `./install.sh` to symlink to `~/.claude/hooks/`.
3. Wire it up in `~/.claude/settings.json` under the matching event:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         { "matcher": "Bash", "hooks": [{ "type": "command", "command": "$HOME/.claude/hooks/your-hook.sh" }] }
       ]
     }
   }
   ```
4. Test by triggering the event; check exit code, stdout, stderr behaviors match expectations.

## Why these specific hooks exist

- **`block-dangerous-git.sh`** — global memory rule: git commit and push require human approval. The hook enforces this even if a session prompt forgets.
- **`session-start-ticket-context.sh`** — auto-resumes ticket context so the user doesn't have to remember to attach the ticket's docs. Works whether those docs live in the repo or in a shared per-ticket directory outside it.
