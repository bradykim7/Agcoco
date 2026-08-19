#!/bin/bash
set -e

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOLS_DIR="$DOTFILES_DIR/tools"
CLAUDE_DIR="$HOME/.claude"  # Claude Code 부트스트랩(Step 1)에서만 사용; symlink 설치는 tools/claude.sh 로

# ─────────────────────────────────────────────
# 서브커맨드 분기
# ─────────────────────────────────────────────
SUBCMD="${1:-install}"

case "$SUBCMD" in
    init)
        # ─────────────────────────────────────
        # init: 프로젝트 레포에 CLAUDE.md 생성
        # ─────────────────────────────────────
        TARGET_DIR="${2:-.}"
        # 틸드(~)를 $HOME으로 확장 (변수 안의 틸드는 쉘이 자동 확장하지 않음)
        TARGET_DIR="${TARGET_DIR/#\~/$HOME}"
        TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
        CLAUDE_MD="$TARGET_DIR/CLAUDE.md"

        echo "=== Claude Code Per-Repo Init ==="
        echo "대상: $TARGET_DIR"
        echo ""

        if [ -f "$CLAUDE_MD" ]; then
            echo "[!] CLAUDE.md가 이미 존재합니다: $CLAUDE_MD"
            echo "    덮어쓰려면 삭제 후 다시 실행하세요."
            exit 1
        fi

        # 프로젝트 정보 자동 감지
        PROJECT_NAME=$(basename "$TARGET_DIR")
        GIT_REMOTE=$(cd "$TARGET_DIR" && git remote get-url origin 2>/dev/null || echo "N/A")

        # 언어/타입 감지
        if [ -f "$TARGET_DIR/composer.json" ]; then
            LANG="PHP"; TYPE="PHP Project"
        elif [ -f "$TARGET_DIR/package.json" ]; then
            LANG="TypeScript/JavaScript"; TYPE="Node.js Project"
        elif [ -f "$TARGET_DIR/pom.xml" ] || [ -f "$TARGET_DIR/build.gradle" ]; then
            LANG="Java"; TYPE="Java Project"
        elif [ -f "$TARGET_DIR/requirements.txt" ] || [ -f "$TARGET_DIR/pyproject.toml" ]; then
            LANG="Python"; TYPE="Python Project"
        elif [ -f "$TARGET_DIR/go.mod" ]; then
            LANG="Go"; TYPE="Go Project"
        elif [ -f "$TARGET_DIR/Cargo.toml" ]; then
            LANG="Rust"; TYPE="Rust Project"
        else
            LANG="Unknown"; TYPE="Project"
        fi

        # 디렉토리 구조 (1레벨)
        DIR_TREE=$(cd "$TARGET_DIR" && ls -d */ 2>/dev/null | head -10 | sed 's/^/├── /' || echo "├── (empty)")

        # 템플릿으로 CLAUDE.md 생성
        cat > "$CLAUDE_MD" << CLAUDEEOF
# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

- **Project**: $PROJECT_NAME
- **Type**: $TYPE
- **Language**: $LANG
- **Remote**: $GIT_REMOTE

## Directory Structure

