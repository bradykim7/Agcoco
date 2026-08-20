# tools/

Tool registry for `install.sh`. Each `.sh` file declares one AI CLI / agent. `install.sh` sources every non-underscore file in this directory, detects whether the tool is installed, and creates the declared symlinks if so.

## Convention

Each tool file exports four variables:

| Variable | Purpose | Example |
|---|---|---|
| `TOOL_NAME` | Human-readable name shown in install output | `"Claude Code"` |
| `TOOL_CMD` | Binary name used for detection (`command -v $TOOL_CMD`) | `"claude"` |
| `TOOL_DIR` | The tool's config directory | `"$HOME/.claude"` |
| `TOOL_SYMLINKS` | Bash array of `"target=source"` pairs (target relative to `TOOL_DIR`, source relative to `DOTFILES_DIR`) | `("CLAUDE.md=AGENTS.md" "skills=skills")` |

## How `install.sh` processes a tool

```
for each tools/*.sh (excluding _-prefixed):
    source the file → load TOOL_NAME, TOOL_CMD, TOOL_DIR, TOOL_SYMLINKS
    if `command -v $TOOL_CMD` fails → log "미설치, 건너뜀" and continue
    mkdir -p $TOOL_DIR if missing
    for each "target=source" in TOOL_SYMLINKS:
        if $DOTFILES_DIR/source missing → warn and skip
        backup existing non-symlink at $TOOL_DIR/target → .bak
        remove existing symlink at $TOOL_DIR/target
        ln -s $DOTFILES_DIR/source $TOOL_DIR/target
    unset variables for next iteration
```

## Adding a new tool

```bash
cp tools/_template.sh tools/mytool.sh
$EDITOR tools/mytool.sh    # fill in the 4 variables
./install.sh               # picks up the new tool automatically
```

`_template.sh` contains commented-out example definitions for Gemini, Cursor, Aider, and Continue — uncomment and adapt as needed.

## Files starting with `_`

Skipped by the install loop. Useful for templates and disabled tools.

## Currently shipped

| File | Status | Notes |
|---|---|---|
| `claude.sh` | Verified | Primary; `install.sh` also auto-installs Claude Code via npm if missing |
| `codex.sh` | Verified | Shares `AGENTS.md` + `skills/` with Claude |
| `codegraph.sh` | Verified | Not a peer CLI — bootstraps the CodeGraph MCP server via `TOOL_SETUP`; creates no symlinks |
| `ponytail.sh` | Verified | Not a peer CLI — installs the Ponytail Claude Code plugin via `TOOL_SETUP`; creates no symlinks |
| `_template.sh` | Inert | Template + speculative examples |
