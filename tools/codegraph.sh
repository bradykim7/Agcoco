# CodeGraph — https://github.com/colbymchenry/codegraph
# 로컬 코드 지식 그래프 MCP 서버. 자체 config 를 symlink 하는 peer 툴이 아니라,
# "설치 후 다른 에이전트(Claude/Codex)에 MCP 서버로 등록"하는 공유 의존성이다.
# 그래서 symlink 대신 install.sh 의 선택적 TOOL_SETUP 훅으로 부트스트랩한다.

TOOL_NAME="CodeGraph"
TOOL_CMD="codegraph"
TOOL_DIR="$HOME/.codegraph"   # 감지/카운트용 placeholder — symlink 대상 없음
TOOL_SYMLINKS=()              # symlink 안 함 (훅이 모든 설정을 담당)

# install.sh 가 감지(detect-skip) 직전에 호출. 여러 번 실행해도 안전(멱등).
TOOL_SETUP() {
    # 1) CodeGraph CLI 글로벌 설치 (없을 때만)
    if ! command -v codegraph &>/dev/null; then
        if command -v npm &>/dev/null; then
            echo "    [*] npm 으로 CodeGraph 설치..."
            npm install -g @colbymchenry/codegraph
        else
            echo "    [!] npm 없음 — CodeGraph 설치 스킵"
            return 0
        fi
    fi

    # 2) Claude Code 에 MCP 등록 (user 스코프, 아직 없을 때만)
    if command -v claude &>/dev/null; then
        if ! claude mcp list 2>/dev/null | grep -q '^codegraph:'; then
            echo "    [*] Claude Code 에 codegraph MCP 등록..."
            claude mcp add -s user codegraph -- codegraph serve --mcp
        fi
    fi

    # 3) Codex 에 MCP 등록 (아직 없을 때만)
    if command -v codex &>/dev/null; then
        if ! codex mcp list 2>/dev/null | grep -q 'codegraph'; then
            echo "    [*] Codex 에 codegraph MCP 등록..."
            codex mcp add codegraph -- codegraph serve --mcp
        fi
    fi
}