\`\`\`
$DIR_TREE
\`\`\`

## Development Commands

### Build
\`\`\`bash
# TODO: 빌드 명령 추가
\`\`\`

### Test
\`\`\`bash
# TODO: 테스트 명령 추가
\`\`\`

### Lint
\`\`\`bash
# TODO: 린트 명령 추가
\`\`\`

### Run (Dev)
\`\`\`bash
# TODO: 개발 서버 실행 명령 추가
\`\`\`

## Technical Guidelines

- TODO: 코드 스타일 가이드 추가
- TODO: 프로젝트 컨벤션 추가

## Important Notes

- TODO: 프로젝트 특이사항 추가
CLAUDEEOF

        # 디렉토리는 미리 만들지 않는다 — .handoffs/.plans/.research 는
        # /handoff·/research·/create-plan 이 실제로 쓸 때 생성된다.
        # 커밋 사고만 막도록 .gitignore 패턴은 미리 등록한다.
        GITIGNORE="$TARGET_DIR/.gitignore"
        if [ -f "$GITIGNORE" ]; then
            for PATTERN in ".handoffs/" ".plans/" ".research/"; do
                if ! grep -qF "$PATTERN" "$GITIGNORE" 2>/dev/null; then
                    echo "$PATTERN" >> "$GITIGNORE"
                fi
            done
        fi

        echo "[✓] CLAUDE.md 생성 완료: $CLAUDE_MD"
        echo ""
        echo "다음 단계:"
        echo "  1. CLAUDE.md의 TODO 항목을 프로젝트에 맞게 수정"
        echo "  2. 필요시 .gitignore에 .handoffs/ .plans/ .research/ 추가 여부 확인"
        exit 0
        ;;

    install|"")
        # 아래 기존 install 로직으로 계속
        ;;

    help|--help|-h)
        echo "사용법: ./install.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  install                 글로벌 설치 (기본값) — ~/.claude/ + (감지 시) ~/.codex/ symlink 생성"
        echo "  init [path]             프로젝트 초기화 — CLAUDE.md 생성 + .gitignore 패턴 등록"
        echo "  help                    이 도움말 표시"
        echo ""
        echo "멀티툴 지원:"
        echo "  - install 실행 시 tools/*.sh 의 모든 정의를 순회하며 설치된 CLI 자동 감지"
        echo "  - 기본 포함: Claude Code, Codex CLI"
        echo "  - 새 툴 추가: cp tools/_template.sh tools/<name>.sh 후 4개 변수만 채우면 끝"
        echo "  - 자세히: tools/README.md"
        echo ""
        echo "Examples:"
        echo "  ./install.sh                                    # 글로벌 설치"
        echo "  ./install.sh init .                             # 현재 디렉토리 프로젝트 초기화"
        echo "  ./install.sh init ~/my-project                  # 특정 프로젝트 초기화"
        exit 0
        ;;

    *)
        echo "[✗] 알 수 없는 명령: $SUBCMD"
        echo "    ./install.sh help 로 사용법을 확인하세요."
        exit 1
        ;;
esac

# ─────────────────────────────────────────────
# install: 글로벌 설치 (기존 로직)
# ─────────────────────────────────────────────

echo "=== AI Agent Dotfiles Installer ==="
echo "  멀티툴 지원: tools/*.sh 에 정의된 모든 CLI를 자동 감지하여 symlink"
echo ""

# Step 1: Claude Code 부트스트랩 — primary tool 이므로 미설치 시 npm 자동 설치 제안
#         (다른 툴들은 사용자가 직접 설치한 경우에만 symlink 됨)
if ! command -v claude &> /dev/null; then
    echo "[!] Claude Code가 설치되어 있지 않습니다."
    echo ""

    if command -v npm &> /dev/null; then
        echo "[*] npm으로 Claude Code를 설치합니다..."
        npm install -g @anthropic-ai/claude-code
        echo "[✓] Claude Code 설치 완료"
    else
        echo "[✗] npm이 설치되어 있지 않습니다."
        echo "    다음 중 하나를 실행해주세요:"
        echo ""
        echo "    # npm 사용"
        echo "    npm install -g @anthropic-ai/claude-code"
        echo ""
        echo "    # 또는 직접 설치 후 다시 실행"
        echo "    # https://docs.anthropic.com/en/docs/claude-code"
        exit 1
    fi
fi

echo "[✓] Claude Code: $(claude --version 2>/dev/null || echo 'installed')"
echo ""

# ─────────────────────────────────────────────
# Step 1.5: skills/ 평탄화 심링크 재생성
# ─────────────────────────────────────────────
# Claude Code / Codex 는 <skills-dir>/<name>/SKILL.md 딱 한 단계만 탐색한다.
# 리포는 skills/<category>/<name>/ 로 분류해두므로 그대로 두면 카테고리 디렉토리가
# 스킬 이름 자리를 차지해 아무것도 발견되지 않는다. 최상위에 이름별 심링크를
# 만들어 분류와 탐색을 동시에 만족시킨다.
#   - 상대 심링크라 리포에 커밋되며 다른 머신에서도 그대로 동작
#   - Step 2 에서 skills/ 디렉토리 전체를 심링크하므로 Claude/Codex 양쪽에 함께 적용됨
#   - `.system/` 은 Claude 가 관리하는 내부 스킬이라 건드리지 않음 (글롭이 dotfile 미매치)
SKILLS_DIR="$DOTFILES_DIR/skills"
if [ -d "$SKILLS_DIR" ]; then
    echo "[*] skills/ 평탄화 심링크 재생성"

    # 기존 최상위 심링크 정리 — 스킬 이름이 바뀌거나 삭제됐을 때 유령 링크가 남지 않도록.
    # 실제 파일(README.md, LICENSE.*)과 카테고리 디렉토리는 심링크가 아니므로 보존된다.
    for link in "$SKILLS_DIR"/*; do
        if [ -L "$link" ]; then
            rm "$link"
        fi
    done

    skill_count=0
    for skill_md in "$SKILLS_DIR"/*/*/SKILL.md; do
        [ -f "$skill_md" ] || continue
        skill_dir=$(dirname "$skill_md")
        skill_name=$(basename "$skill_dir")
        skill_category=$(basename "$(dirname "$skill_dir")")

        if [ -e "$SKILLS_DIR/$skill_name" ]; then
            echo "    [!] 이름 충돌 — 스킵: $skill_category/$skill_name"
            continue
        fi

        ln -s "$skill_category/$skill_name" "$SKILLS_DIR/$skill_name"
        skill_count=$((skill_count + 1))
    done

    echo "    [✓] 스킬 $skill_count 개 연결"
    echo ""
fi

# ─────────────────────────────────────────────
# Step 2: 멀티툴 symlink — tools/ 디렉토리의 정의 자동 로딩
# ─────────────────────────────────────────────
# 각 tools/<name>.sh 가 TOOL_NAME / TOOL_CMD / TOOL_DIR / TOOL_SYMLINKS 4개 변수를
# export 함. 이 install_tool 함수가 그 정의를 받아서:
#   1) command -v $TOOL_CMD 로 설치 확인 → 미설치면 스킵
#   2) $TOOL_DIR mkdir -p
#   3) TOOL_SYMLINKS 의 각 "target=source" 엔트리에 대해 backup + symlink

INSTALLED_TOOLS=()
SKIPPED_TOOLS=()
INSTALLED_SYMLINKS=()

install_tool() {
    local tool_file="$1"
    local tool_basename
    tool_basename=$(basename "$tool_file" .sh)

    # _ 로 시작하는 파일은 템플릿/비활성 — 스킵
    if [[ "$tool_basename" == _* ]]; then
        return
    fi

    # 이전 sourced 값 정리
    unset TOOL_NAME TOOL_CMD TOOL_DIR
    unset -f TOOL_SETUP 2>/dev/null || true
    TOOL_SYMLINKS=()

    # shellcheck source=/dev/null
    source "$tool_file"

    # 필수 변수 검증
    if [ -z "$TOOL_NAME" ] || [ -z "$TOOL_CMD" ] || [ -z "$TOOL_DIR" ]; then
        echo "[!] $tool_basename: TOOL_NAME/CMD/DIR 누락 — 스킵"
        return
    fi

    # 선택적 setup 훅 — 감지 전에 실행. 아직 미설치인 공유 의존성(예: MCP 서버 CLI)이
    # 스스로 설치/등록하게 함. 훅 미정의 시 아무 동작 없음(기존 툴 그대로).
    if declare -F TOOL_SETUP >/dev/null 2>&1; then
        echo "[*] $TOOL_NAME: setup 훅 실행"
        TOOL_SETUP || echo "    [!] $TOOL_NAME setup 훅 실패 — 계속 진행"
    fi

    # 감지
    if ! command -v "$TOOL_CMD" &> /dev/null; then
        echo "[i] $TOOL_NAME ($TOOL_CMD) 미설치 — 건너뜀"
        SKIPPED_TOOLS+=("$TOOL_NAME")
        return
    fi

    echo "[*] $TOOL_NAME 감지됨 → $TOOL_DIR/ 설정"
    mkdir -p "$TOOL_DIR"

    local entry target_rel source_rel target_path source_path
    for entry in "${TOOL_SYMLINKS[@]}"; do
        target_rel="${entry%%=*}"
        source_rel="${entry#*=}"
        target_path="$TOOL_DIR/$target_rel"
        source_path="$DOTFILES_DIR/$source_rel"

        if [ ! -e "$source_path" ]; then
            echo "    [!] source 없음 — 스킵: $source_rel"
            continue
        fi

        # 기존 실제 파일/디렉토리는 .bak 백업
        if [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
            echo "    기존 $target_rel 백업 → $target_rel.bak"
            mv "$target_path" "$target_path.bak"
        elif [ -L "$target_path" ]; then
            rm "$target_path"
        fi

        # nested target (e.g., "plugins/foo/data.json") 지원
        mkdir -p "$(dirname "$target_path")"

        ln -s "$source_path" "$target_path"
        echo "    [✓] $target_path → $source_path"
        INSTALLED_SYMLINKS+=("$target_path")
    done

    INSTALLED_TOOLS+=("$TOOL_NAME")
    echo ""
}

if [ ! -d "$TOOLS_DIR" ]; then
    echo "[✗] tools/ 디렉토리를 찾을 수 없습니다: $TOOLS_DIR"
    exit 1
fi

for tool_file in "$TOOLS_DIR"/*.sh; do
    [ -f "$tool_file" ] && install_tool "$tool_file"
done

echo ""
echo "=== 설치 완료! ==="
echo ""
if [ ${#INSTALLED_TOOLS[@]} -gt 0 ]; then
    echo "활성화된 툴 (${#INSTALLED_TOOLS[@]}): ${INSTALLED_TOOLS[*]}"
fi
if [ ${#SKIPPED_TOOLS[@]} -gt 0 ]; then
    echo "건너뛴 툴   (${#SKIPPED_TOOLS[@]}): ${SKIPPED_TOOLS[*]}  ← 설치 후 ./install.sh 재실행하면 자동 연결"
fi
echo ""
if [ ${#INSTALLED_SYMLINKS[@]} -gt 0 ]; then
    echo "생성된 symlinks:"
    ls -la "${INSTALLED_SYMLINKS[@]}"
fi
echo ""
echo "사용 가능한 커맨드:"
echo ""
echo "  === 워크플로우 (메타) ==="
echo "  /workfinish         - 작업 마무리 (커밋 + PR 설명)"
echo ""
echo "  === 계획 라이프사이클 ==="
echo "  /create-plan        - 구조적 구현 계획 수립"
echo "  /implement-plan     - 계획서 Phase별 구현"
echo "  /iterate-plan       - 기존 계획서 수정"
echo "  /validate-plan      - 구현 결과 검증"
echo ""
echo "  === 리서치 & 디버깅 ==="
echo "  /research           - 코드베이스 구조적 탐색"
echo "  /debug              - 구조적 디버깅 (병렬 조사)"
echo ""
echo "  === 세션 관리 ==="
echo "  /handoff            - 세션 인수인계 문서 작성"
echo "  /resume-handoff     - 핸드오프에서 작업 재개"
echo ""
echo "  === 테스트 ==="
echo "  /affected-endpoints - 영향받는 엔드포인트 추적"
echo ""
echo "  === 커밋 & PR ==="
echo "  /commit-mailplug    - 팀 컨벤션 커밋 메시지 추천"
echo "  /commit-suggest     - 일반 커밋 메시지 추천"
echo "  /pr-description     - PR 설명 자동 생성"
echo ""
echo "  === Claude Code 사용 통계 ==="
echo "  /claude-usage-collect  - 본인 사용 데이터 수집 → 공유 zip 생성 (팀원 배포용)"
echo "  /claude-usage-analyze  - 본인 사용 분석 → 개인 리포트 생성"
echo "  /claude-usage-report   - 팀원 JSON 수합 → 8섹션 팀 리포트 (+Confluence 옵션)"
echo ""
echo "프로젝트 초기화: ./install.sh init /path/to/project"
echo "워크플로우:     $DOTFILES_DIR/WORKFLOW.md"
