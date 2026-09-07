# Scripts

Standalone shell and Python helpers under [`scripts/`](../scripts/) — installers, setup utilities, one-off automation. Unlike `hooks/` (auto-invoked by Claude Code) and `commands/` (invoked by `/<name>`), these scripts are run manually by the user from the terminal.

> 한국어: [scripts.kr.md](./scripts.kr.md)

## Inventory

| Script | Run as | Purpose |
|--------|--------|---------|
| [`jira-daily-setup.sh`](../scripts/jira-daily-setup.sh) | `./scripts/jira-daily-setup.sh` | Interactive macOS LaunchAgent installer for `/jira-daily`. Schedules the command headlessly (typically twice a day) with auto-detected `HOME`, node path, and working directory. |
| [`check-plugin-sync.sh`](../scripts/check-plugin-sync.sh) | `bash scripts/check-plugin-sync.sh` | Checks command, skill, and agent copies; declared unpublished commands; and missing custom agents referenced by commands. Exits 1 on drift or missing dependencies. |
| [`check-agent-regressions.py`](../scripts/check-agent-regressions.py) | `python3 -B scripts/check-agent-regressions.py` | Offline CLI checks for invalid responses and same-named input files; no API calls. |
| [`check-shell-regressions.py`](../scripts/check-shell-regressions.py) | `python3 -B scripts/check-shell-regressions.py` | Git/home deletion guard, schedule parsing, backup preservation, init, and plugin checker regressions. No destructive commands or launchd registration. |

Run checks from the repository root with Python 3.10+, Bash, Git, jq, and shfmt 3 (`brew install shfmt` on macOS). The tests stub Anthropic, so no API key or SDK installation is needed. The Jira installer parses times in decimal (`08:30` is valid; `08:99` is rejected).

## Conventions

- Use a matching shebang: `#!/usr/bin/env bash` or `#!/usr/bin/env python3`.
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
4. No symlinks needed — run these directly from the repository, as shown above.
