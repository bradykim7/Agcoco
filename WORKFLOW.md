# Claude Code 작업 워크플로우

## 전체 커맨드 목록

### 메타 커맨드 (플로우 한번에 실행)

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| **`/workfinish`** | 커밋 추천 + PR 설명 한번에 | `/workfinish` |

### 계획 라이프사이클 커맨드

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| `/create-plan` | 구조적 구현 계획 수립 (조사→설계→계획서) | `/create-plan 검색 필터 추가` |
| `/implement-plan` | 계획서 Phase별 구현 + 자동/수동 검증 | `/implement-plan .plans/2026-04-08-desc.md` |
| `/iterate-plan` | 기존 계획서 피드백 반영 수정 | `/iterate-plan .plans/파일.md Phase 2 분리` |
| `/validate-plan` | 구현 결과 전체 검증 + 리포트 | `/validate-plan` |

### 리서치 & 디버깅 커맨드

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| `/research` | 코드베이스 구조적 탐색 & 리서치 문서 | `/research 인증 플로우 분석` |
| `/debug` | 구조적 디버깅 (병렬 조사) | `/debug 500 에러 발생` |
| `/ask-codex` | Claude ↔ Codex 블라인드 교차 검증 (독립 답변 → 교차 반론 → 이견 병기) | `/ask-codex 이 락 전략 안전한가?` |

**`/ask-codex` 구조**: R0에서 Claude 서브에이전트와 Codex가 **서로의 답을 모르는 채로** 각자 답하고(앵커링 방지), R1에서 상대 답변만 받아 교차 반론합니다. 이 세션의 Claude는 참가자가 아니라 심판이라 초안을 쓰지 않으며, 합의되지 않은 지점은 한쪽으로 정리하지 않고 양쪽 입장을 병기합니다.

**사전 준비**: `codex` CLI 설치 + 로그인. 모델 미지정 시 `~/.codex/config.toml`의 기본값(`gpt-5.6-sol`)을 사용하며 `--model`로 덮어쓸 수 있습니다. Codex는 `--sandbox read-only`로 현재 디렉토리를 읽으므로, 외부에 노출하면 안 되는 리포에서는 실행 위치를 확인하세요.

### 세션 관리 커맨드

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| `/handoff` | 세션 인수인계 문서 작성 | `/handoff` |
| `/resume-handoff` | 핸드오프에서 작업 재개 | `/resume-handoff .handoffs/2026-04-08_14-30-00_desc.md` |

### 테스트 커맨드

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| `/affected-endpoints` | 영향 엔드포인트 추적 (읽기 전용) | `/affected-endpoints` |

### 커밋 & PR 커맨드

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| `/commit-mailplug` | 팀 컨벤션 커밋 메시지 추천 | `/commit-mailplug` |
| `/pr-description` | PR 설명 자동 생성 | `/pr-description` |
| `/commit-suggest` | 일반 커밋 메시지 추천 | `/commit-suggest` |

### Claude Code 사용 통계 커맨드

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| `/claude-usage-collect` | 본인 사용 데이터 수집 → 공유 zip 생성 | `/claude-usage-collect` |
| `/claude-usage-analyze` | 본인 사용 분석 → 개인 리포트 | `/claude-usage-analyze 14d` |
| `/claude-usage-report` | 팀원 JSON 수합 → 8섹션 팀 리포트 | `/claude-usage-report ./team-data 212482160` |

**플로우**: 팀원들이 `collect` 실행 → zip 수합 → 팀장이 `report`로 통합 분석. 개인은 `analyze`로 스스로 점검.

### Jira 자동화 커맨드

| 커맨드 | 용도 | 입력 예시 |
|--------|------|-----------|
| `/jira-daily` | 오늘 새로 할당된 Jira 이슈 자동 분석 + macOS 알림 + 계획서 초안 생성 | `/jira-daily` 또는 `/jira-daily WM-XXXXX` |

**플로우**: 수동 실행이 기본. launchd 백그라운드 스케줄을 원하면 `scripts/jira-daily-setup.sh` 한 번 실행 → 평일 정해진 시간에 자동 발화 → macOS 알림 → 클릭 시 `.plans/` 폴더 또는 해당 `.md` 파일 오픈.

- 사전 준비: `brew install terminal-notifier` + Jira MCP 설정
- 계획서 저장: `$JIRA_DAILY_PLANS_DIR` env (기본 `$PWD/.plans/`)
- 자동 스케줄 설치: `bash "$(dirname "$(readlink ~/.claude/CLAUDE.md)")/scripts/jira-daily-setup.sh"` (대화형, 시간/디렉토리 선택)

