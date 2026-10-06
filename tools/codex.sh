# Codex CLI — https://github.com/openai/codex
# 검증됨 (verified working). Codex는 Claude Code와 동일한 SKILL.md 포맷을 사용함.

TOOL_NAME="Codex CLI"
TOOL_CMD="codex"
TOOL_DIR="$HOME/.codex"

TOOL_SYMLINKS=(
    "AGENTS.md=AGENTS.md"
    "skills=skills"
    # 공식 문서의 현재 개인 스킬 경로. 0.159.1은 ~/.codex/skills도 읽고, 둘 다 있어도 실경로 기준으로 중복 제거됨.
    "../.agents/skills=skills"
)
