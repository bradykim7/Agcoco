# Scripts

Standalone shell helpers under [`scripts/`](../scripts/) — installers, setup utilities, one-off automation. Unlike `hooks/` (auto-invoked by Claude Code) and `commands/` (invoked by `/<name>`), these scripts are run manually by the user from the terminal.

> 한국어: [scripts.kr.md](./scripts.kr.md)

## Inventory

| Script | Run as | Purpose |
|--------|--------|---------|
| [`jira-daily-setup.sh`](../scripts/jira-daily-setup.sh) | `./scripts/jira-daily-setup.sh` | Interactive macOS LaunchAgent installer for `/jira-daily`. Schedules the command headlessly (typically twice a day) with auto-detected `HOME`, node path, and working directory. |
| [`check-plugin-sync.sh`](../scripts/check-plugin-sync.sh) | `bash scripts/check-plugin-sync.sh` | Verifies `plugins/` copies haven't silently drifted from their `commands/` originals, and that every command is either published in a plugin or listed as deliberately unpublished. Exits 1 on unregistered drift. |

## Conventions

- Shebang at top (`#!/bin/bash` or `#!/usr/bin/env bash`).
- Make executable: `chmod +x scripts/your-script.sh`.
- Prereqs listed in a header comment.
- Prefer interactive prompts over hardcoded paths so the script works on a fresh machine.
- Validate platform if it's platform-specific (e.g., `[ "$(uname)" = "Darwin" ] || { echo "macOS only"; exit 1; }`).

## When to put something here vs. elsewhere

| Goal | Location |
|------|----------|
| User invokes via `/<name>` in Claude | [`commands/`](../commands/) |
| Triggered by Claude Code lifecycle event | [`hooks/`](../hooks/) |
| User runs manually from terminal | [`scripts/`](../scripts/) ← here |
| Tool registration consumed by `install.sh` | [`tools/`](../tools/) |

## Adding a new script

1. Drop the file in [`scripts/`](../scripts/); `chmod +x scripts/your-script.sh`.
2. Add prereqs + usage to a header comment block.
3. If it's a one-time setup, mention it in the repo `README.md` under "Setup".
4. No symlinks needed — these are invoked by absolute path from the repo.
