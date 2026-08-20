# agcoco

> **agcoco** = **Ag**ent-**Co**ding-**Co**nfig — pronounced "AG-co-co".
> Personal dotfiles repo for AI agent-assisted coding.

Manages custom slash commands, sub-agents, skills, and per-tool symlinks for any CLI that follows the `AGENTS.md` convention (Claude Code, Codex, and easily extensible to Gemini / Cursor / Aider / Continue via `tools/<name>.sh`).

> Korean / 한국어: [README.kr.md](./README.kr.md)

## Architecture

```
  agcoco repo — one source of truth
  ├── AGENTS.md — canonical agent memory
  └── commands/ · agents/ · skills/ · hooks/ · settings.json
         │
         ▼
  ./install.sh — loops over tools/*.sh, auto-detects installed CLIs
         │
  ┌──────┴──────┐
  ▼             ▼
  ~/.claude/    ~/.codex/     (symlinks)
  └──────┬──────┘
         ▼
  ┌───▶ agent session
  │      │  writes
  │      ▼
  │   .plans/ · .research/ · .handoffs/
  │   commit messages · PR descriptions
  │      │
  └──────┘   read back at the start of the next session
```

## Quick Start

```bash
git clone <repo-url> ~/agcoco
cd ~/agcoco
./install.sh
```

## How it works

Three ways to fire a workflow — a slash command you type, a skill that auto-fires from your phrasing, or a sub-agent the running command spawns. The core agent loop reads context, plans, fans out to specialists, and folds findings back into a single answer.

- **Commands** (`/foo`) — you invoke explicitly. Full workflows.
- **Skills** — auto-fire when your phrasing matches the `description` field. No slash needed.
- **Agents** — Claude spawns them automatically inside a command. Specialized single tasks.

```
  your message
      │
      ▼
  routing — the agent reads it against the config it already loaded
      │
      ├─▶ commands/*.md      explicit: you typed /research
      │                      a fully scripted workflow
      │
      ├─▶ skills/*/SKILL.md  implicit: your phrasing matched a description
      │                      auto-loaded, no slash needed
      │
      ▼
  core loop — read · plan · delegate · observe · write
      │
      ├─▶ agents/*.md        1..N spawned in parallel
      │                      grep · analysis · web search · doc summary
      │◀─                    structured returns, folded back
      ▼
  one coherent answer + files written to disk
```

One supervisor plans and merges; the sub-agents it spawns run on cheaper models — 8 of the 12 on Sonnet, 3 on Haiku, 1 on Opus.

## What's Included

### Commands (18)

| Category | Commands |
|----------|----------|
| **Plan Lifecycle** | `/create-plan`, `/implement-plan`, `/iterate-plan`, `/validate-plan` |
| **Research & Debug** | `/research`, `/debug`, `/ask-codex` |
| **Session** | `/handoff`, `/resume-handoff` |
| **Test** | `/affected-endpoints` |
| **Commit & PR** | `/workfinish`, `/commit-mailplug`, `/commit-suggest`, `/pr-description` |
| **Claude Usage** | `/claude-usage-collect`, `/claude-usage-analyze`, `/claude-usage-report` |
| **Jira Automation** | `/jira-daily` (+ optional `scripts/jira-daily-setup.sh` for launchd cron) |

### Agents (12)

Commands trigger these automatically — you don't call them directly.

| Agent | Role |
|-------|------|
| `codebase-analyzer` | Code implementation analysis |
| `codebase-locator` | File/component location (Super Grep) |
| `codebase-pattern-finder` | Find similar patterns + code examples |
| `docs-locator` | Search past plans/research/handoffs |
| `docs-analyzer` | Extract insights from past documents |
| `web-search-researcher` | Web search for up-to-date info |
| `architecture-review` | Architecture risk analysis |
| `endpoint-analysis` | API endpoint behavior analysis |
| `pr-review-assistant` | PR risk-focused review |
| `consistency-check` | Data snapshot comparison |
| `document-summarizer` | Document summarization |
| `pr-description-generator` | PR description generation |

### Skills (21)

Ported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT). Skills auto-fire when your phrasing matches their `description` field — no slash command needed.

| Category | Skill | Triggers when you say… |
|----------|-------|------------------------|
| **engineering** | `setup-matt-pocock-skills` | "set up the engineering skills for this repo" — run first in any new project |
| | `grill-with-docs` | "stress-test this plan against our domain model" |
| | `to-prd` | "turn this conversation into a PRD" |
| | `to-issues` | "break this plan into issues" |
| | `triage` | "triage these incoming issues" |
| | `tdd` | "let's TDD this", "red-green-refactor" |
| | `diagnose` | "diagnose this bug", "this is broken/throwing/failing" |
| | `improve-codebase-architecture` | "find refactoring opportunities", "improve architecture" |
| | `prototype` | "let me prototype this", "try a few UI variations" |
| | `zoom-out` | "zoom out", "give me the bigger picture" |
| **productivity** | `grill-me` | "grill me on this plan", "interview me" |
| | `caveman` | (terse output mode) |
| | `write-a-skill` | "create a new skill" |
| **misc** | `git-guardrails-claude-code` | "block dangerous git commands", "add git safety hooks" |
| | `setup-pre-commit` | "set up pre-commit hooks", "add Husky + lint-staged" |
| | `migrate-to-shoehorn` | "replace `as` with shoehorn in tests" |
| | `scaffold-exercises` | "scaffold an exercise structure" |
| **personal** | `edit-article` | "edit/revise this article" |
| **in-progress** | `writing-fragments` | "ideate", "fragments", "raw material" |
| | `writing-shape` | "shape these notes into an article" |
| | `writing-beats` | "assemble this as a narrative" |

