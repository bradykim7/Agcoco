# Hooks

Bash scripts under [`hooks/`](../hooks/) wired into Claude Code's hook system. Each script runs at a specific lifecycle moment and can:

- **block** a tool call (`exit 2` from `PreToolUse`),
- **annotate** Claude's context (plain-text stdout on `SessionStart`),
- **explain a block** (`PreToolUse` with `exit 2` sends stderr to Claude).

Linked into `~/.claude/hooks/` by `install.sh`; the actual hook registration lives in `~/.claude/settings.json`.

> 한국어: [hooks.kr.md](./hooks.kr.md)

## Inventory

| Script | Event | Type | Purpose |
|--------|-------|------|---------|
| [`block-dangerous-git.sh`](../hooks/block-dangerous-git.sh) | PreToolUse: Bash | **Blocking** | Refuses `git commit`, `git push`, `git filter-repo`, `git reset --hard`, etc. — commit/push are always manual |
| [`session-start-ticket-context.sh`](../hooks/session-start-ticket-context.sh) | SessionStart | Annotates context | When the branch matches a Jira-style ticket pattern, surfaces that ticket's docs. Prefers a shared ticket-docs root — set `$TICKET_DOCS_ROOT`, or let it find a sibling `issue/` by walking up — and otherwise falls back to matching files in `.plans/`, `.handoffs/`, `.research/` |

## Hook event model (quick reference)

| Event | Fires when | Behavior used here |
|-------|------------|--------------------|
| `PreToolUse` | Before a tool runs | `exit 2` blocks the tool call; stderr explains why. `exit 0` without a JSON decision leaves normal permissions in effect. |
| `SessionStart` | Start of a session | Plain-text stdout adds context; the hook does not block session start. |

Other non-zero exit codes do not block by themselves. `Stop` can prevent stopping with `exit 2`, but this repo does not register a `Stop` hook. See the [official hook reference](https://code.claude.com/docs/en/hooks#exit-code-output).

## Conventions

- Shebang: `#!/usr/bin/env bash`.
- `PreToolUse: Bash` hooks read the tool input as JSON on stdin — use `jq -r '.tool_input.command'` to extract the command.
- Keep hooks fast (< ~100ms). They run on every matched tool call.
- The Git guard exits 2 if jq/Python/shfmt is unavailable or inspection fails. Do not replace this with an `exit 0` fallback. The informational session hook exits 0 when no matching context exists.
- Output handling depends on the event and exit code: use stdout for session context and stderr for a blocked Git command’s reason.

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

- **`block-dangerous-git.sh`** — global memory rule: git commit and push are always run manually by the user, even after approval. The hook enforces this even if a session prompt forgets.
- **`session-start-ticket-context.sh`** — auto-resumes ticket context so the user doesn't have to remember to attach the ticket's docs. Works whether those docs live in the repo or in a shared per-ticket directory outside it.

The Git guard requires Python 3, jq, and [shfmt 3](https://github.com/mvdan/sh#shfmt) (`brew install shfmt` on macOS). Keep `git-command-guard.py` beside the shell hook when copying it manually. It uses shfmt's Bash syntax tree without executing the input: comments, redirects, and quoted heredoc bodies are distinguished from commands, including nested substitutions. Dynamic executable names, Git operations, and shell `-c` scripts are rejected when they cannot be inspected literally. Aliases and external scripts still require execution-level controls for complete coverage. A missing or failing parser blocks execution with exit code 2.
