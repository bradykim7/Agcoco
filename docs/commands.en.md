# Slash Commands

Slash commands for Claude Code. Each `.md` file under [`commands/`](../commands/) is invoked as `/<filename>`.

`install.sh` symlinks the `commands/` directory into `~/.claude/commands/`. Routing rules — when each command auto-fires from natural phrasing — live in [`AGENTS.md`](../AGENTS.md#intent-routing--natural-phrasing--action).

> 한국어: [commands.kr.md](./commands.kr.md)

## Inventory

### Planning lifecycle
| Command | Purpose |
|---------|---------|
| [`/create-plan`](../commands/create-plan.md) | Build a structured implementation plan — research → design → phased plan |
| [`/iterate-plan`](../commands/iterate-plan.md) | Update an existing plan with feedback (research-driven) |
| [`/implement-plan`](../commands/implement-plan.md) | Implement plan phase-by-phase with auto-verification gates |
| [`/validate-plan`](../commands/validate-plan.md) | Verify implementation against the plan's success criteria |

### Research, debug, understanding
| Command | Purpose |
|---------|---------|
| [`/research`](../commands/research.md) | Parallel codebase exploration → research doc |
| [`/debug`](../commands/debug.md) | Broad parallel investigation (logs + git + files) when cause is unknown |
| [`/ask-codex`](../commands/ask-codex.md) | Blind cross-check — Claude and Codex answer independently, then rebut each other; this session's Claude judges rather than participates |

### Test
| Command | Purpose |
|---------|---------|
| [`/affected-endpoints`](../commands/affected-endpoints.md) | Trace HTTP endpoints affected by a code change |

### Commit & PR
| Command | Purpose |
|---------|---------|
| [`/commit-suggest`](../commands/commit-suggest.md) | Recommend a commit message from staged files + history |
| [`/commit-mailplug`](../commands/commit-mailplug.md) | Team-convention commit (ticket ID auto-detected) |
| [`/pr-description`](../commands/pr-description.md) | Generate PR description from diff + commits |
| [`/workfinish`](../commands/workfinish.md) | Commit-suggest + PR description in one run — "wrap up" |

### Session
| Command | Purpose |
|---------|---------|
| [`/handoff`](../commands/handoff.md) | Preserve session context so a future session can resume |
| [`/resume-handoff`](../commands/resume-handoff.md) | Restore context from a handoff doc and continue |

### Claude usage
| Command | Purpose |
|---------|---------|
| [`/claude-usage-collect`](../commands/claude-usage-collect.md) | Extract your own ccusage data into a shareable bundle |
| [`/claude-usage-analyze`](../commands/claude-usage-analyze.md) | Personal ROI / model-routing / session-hygiene report |
| [`/claude-usage-report`](../commands/claude-usage-report.md) | Team-wide report from collected bundles (8 sections; optional Confluence publish) |

### Jira
| Command | Purpose |
|---------|---------|
| [`/jira-daily`](../commands/jira-daily.md) | Analyze today's assigned Jira issues — macOS notification + plan doc |

## Conventions

- Filename = command name (no leading slash).
- Frontmatter `description:` is what's shown above.
- Korean and English commands are both supported; routing matches phrasing in either language.

## Adding a new command

1. Drop `your-command.md` in [`commands/`](../commands/) with frontmatter:
   ```yaml
   ---
   description: One-line summary shown in /help and this README
   ---
   ```
2. Re-run `./install.sh` from the repo root to symlink it into `~/.claude/commands/`.
3. If it should auto-fire from natural phrasing, add a routing entry in [`AGENTS.md`](../AGENTS.md#intent-routing--natural-phrasing--action).