---

## 빠른 사용법 (메타 커맨드)

```
git checkout -b feature/WM-XXXXX
# 코드 작업...

/workfinish             ← 커밋 + PR 설명 생성
```

이것만으로 전체 플로우가 완료됩니다. 세부 제어가 필요하면 아래 개별 커맨드를 사용하세요.

---

## 개발 워크플로우 (NEW)

### 계획 → 구현 → 검증 → 인수인계 (Full Lifecycle)

```
/create-plan 기능 설명        ← 1. 조사 → 설계 → 계획서 작성
/iterate-plan 피드백          ← 2. 계획 수정 (필요시 반복)
/implement-plan               ← 3. Phase별 구현 + 자동 검증
/validate-plan                ← 4. 구현 결과 전체 검증
/debug 에러 설명              ←    문제 발생 시 병렬 조사
/workfinish                   ← 5. 커밋 + PR 생성
/handoff                      ← 6. 세션 종료 시 인수인계
/resume-handoff               ←    다음 세션에서 이어서
```

### 코드베이스 이해

```
/research 주제                ← 코드베이스 탐색 & 문서화
```

### 에이전트 자동 호출 흐름 (예시)

```
사용자: /create-plan 메일 검색 필터 추가

Claude (Opus):
  ├─ spawn codebase-locator (Sonnet)       ← 관련 파일 찾기
  ├─ spawn codebase-analyzer (Sonnet)      ← 기존 구현 분석
  ├─ spawn codebase-pattern-finder (Sonnet) ← 유사 패턴 검색
  ├─ spawn docs-locator (Sonnet)           ← 과거 관련 문서 탐색
  └─ 종합하여 구현 계획서 작성
```

### 프로젝트 초기화

```bash
# 새 프로젝트에서 Claude Code 초기화
./install.sh init /path/to/project

# 생성되는 것:
#   CLAUDE.md       ← 프로젝트별 AI 지침 (TODO 항목 편집)
#   .handoffs/      ← 핸드오프 문서 저장소
#   .plans/         ← 구현 계획서 저장소
#   .research/      ← 리서치 문서 저장소
```

---

## 자동 서브에이전트 (NEW — humanlayer 영감)

커맨드와 달리, 에이전트는 **사용자가 직접 호출하지 않습니다.** Claude가 작업 중 필요할 때 자동으로 spawns 합니다.

### 에이전트 목록

| 에이전트 | 용도 | 자동 호출 시점 |
|----------|------|---------------|
| `codebase-analyzer` | 코드 구현 상세 분석 (데이터 흐름, 로직) | `/create-plan`, `/research`, `/debug` |
| `codebase-locator` | 파일/컴포넌트 위치 탐색 (Super Grep) | `/create-plan`, `/research`, `/implement-plan`, `/debug` |
| `codebase-pattern-finder` | 유사 구현/패턴 찾기 + 코드 예시 | `/create-plan`, `/research`, `/implement-plan` |
| `docs-locator` | 과거 문서 탐색 (.plans/.research/.handoffs/) | `/create-plan`, `/research`, `/resume-handoff`, `/debug` |
| `docs-analyzer` | 과거 문서 인사이트 추출 (의사결정, 제약) | `/resume-handoff`, `/iterate-plan` |
| `web-search-researcher` | 웹 검색으로 최신 정보 조사 | 외부 API/라이브러리 정보 필요할 때 |
| `architecture-review` | 아키텍처 제안 검토 & 리스크 분석 | 설계 문서 리뷰 시 |
| `endpoint-analysis` | API 엔드포인트 동작/계약 분석 | `/validate-plan`, 엔드포인트 분석 시 |
| `pr-review-assistant` | PR 리스크 포커스 리뷰 | `/validate-plan`, PR 리뷰 시 |
| `consistency-check` | 데이터 스냅샷 비교 & 불일치 탐지 | 데이터 정합성 확인 시 |
| `document-summarizer` | 문서 요약 & 구조화 | 미팅 노트/설계 문서 정리 시 |
| `pr-description-generator` | PR 설명 자동 생성 | PR 생성 시 |

### 커맨드 vs 에이전트 차이

```
커맨드 (commands/)          에이전트 (agents/)
──────────────────          ──────────────────
사용자가 직접 호출           Claude가 자동 호출
/create-plan 으로 실행      Claude가 필요할 때 spawn
전체 워크플로우 정의         단일 전문 작업 수행
Opus 모델 사용              Sonnet 모델 사용 (빠르고 저렴)
```

