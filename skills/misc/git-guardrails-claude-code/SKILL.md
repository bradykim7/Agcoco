---
name: git-guardrails-claude-code
description: Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
---

# Setup Git Guardrails

Sets up a PreToolUse hook that intercepts and blocks dangerous git commands before Claude executes them.

## What Gets Blocked

- `git commit` (always blocked, even after approval; the user commits manually)
- `git push` (all variants including `--force`)
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

When blocked, Claude sees a message telling it that it does not have authority to access these commands.

## Steps

### 1. Ask scope

Ask the user: install for **this project only** (`.claude/settings.json`) or **all projects** (`~/.claude/settings.json`)?

### 2. Copy the hook script

Requires Bash, Python 3, jq and [shfmt 3](https://github.com/mvdan/sh#shfmt). Install shfmt before enabling the hook (`brew install shfmt` on macOS); the guard blocks if the parser is missing or fails. The bundled files are [scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh) and [scripts/git-command-guard.py](scripts/git-command-guard.py).

Copy it to the target location based on scope:

- **Project**: `.claude/hooks/block-dangerous-git.sh`
- **Global**: `~/.claude/hooks/block-dangerous-git.sh`

Copy `git-command-guard.py` into the same hooks directory. Keep both files together and make the shell script executable with `chmod +x`.

The guard uses shfmt's Bash syntax tree without executing the input. It inspects Git global options, shell `-c` wrappers, and commands inside substitutions; comments, redirects, and quoted heredoc bodies are distinguished from commands. Dynamic executable names, Git operations, and shell `-c` scripts are rejected when they cannot be inspected literally. Aliases and external scripts still require execution-level controls for complete coverage.

### 3. Add hook to settings

Add to the appropriate settings file:

**Project** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**Global** (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

If the settings file already exists, merge the hook into existing `hooks.PreToolUse` array — don't overwrite other settings.

### 4. Ask about customization

Ask if the user wants to customize other blocked operations in `git-command-guard.py`. Keep `git commit` unconditionally blocked; approval is not an exception.

### 5. Verify

Run a quick test:

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

Should exit with code 2 and print a BLOCKED message to stderr.
