# skills/

Claude Code skills ported verbatim from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT licensed — see `LICENSE.mattpocock`).

## Structure

Each subfolder is a category. Each skill is a folder containing `SKILL.md` (frontmatter + body) and optional supporting files.

| Category | Skills |
|---|---|
| `engineering/` | diagnose, grill-with-docs, improve-codebase-architecture, prototype, setup-matt-pocock-skills, tdd, to-issues, to-prd, triage, zoom-out |
| `productivity/` | caveman, grill-me, write-a-skill |
| `misc/` | git-guardrails-claude-code, migrate-to-shoehorn, scaffold-exercises, setup-pre-commit |
| `personal/` | edit-article |
| `in-progress/` | writing-beats, writing-fragments, writing-shape |

## Install

`./install.sh install` first regenerates gitignored flat per-skill symlinks (`skills/<name>` → `<category>/<name>`, since Claude Code and Codex scan only one level deep), then links this directory to `~/.claude/skills` and, if Codex is installed, to `~/.codex/skills` and `~/.agents/skills`.

## Source

- Upstream: https://github.com/mattpocock/skills
- License: MIT (Copyright 2026 Matt Pocock) — full text in `LICENSE.mattpocock`
- Ported: 2026-05-08 (deprecated/ category excluded)
