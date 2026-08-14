#!/bin/bash
# plugins/ 사본이 commands/ 원본에서 벗어났는지 검사한다.
#
# 왜 필요한가: plugins/ 는 심링크가 아니라 실물 복사본이다 (마켓플레이스로 배포되므로
# 리포 밖에서도 자립해야 한다). 그래서 commands/ 를 고쳐도 사본은 조용히 뒤처진다.
#
# 단, 모든 차이가 버그는 아니다. commands/ 쪽에 회사 워크스페이스 전용 경로 라우팅
# ($MAILWORK_ROOT, mailFramework/, issue/{TICKET}/) 이 들어가는 경우가 있는데 — 현재
# scripts/, hooks/ 가 그렇다 — 이건 공개 배포본에 넣으면 안 된다. commands/ 에도
# 그런 게 생기면 아래 DIVERGENT / UNPUBLISHED 에 이유와 함께 등록한다.
#
# 사용법: bash scripts/check-plugin-sync.sh
# 종료코드: 0 = 등록되지 않은 드리프트 없음, 1 = 있음

set -u
cd "$(dirname "$0")/.." || exit 1

# 의도적으로 다른 파일 — "사본=구버전"이 정답인 것들.
# 형식: "<plugin 상대경로>|<사유>"
#
# 지금은 비어있다. 등록은 **커밋된** 차이에 대해서만 하라 — 워킹트리에만 잠깐
# 보이는 차이(동기화 유입, 미커밋 실험)를 등록하면 그 항목이 이후의 진짜
# 드리프트까지 영구히 가려버린다. 여기 없는 차이는 체커가 알아서 잡아주므로,
# 잡힌 다음에 사유를 달아 추가하는 순서가 맞다.
DIVERGENT=()

# 의도적으로 어느 플러그인에도 넣지 않는 커맨드.
UNPUBLISHED=(
    "jira-daily.md|Mailplug 전용 — jira-auth-proxy MCP, WM- 티켓, mailFramework 경로에 결합"
)

is_listed() {
    local needle="$1"; shift
    local entry
    for entry in "$@"; do
        [ "${entry%%|*}" = "$needle" ] && return 0
    done
    return 1
}

fail=0

echo "=== 1. 플러그인 사본 vs commands/ 원본 ==="
for copy in plugins/*/commands/*.md; do
    [ -f "$copy" ] || continue
    src="commands/$(basename "$copy")"

    if [ ! -f "$src" ]; then
        echo "  [고아] $copy — commands/ 에 원본이 없다"
        fail=1
        continue
    fi

    diff -q "$copy" "$src" >/dev/null && continue

    # bash 3.2 + set -u 에서 빈 배열의 "${arr[@]}" 는 unbound 로 터진다.
    if is_listed "$copy" ${DIVERGENT[@]+"${DIVERGENT[@]}"}; then
        for entry in ${DIVERGENT[@]+"${DIVERGENT[@]}"}; do
            [ "${entry%%|*}" = "$copy" ] && echo "  [의도된 차이] $copy — ${entry#*|}"
        done
    else
        echo "  [드리프트] $copy — 원본과 다른데 사유가 등록돼 있지 않다"
        echo "             동기화하려면: cp $src $copy"
        echo "             의도된 차이라면 이 스크립트의 DIVERGENT 에 사유와 함께 추가하라"
        fail=1
    fi
done

echo ""
echo "=== 2. 어느 플러그인에도 없는 커맨드 ==="
for src in commands/*.md; do
    name=$(basename "$src")
    if find plugins -path "*/commands/$name" -print -quit | grep -q .; then
        continue
    fi

    if is_listed "$name" ${UNPUBLISHED[@]+"${UNPUBLISHED[@]}"}; then
        for entry in ${UNPUBLISHED[@]+"${UNPUBLISHED[@]}"}; do
            [ "${entry%%|*}" = "$name" ] && echo "  [의도된 제외] $name — ${entry#*|}"
        done
    else
        echo "  [미배포] $name — 어느 플러그인에도 없다"
        echo "           배포하려면 알맞은 plugins/<pack>/commands/ 에 복사하고"
        echo "           plugin.json / marketplace.json / docs/plugins.*.md 설명도 갱신하라"
        echo "           배포하지 않을 것이면 UNPUBLISHED 에 사유와 함께 추가하라"
        fail=1
    fi
done

echo ""
if [ "$fail" -eq 0 ]; then
    echo "[✓] 등록되지 않은 드리프트 없음"
else
    echo "[✗] 위 항목을 처리하라"
fi
exit "$fail"