### 실제 동작 예시

```
사용자: /create-plan 메일 검색 필터 추가

Claude (Opus):
  ├─ spawn codebase-locator (Sonnet)    ← 관련 파일 찾기
  ├─ spawn codebase-analyzer (Sonnet)   ← 기존 구현 분석
  ├─ spawn codebase-pattern-finder (Sonnet) ← 유사 패턴 탐색
  └─ 종합하여 구현 계획서 작성
```

---

## 자동 스킬 (NEW — mattpocock/skills 포팅)

스킬은 **프롬프트 내용으로 자동 호출**됩니다. 슬래시 커맨드로 부르지 않고, 사용자 발화가 스킬의 `description` 필드와 매칭되면 Claude가 알아서 트리거합니다.

### 커맨드 vs 에이전트 vs 스킬

```
커맨드 (commands/)        에이전트 (agents/)         스킬 (skills/)
──────────────────        ──────────────────         ──────────────────
사용자가 직접 호출         Claude가 커맨드 안에서      사용자 발화 매칭으로
/foo 로 실행              자동 spawn                자동 호출
전체 워크플로우 정의       전문 단일 작업              자동 발화 트리거
```

### 스킬 목록 (21개)

| 카테고리 | 스킬 | 자동 호출 트리거 |
|----------|------|------------------|
| **engineering** | `setup-matt-pocock-skills` | 새 프로젝트에서 처음 실행 — issue tracker, 도메인 문서 위치를 다른 스킬들에게 알려주는 부트스트랩 |
| | `grill-with-docs` | "도메인 모델에 비추어 이 계획 까봐줘" |
| | `to-prd` | "이 대화를 PRD로 만들어줘" |
| | `to-issues` | "이 계획을 이슈로 쪼개줘" |
| | `triage` | "들어온 이슈들 triage 해줘" |
| | `tdd` | "TDD로 가자", "red-green-refactor" |
| | `diagnose` | "이 버그 진단", "에러 발생", "성능 회귀" |
| | `improve-codebase-architecture` | "리팩토링 기회 찾기", "아키텍처 개선" |
| | `prototype` | "프로토타입 만들어보자", "UI 시안 몇 개" |
| | `zoom-out` | "큰 그림 보여줘", "맥락 좀 줘" |
| **productivity** | `grill-me` | "이 계획 까봐줘", "interview me" |
| | `caveman` | 간결 출력 모드 |
| | `write-a-skill` | "새 스킬 만들어줘" |
| **misc** | `git-guardrails-claude-code` | "위험한 git 명령 차단", "git 안전 훅 추가" |
| | `setup-pre-commit` | "pre-commit hook 설정", "Husky + lint-staged" |
| | `migrate-to-shoehorn` | "테스트의 `as`를 shoehorn으로 바꿔줘" |
| | `scaffold-exercises` | "exercise 구조 만들어줘" |
| **personal** | `edit-article` | "이 글 수정/개선해줘" |
| **in-progress** | `writing-fragments` | "ideate", "fragments", "글 raw material" |
| | `writing-shape` | "이 노트들을 글로 만들어줘" |
| | `writing-beats` | "내러티브로 조립해줘" |

### 기존 커맨드와의 중복 (참고)

같은 의도, 다른 형태 — 둘 다 유효하지만 사용 시점이 다릅니다:

| 기존 커맨드 | 새 스킬 | 차이 |
|-------------|---------|------|
| `/debug` | `diagnose` | `/debug`는 병렬 조사 워크플로우. `diagnose`는 reproduce → minimize → instrument 엄격 루프 (HITL 포함) |
| `/create-plan` (한방) | `grill-with-docs` + `to-prd` + `to-issues` (체인) | `/create-plan`은 한번에. Matt 방식은 점진적 |

### 새 프로젝트에서 시작하기

```
1. ./install.sh init /path/to/project        ← CLAUDE.md 생성 + .gitignore 패턴 등록
2. cd /path/to/project
3. (Claude 세션에서) "set up the engineering skills"  ← setup-matt-pocock-skills 자동 호출
4. AGENTS.md 또는 CLAUDE.md에 issue tracker, triage labels, 도메인 문서 경로 자동 기록됨
5. 이후 tdd, triage, diagnose 등 다른 엔지니어링 스킬이 컨텍스트를 알고 동작
```

---

## 상세 워크플로우 (기존 커맨드)

### 1단계: 브랜치 생성 & 코드 작업

```bash
git checkout -b feature/WM-XXXXX
# 코드 수정 작업...
```