### Plugins (6)

Commands and skills also ship as installable plugin packs in `plugins/`. Cherry-pick a pack — you don't have to adopt the whole config.

```bash
/plugin marketplace add mskim/Agcoco
/plugin install engineering-skills@agcoco
/plugin install workflow@agcoco
```

### Hooks (2)

Non-LLM scripts that run on tool invocation or session events. The agent doesn't choose to honour them — the runtime enforces them.

| Hook | Event | Purpose |
|------|-------|---------|
| `block-dangerous-git.sh` | PreToolUse: Bash | Block `git commit/push/filter-repo/reset --hard` — require human approval |
| `session-start-ticket-context.sh` | SessionStart | On a Jira-style ticket branch, surface that ticket's docs — from a shared ticket-docs root (`$TICKET_DOCS_ROOT`) if there is one, else from `.plans/`, `.handoffs/`, `.research/` |

## Multi-Tool Support (`tools/` registry)

Tool-agnostic — `install.sh` runs a generic loop over `tools/*.sh`, auto-detects whatever CLIs are installed, and creates the declared symlinks. `AGENTS.md` is the **canonical** agent context (openclaw pattern); each tool's expected memory filename is a symlink to it.

**Shipped (verified):**

| File | Tool | Detection | Symlinks created |
|---|---|---|---|
| `tools/claude.sh` | Claude Code | `command -v claude` | `~/.claude/CLAUDE.md` → `AGENTS.md`, `commands`, `agents`, `skills`, `settings.json` |
| `tools/codex.sh` | Codex CLI | `command -v codex` | `~/.codex/AGENTS.md` → `AGENTS.md`, `skills` (same SKILL.md format) |
| `tools/codegraph.sh` | CodeGraph MCP | `command -v codegraph` | none — bootstrapped through the adapter's `TOOL_SETUP` hook |
| `tools/ponytail.sh` | Ponytail plugin | `command -v claude` | none — installed from the plugin marketplace by `TOOL_SETUP` |

**Add any other tool** — Gemini, Cursor agent, Aider, Continue, etc:

```bash
cp tools/_template.sh tools/<your-tool>.sh
$EDITOR tools/<your-tool>.sh    # fill in 4 vars: TOOL_NAME, TOOL_CMD, TOOL_DIR, TOOL_SYMLINKS
./install.sh                    # auto-detected from the next run on
```

`_template.sh` has commented-out example definitions for Gemini, Cursor, Aider, and Continue. See `tools/README.md` for the convention details. Tools whose CLI isn't installed are listed under the "skipped tools" section and skipped silently.

## Memory & State

Plain Markdown on disk is the memory. Plans, research notes, and handoffs all live as files the agent can read on the next session, on the next branch, or from a different machine — context survives the chat window.

```
  session 1 — /research → /create-plan → /handoff
      │
      ▼ writes
  .research/*.md · .plans/*.md · .handoffs/*.md
      │
      ▼ /resume-handoff · SessionStart hook
  session 2 — new chat · new branch · another machine
      │
      └─▶ appends to the same files (loops back to the top)
```

### Project Init

```bash
./install.sh init /path/to/project
```

Creates `CLAUDE.md` in the target project, and registers `.handoffs/`, `.plans/`, `.research/` in its `.gitignore`. The directories themselves are made on demand by `/handoff`, `/research`, and `/create-plan`.

## Output

Every workflow produces a concrete file or message — not just a chat reply. Commit messages follow team convention, PR descriptions write themselves, test reports get checked in for the next session to read.

## Docs

### Component reference
- [Slash Commands](docs/commands.en.md) ([KR](docs/commands.kr.md)) — 18 commands grouped by category
- [Sub-agents](docs/agents.en.md) ([KR](docs/agents.kr.md)) — 12 specialized agents Claude spawns
- [Hooks](docs/hooks.en.md) ([KR](docs/hooks.kr.md)) — 2 lifecycle hook scripts
- [Scripts](docs/scripts.en.md) ([KR](docs/scripts.kr.md)) — Standalone shell helpers
- [Plugins](docs/plugins.en.md) ([KR](docs/plugins.kr.md)) — 6 plugin marketplace bundles

### Guides
- [Onboarding Guide](docs/onboarding.md) — Intro for first-time users
- [Workflow Reference](WORKFLOW.md) — Full command & workflow reference
- [Submodule Approach](docs/approach-a-submodule.md) — Alternative structure for team sharing

## Inspired by

- [humanlayer/humanlayer](https://github.com/humanlayer/humanlayer) `.claude/` structure
