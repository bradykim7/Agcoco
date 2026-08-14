# Claude Code — https://claude.com/claude-code
# 검증됨 (verified working).

TOOL_NAME="Claude Code"
TOOL_CMD="claude"
TOOL_DIR="$HOME/.claude"

# 각 항목: "<target relative to TOOL_DIR>=<source relative to DOTFILES_DIR>"
TOOL_SYMLINKS=(
    "CLAUDE.md=AGENTS.md"
    "DESIGN.md=DESIGN.md"
    "commands=commands"
    "agents=agents/claude-code"
    "skills=skills"
    "hooks=hooks"
    "settings.json=settings.json"
)
