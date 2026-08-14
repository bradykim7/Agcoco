---
description: 오늘 나에게 할당된 Jira 이슈 자동 분석 — macOS 알림 + 계획서 생성
allowed-tools: Read, Write, Glob, Grep, Bash(terminal-notifier:*), Bash(osascript:*), Bash(ls:*), Bash(date:*), Bash(mkdir:*), Bash(pwd:*), Bash(echo:*), mcp__jira-auth-proxy__jira_search, mcp__jira-auth-proxy__jira_get_issue, Agent
argument-hint: [선택: 특정 이슈 키 또는 추가 JQL 조건]
---

# Jira Daily — 오늘 할당된 이슈 자동 처리

오늘 나에게 새로 할당된 Jira 이슈를 가져와서:
1. macOS 알림으로 요약 전송 (Slack 스타일 압축, 클릭 시 파일/폴더 오픈)
2. 각 이슈마다 자동 리서치 + 계획서 생성
3. 완료 후 최종 요약 알림

수동 실행(`/jira-daily`) 또는 launchd 백그라운드 스케줄 모두 지원.

## 사전 준비

- macOS + `terminal-notifier` (`brew install terminal-notifier`) — 알림 클릭 액션용
- Jira MCP 서버 (`mcp__jira-auth-proxy__*`) 설정됨
  - 접두사는 로컬에 등록한 MCP 서버 **이름**을 따라갑니다. `claude mcp list`로 확인하고, 다르면 이 파일의 `mcp__` 참조를 그 이름으로 바꾸세요.
- 계획서 저장 폴더 (기본 `$PWD/.plans/`, 또는 `JIRA_DAILY_PLANS_DIR` 환경변수로 오버라이드)

---

## Step 0: 계획서 저장 경로 결정

가장 먼저 `Bash`로 다음 명령 실행해서 계획서 디렉토리 경로 확정:

```bash
PLANS_DIR="${JIRA_DAILY_PLANS_DIR:-$PWD/.plans}"
mkdir -p "$PLANS_DIR"
echo "PLANS_DIR=$PLANS_DIR"
```

이후 모든 단계에서 위에서 출력된 `PLANS_DIR` 값을 그대로 사용 (예: `/Users/foo/work/.plans`).

---

## Step 1: 인자 파싱

`$ARGUMENTS` 처리:
- 비어있음 → 기본 모드 (오늘 할당 이슈 전체)
- `WM-12345` 같은 KEY 패턴 → 단일 이슈 강제 처리 (이미 계획 있어도)
- 그 외 → 추가 JQL 조건으로 AND 결합

---

## Step 2: 이슈 조회

기본 JQL: `assignee = currentUser() AND created >= -1d ORDER BY created DESC`

`mcp__jira-auth-proxy__jira_search` 호출 (limit=20).

> **참고**: `assigned >= -1d`는 일부 Jira 인스턴스에서 미지원. `created >= -1d`를 프록시로 사용 (대부분 생성 ≈ 할당).

**결과 0건이면:**
```bash
terminal-notifier -title "🎫 Jira Daily" -message "오늘 새로 할당된 이슈가 없습니다" -sound Glass -execute "open $PLANS_DIR"
```
종료 후 사용자에게 "오늘 신규 이슈 없음" 보고.

---

## Step 3: 중복 체크

각 이슈에 대해:
- `Glob`으로 `$PLANS_DIR/*{KEY}*.md` 패턴 확인
- 이미 있으면 처리 목록에서 제외 (사용자가 명시적으로 KEY를 인자로 준 경우는 예외)

처리할 이슈가 0건이면:
```bash
terminal-notifier -title "🎫 Jira Daily" -message "신규 N건 모두 이미 계획서 존재" -sound Glass -execute "open $PLANS_DIR"
```

---

## Step 4: 시작 알림

처리 대상 N건이 있으면:
```bash
terminal-notifier -title "🎫 Jira Daily" -subtitle "신규 N건 처리" -message "[KEY1, KEY2, ...] 분석 시작" -sound Hero -execute "open $PLANS_DIR"
```

---

## Step 5: 각 이슈 처리 (반복)

### 5a. 상세 정보 가져오기
`mcp__jira-auth-proxy__jira_get_issue`로 description + 댓글 포함 전체 정보.

### 5b. 코드베이스 리서치 (Agent)
`codebase-locator` 에이전트 호출:

```
Jira 이슈 {KEY}: {summary}

Description:
{description 일부, 500자 이내}

이 이슈와 관련된 코드/파일을 현재 작업 디렉토리(또는 상위) 하위에서 찾아주세요.

200단어 이내로 보고:
- 관련 파일 경로 (file:line)
- 비슷한 기능/패턴이 이미 있는지
- 영향 받을 가능성이 있는 모듈
- 어느 모듈/디렉토리가 메인 작업 대상인지 추정
```

### 5c. 계획서 작성

파일 경로: `$PLANS_DIR/{YYYY-MM-DD}-{KEY}-{kebab-summary}.md`
- `{YYYY-MM-DD}`: 오늘 날짜 (`date +%Y-%m-%d`)
- `{kebab-summary}`: summary를 kebab-case로 (한글이면 핵심 영문 키워드 추출)

템플릿:
```markdown
---
date: {YYYY-MM-DD}
ticket: {KEY}
title: {summary}
status: 자동 생성됨 (검토 필요)
generated_by: /jira-daily
---

# {KEY}: {summary}

## Jira 정보
- **Status**: {status}
- **Reporter**: {reporter.displayName}
- **Created**: {created}
- **Priority**: {priority}
- **URL**: {jira self URL → browse 링크 변환}

## 요구사항 (Jira description)
{description — 마크다운 변환, 너무 길면 핵심만 발췌}

## 댓글 (최근 3개)
{최근 댓글 요약 — 있으면}

## 관련 코드 (자동 탐색 결과)
{codebase-locator 결과}

## 제안 접근 방향
> 자동 생성된 초안. `/create-plan {KEY}`로 상세 계획 수립 권장.

1. [Jira description 기반 1차 추정 단계]
2. [관련 코드 분석에서 도출한 단계]
3. [검증/테스트 단계]

## 확인 필요 사항
- [Jira 본문/댓글에서 모호한 부분]
- [Reporter에게 물어야 할 부분]

## 다음 단계
- [ ] 요구사항 명확화 (Reporter 확인)
- [ ] `/create-plan {KEY}` 실행해서 상세 계획 작성
- [ ] 구현 시작
```

### 5d. 개별 알림 (클릭 시 해당 .md 파일 오픈)
```bash
terminal-notifier -title "✅ {KEY}" -subtitle "{summary 30자 이내}" -message "계획서 생성됨 — 클릭해서 열기" -sound Glass -execute "open $PLANS_DIR/{파일명}"
```

---

## Step 6: 최종 요약

모든 이슈 처리 후 (클릭 시 폴더 오픈):

```bash
terminal-notifier -title "🎫 Jira Daily 완료" -subtitle "신규 {N}건 처리됨" -message "{N}건 분석 완료 — 클릭해서 폴더 열기" -sound Hero -execute "open $PLANS_DIR"
```

대화창에는 표 형식으로:

```
| KEY | Summary | Plan |
|-----|---------|------|
| WM-XXXXX | ... | $PLANS_DIR/2026-MM-DD-... |
```

---

## 동작 원칙

- **읽기 전용 + 파일 생성만** — Jira 업데이트, 트랜지션 변경 안 함
- **중복 방지** — 이미 계획서 있으면 스킵 (인자 명시 제외)
- **빠르게** — 이슈당 처리 시간 1-2분 목표 (긴 리서치 X)
- **초안일 뿐** — 계획서는 검토용 초안, 사용자가 `/create-plan`으로 정식 수립
- **알림은 짧게** — Slack DM 한 줄 느낌으로 압축
- **경로는 환경변수 우선** — `JIRA_DAILY_PLANS_DIR` > `$PWD/.plans`

---

## launchd 자동 스케줄 (옵션)

평일 정해진 시간에 자동 실행하려면 다음 중 하나:

**팀용 setup 스크립트 (권장):**
```bash
bash <(curl -fsSL ...)/scripts/jira-daily-setup.sh
# 또는 Agcoco 레포에서:
"$(dirname "$(readlink ~/.claude/CLAUDE.md)")/scripts/jira-daily-setup.sh"
```
대화형으로 작업 디렉토리/스케줄 시간 입력받아 launchd 등록.

**수동 등록**: `~/Library/LaunchAgents/com.{user}.jira-daily.plist` 직접 작성 후 `launchctl bootstrap gui/$(id -u) <plist>`. setup 스크립트 출력 참고.

⚠️ launchd는 Mac이 켜져 있고 사용자가 로그인된 상태여야 발화. 잠자기 중에는 미실행 (깨어나면 catch-up 시도).
