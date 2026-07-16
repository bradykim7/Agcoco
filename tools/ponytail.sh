# Ponytail — https://github.com/DietrichGebert/ponytail
# "게으른 시니어 개발자" 모드 Claude Code 플러그인. YAGNI/stdlib-first 강제로
# 과잉 엔지니어링을 막는다. codegraph 처럼 symlink 대상이 아니라
# "Claude Code 플러그인 마켓플레이스로 설치"하는 공유 의존성이라 TOOL_SETUP 훅으로 부트스트랩.
# 사용: /ponytail [lite|full|ultra|off], /ponytail-review, /ponytail-audit 등

TOOL_NAME="Ponytail"
TOOL_CMD="claude"             # Claude Code 플러그인이므로 claude 존재 여부로 감지
TOOL_DIR="$HOME/.claude"      # 감지/카운트용 placeholder — symlink 대상 없음
TOOL_SYMLINKS=()              # symlink 안 함 (훅이 모든 설정을 담당)

# install.sh 가 감지(detect-skip) 직전에 호출. 여러 번 실행해도 안전(멱등).
TOOL_SETUP() {
    # ── Claude Code ──
    if command -v claude &>/dev/null; then
        # 마켓플레이스 등록 (아직 없을 때만)
        if ! claude plugin marketplace list 2>/dev/null | grep -q 'DietrichGebert/ponytail'; then
            echo "    [*] Claude Code: ponytail 마켓플레이스 등록..."
            claude plugin marketplace add DietrichGebert/ponytail
        fi
        # 플러그인 설치 (아직 없을 때만)
        if ! claude plugin list 2>/dev/null | grep -q 'ponytail@ponytail'; then
            echo "    [*] Claude Code: ponytail 플러그인 설치..."
            claude plugin install ponytail@ponytail
        fi
    else
        echo "    [!] claude 없음 — Claude Code용 Ponytail 스킵"
    fi

    # ── Codex ──
    if command -v codex &>/dev/null; then
        # `codex plugin marketplace list` 는 이름만 출력 (URL 없음)
        if ! codex plugin marketplace list 2>/dev/null | grep -q '^ponytail\b'; then
            echo "    [*] Codex: ponytail 마켓플레이스 등록..."
            codex plugin marketplace add DietrichGebert/ponytail
        fi
        # `codex plugin list` 는 미설치 플러그인도 "not installed" 로 나열하므로 STATUS 까지 확인
        if ! codex plugin list 2>/dev/null | grep 'ponytail@ponytail' | grep -qv 'not installed'; then
            echo "    [*] Codex: ponytail 플러그인 설치..."
            codex plugin add ponytail@ponytail
            echo "    [i] Codex 첫 실행 시 /hooks 에서 ponytail 훅 2개를 trust 해야 활성화됩니다"
        fi
    fi
}