### 2단계: 영향 분석

변경한 코드가 어떤 API 엔드포인트에 영향을 주는지 확인:

```
/affected-endpoints
```

출력 예시:
```
IndexDAO → ReadService → ReadController
  → GET /api/v2/mail/mailboxes/{id}/messages/{id}
NoticeMailMemberDAO → NoticeMailService → AdminNoticeMailController
  → POST /api/v2/mail/admin/mails/notice
```

### 3단계: 커밋

```
/commit-mailplug
```

출력 예시:
```
📌 감지된 티켓: WM-XXXXX

✨ 추천: feat(WM-XXXXX): 자동완성에서 Google 계정 제외 처리

📝 대안:
1. fix(WM-XXXXX): 자동완성 Google 계정 필터링 추가
2. refactor(WM-XXXXX): 자동완성 쿼리에 account_type 조건 추가
```

### 4단계: PR 생성

```
/pr-description
```

출력 예시:
```markdown
# PR: WM-XXXXX — 자동완성에서 Google 계정 제외

## Jira
- https://jira.example.com/browse/WM-XXXXX

## 요약
- ...

## 변경 사항
- ...

## 테스트 플랜
- [ ] ...
```

---

## Write→Verify 패턴

POST/PUT/PATCH/DELETE 실행 시 자동으로 GET 검증을 수행:

```
1. GET /representatives       → before.json 저장
2. POST /representatives {..} → 201 확인
3. GET /representatives       → after.json 저장
4. diff before.json after.json
   → "id:5 항목이 새로 추가됨 ✓"
```

### verify 자동 추론 규칙

| Write 메서드 | verify GET 경로 |
|-------------|----------------|
| `POST /xxx` | `GET /xxx` |
| `PUT /xxx` | `GET /xxx` |
| `PATCH /xxx/1` | `GET /xxx/1` |
| `DELETE /xxx/1` | `GET /xxx` (부모 경로) |

TEST_ENDPOINTS.md에서 verify 컬럼으로 직접 지정 가능:

```markdown
| | METHOD | Path | verify | 비고 |
|-|--------|------|--------|------|
| [ ] | POST | representatives | GET representatives | 생성 후 재조회 |
| [ ] | DELETE | representatives/1 | GET representatives | 삭제 후 재조회 |
```

---

## 환경 설정

### dotfiles 구조

리포는 어디에 클론해도 됩니다. `install.sh`가 자기 위치를 기준으로 심링크를 겁니다.

```
<repo>/                      ← git repo (bradykim7/Agcoco)
├── AGENTS.md                ← 글로벌 에이전트 메모리 (→ ~/.claude/CLAUDE.md, ~/.codex/AGENTS.md)
├── CLAUDE.md                ← AGENTS.md 심링크
├── DESIGN.md                ← HTML/프론트엔드 디자인 시스템
├── commands/                ← 커스텀 커맨드 → ~/.claude/commands/
├── agents/claude-code/      ← 서브에이전트 정의 → ~/.claude/agents/
├── skills/                  ← 스킬. <category>/<name>/SKILL.md 로 분류하고
│                              install.sh 가 최상위에 <name> 평탄화 심링크를 생성
├── hooks/                   ← PreToolUse / SessionStart 훅 → ~/.claude/hooks/
├── plugins/                 ← 플러그인 마켓플레이스 배포본
├── tools/                   ← 툴별 심링크 레지스트리 (claude.sh, codex.sh, ...)
├── scripts/                 ← 독립 셸 헬퍼 (jira-daily-setup.sh 등)
├── templates/               ← 프로젝트 템플릿
├── docs/                    ← 참고 문서
├── settings.json            ← 글로벌 설정 → ~/.claude/settings.json
├── install.sh               ← symlink 설치 + 프로젝트 init
└── WORKFLOW.md              ← 이 문서
```

커맨드/에이전트 인벤토리는 위 표들이 정본입니다. 여기서 중복 나열하지 않습니다.

### 새 환경 설정 (dev server 등)

```bash
git clone https://github.com/bradykim7/Agcoco.git ~/Agcoco
cd ~/Agcoco
./install.sh
```

### 커맨드 추가/수정 후 동기화

```bash
cd <repo>
git add -A && git commit -m "update commands" && git push

# dev server에서:
cd <repo> && git pull
```

심링크 방식이라 `git pull` 이후 재설치는 필요 없습니다. 단, **파일을 새로 추가하거나 스킬 디렉토리를 옮겼다면** `./install.sh`를 다시 돌려야 심링크가 갱신됩니다.
