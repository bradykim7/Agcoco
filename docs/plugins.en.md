# Plugins

Claude Code plugin marketplace bundles under [`plugins/`](../plugins/). Each subdirectory is a self-contained plugin: a `.claude-plugin/plugin.json` manifest plus `commands/` and/or `skills/` shipped together.

These are consumed via the marketplace UI:

```bash
/plugin marketplace add mskim/Agcoco
/plugin install <plugin-name>@agcoco
```

The top-level [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) advertises every plugin in the directory.

> 한국어: [plugins.kr.md](./plugins.kr.md)

## Inventory

| Plugin | Contents | Purpose |
|--------|----------|---------|
| [`planning`](../plugins/planning/) | commands | Plan lifecycle — `create-plan`, `implement-plan`, `iterate-plan`, `validate-plan` |
| [`workflow`](../plugins/workflow/) | commands | Core meta commands — `workfinish`, `debug`, `research`, `ask-codex`, `handoff`, `resume-handoff` |
| [`testing`](../plugins/testing/) | commands | Affected-endpoint tracing — `affected-endpoints` |
| [`git-tools`](../plugins/git-tools/) | commands + skills | Commit & PR — `commit-mailplug`, `commit-suggest`, `pr-description` + `git-guardrails`, `setup-pre-commit` |
| [`engineering-skills`](../plugins/engineering-skills/) | skills | Engineering workflow skills — `diagnose`, `tdd`, `triage`, `to-prd`, `to-issues`, `zoom-out`, `improve-codebase-architecture`, `prototype`, `grill-with-docs`, `grill-me` |
| [`claude-usage`](../plugins/claude-usage/) | commands | Claude Code usage analytics — `claude-usage-collect`, `claude-usage-analyze`, `claude-usage-report` |

## Plugin vs. personal-install

| Install method | Where it lands | Best for |
|----------------|---------------|----------|
| `./install.sh` (symlinks) | `~/.claude/commands/`, `~/.claude/skills/`, `~/.claude/hooks/` | Personal use — get every command/skill/hook in one shot |
| `/plugin install <name>@agcoco` | Plugin-managed directories | Bundled sets — share specific themes with teammates without forcing the rest |

Both can coexist; the marketplace lets others adopt subsets without cloning the whole repo.

## Plugin layout

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json          ← name, description, version
├── commands/                ← (optional) slash commands shipped by this plugin
│   └── *.md
└── skills/                  ← (optional) skills shipped by this plugin
    └── <skill-name>/
        └── SKILL.md
```

## Adding a new plugin

1. Create `plugins/your-plugin/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "your-plugin",
     "description": "One-line summary",
     "version": "1.0.0"
   }
   ```
2. Add `commands/` and/or `skills/` next to the manifest.
3. Register the plugin in [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json).
4. Users install via `/plugin install your-plugin@agcoco`.
