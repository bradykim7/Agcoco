---
description: Claude Code 팀 사용 리포트 생성 — 팀원 JSON 수합 → 8개 섹션 분석 (+ 선택: Confluence 발행)
allowed-tools: Bash(npx:*), Bash(ccusage:*), Bash(unzip:*), Bash(ls:*), Bash(mkdir:*), Bash(jq:*), Bash(date:*), Bash(test:*), Bash(find:*), Bash(cp:*), Bash(mv:*), Read, Write, Glob, Grep, Agent, mcp__jira-auth-proxy__confluence_get_page, mcp__jira-auth-proxy__confluence_create_page, mcp__jira-auth-proxy__confluence_update_page
argument-hint: <input 폴더 경로> [confluence-parent-id]
---

# Claude Usage Report (팀 사용 리포트)

팀원들이 `/claude-usage-collect`로 생성한 zip/JSON 파일들을 통합하여 8개 섹션의 종합 리포트를 생성합니다.
선택적으로 Confluence에 자동 발행합니다.

**Team-wide Claude Code usage report — aggregates individual usage packages into an 8-section analysis.**

---

## 사전 조건 / Prerequisites

1. `<input 폴더>` 안에 팀원 1명당 파일 1세트:
   - `claude-usage-<name>.zip` (collect 결과) 또는
   - 압축 해제된 `<name>/` 디렉토리 with `daily.json` / `session.json` / `monthly.json` / `meta.json`
2. `jq` 설치
3. 프로젝트 루트에 `.wiki-drafts/` 가 쓰기 가능
4. (선택) Confluence 발행: `mcp__jira-auth-proxy` 설정 + 인자 2번째에 parent page ID

---

## 실행 흐름 / Flow

### Step 1: 입력 검증

```bash
INPUT="${1:?input 폴더가 필요합니다}"
test -d "$INPUT" || { echo "[✗] 폴더 없음: $INPUT"; exit 1; }
```

- 폴더 안 `*.zip` 자동 해제 (`./team-data/<name>/` 로)
- 결과: N명의 사용자 디렉토리

```
team-data/
  kimminseok/
    daily.json session.json monthly.json meta.json
  parkjinhyeong/
    ...
```

### Step 2: 사용자 식별 & 한글화 매핑

사용자 이름 추출 순서:
1. 파일명 패턴 (`claude-usage-<name>-YYYYMMDD.zip`)
2. `meta.json` 의 `collector` 필드
3. 폴더명

**영문 → 한글 매핑**: 사용자에게 확인 요청

```
감지된 사용자:
  - kimminseok
  - parkjinhyeong
  - parkjunghyun
  - leeyunjea

한글명 매핑을 입력하세요 (엔터 = 영문 유지):
  kimminseok → 김민석
  parkjinhyeong → 박진형
  ...
```

매핑은 `.wiki-drafts/name-map.json` 에 저장 (다음 실행 시 재사용).

### Step 3: 데이터 집계

각 사용자별로 jq 파이프라인:

```jq
# Total tokens
[.daily[] | .totalTokens] | add

# Model breakdown
[.daily[] | .modelBreakdowns[]?] | group_by(.modelName) |
  map({
    model: .[0].modelName,
    input: (map(.inputTokens) | add),
    output: (map(.outputTokens) | add),
    cost: (map(.cost // 0) | add)
  })

# Daily peaks (top 5)
[.daily[] | {date, totalTokens}] | sort_by(.totalTokens) | reverse | .[0:5]

# Sessions
.session | length

# Longest session
[.session[] | (.endTime - .startTime)] | max

# Active days (전체 기간 중 토큰 > 0 인 날)
[.daily[] | select(.totalTokens > 0) | .date] | length
```

### Step 4: 지표 & 플래그 계산

(→ `/claude-usage-analyze` 와 동일 규칙 재사용)

사용자별:
- Activity: total, sessions, active_days, tokens/session, peak_day
- Routing: Opus%, Sonnet%, Haiku% + 플래그
- Hygiene: longest_session, 24h+/5d+ session 수 + 플래그
- Cost: API 환산, ROI, $/M tokens

팀 합계:
- Total team tokens, sessions, users
- Avg per-user ROI, median
- Opus/Sonnet/Haiku 팀 평균
- 비용: 월 구독료 합계 vs API 환산 합계 → 팀 ROI & 절감액

### Step 5: 병렬 서브에이전트로 분석 deepening (선택)

대용량 데이터인 경우 `document-summarizer` 에이전트 병렬 활용:
- 사용자별 메타 요약 (특이 패턴, anomaly)
- 팀 관점 인사이트 초안

### Step 6: 8개 섹션 드래프트 생성

`.wiki-drafts/` 하위에 다음 파일 생성:

| # | 파일 | 내용 |
|---|---|---|
| 01 | `01-executive-summary.md` | Bottom-line 수치, TL;DR 4명 요약 |
| 02 | `02-context-methodology.md` | 데이터 출처, 사용자 목록, 가격표, ROI 공식 |
| 03 | `03-teamwide-usage.md` | 팀 집계, 모델 전환 타이밍, 피크일 |
| 04 | `04-per-user-breakdown.md` | 사용자별 상세 (활동/모델/평가/권장) |
| 05 | `05-usage-quality.md` | 모델 라우팅 · 세션 위생 · 세션 깊이 |
| 06 | `06-cost-analysis.md` | 구독료 vs API 환산, 연간 추정, 대안 시나리오 |
| 07 | `07-plan-recommendations.md` | Max5×/Pro 플랜 권장 + 분기점 |
| 08 | `08-insights-next-actions.md` | 핵심 인사이트, 리스크, 다음 단계 체크리스트 |

각 섹션은 **한글/영어 bilingual** (CLAUDE.md 정책).

### Step 7: (선택) Confluence 발행

인자 2번에 parent page ID가 오면 자동 발행:

```
/claude-usage-report ./team-data 212482160
```

동작:
1. `mcp__jira-auth-proxy__confluence_get_page` 로 parent 존재 확인
2. 각 섹션에 대해:
   - 기존 페이지 있으면 `confluence_update_page`
   - 없으면 `confluence_create_page`
3. 마크다운 → Confluence storage 변환 시 주의:
   - **triple-backtick 금지** (매크로 leak → "Defaultnonetrue..." 렌더)
   - **중첩 bullet 2-space indent 위험** → 테이블로 재구성
   - **`enable_heading_anchors=false`**
   - 다중 줄 blockquote 병합 방지 → 분리
4. 페이지 ID 매핑 `.wiki-drafts/confluence-map.json` 저장

### Step 8: 결과 출력

```
[✓] 리포트 생성 완료

로컬 파일 (8개):
  .wiki-drafts/01-executive-summary.md
  .wiki-drafts/02-context-methodology.md
  ...
  .wiki-drafts/08-insights-next-actions.md

팀 요약:
  사용자: 4명 (김민석, 박진형, 박정현, 이윤재)
  총 토큰: 26.8M (14일)
  팀 ROI: 4.3×
  월 절감: $1,310 / ₩1,834,197

{Confluence 발행 시}
Confluence:
  Parent: https://.../pages/212482160
  01-08: v{N} 업데이트 완료

다음 단계:
  1. 드래프트 리뷰: .wiki-drafts/
  2. 재측정: 2-4주 후 다시 /claude-usage-report
```

---

## 분석 지침 / Analysis Guidelines

### 수치는 사실, 해석은 절제

- **말하지 않을 것**: "이 사용자는 낭비한다", "게으르다"
- **말할 것**: "Haiku 비중 0.6%는 라우팅 개선 여지 시그널"

### 필수 플래그

| 관찰 | 플래그 | 예시 표현 |
|---|---|---|
| Haiku < 2% | 🔴 | "경량 작업이 Opus로 처리되는 패턴" |
| Sonnet 급증 (last 7d) | 🟡 | "Opus rate limit 회피 가능성 — 본인 확인 필요" |
| 최장 세션 5d+ | 🔴 | "idle 세션 의심 — 세션 위생 점검" |
| 세션당 < 20k | 🟡 | "학습 중 단계 / 초보 패턴" |
| ROI < 1.0 | 🟡 | "Pro 다운그레이드 검토 대상 (2-4주 재측정 후)" |

### 재측정 원칙

리포트는 **14일 스냅샷**이므로 다음을 반드시 명시:
- 측정 기간, 측정일
- 한계: 모델 전환기/프로젝트 스파이크 가능성
- 재측정 시점 제안 (2-4주)

---

## 실패 처리 / Error Handling

| 상황 | 대응 |
|------|------|
| 일부 사용자 JSON 손상 | 해당 사용자 스킵 + 경고 (나머지 계속) |
| ccusage schema 변경 | jq 쿼리 실패 시 로그 출력 + 원본 일부 샘플 첨부 |
| Confluence 실패 | 로컬 드래프트는 유지 + 수동 발행 가이드 |
| name-map.json 충돌 | 기존 매핑 우선, 변경 확인 요청 |
| 14일 미만 데이터 | 경고 출력 + 리포트 계속 (신뢰도 주석) |

---

## 주요 주의사항 / Caveats

1. **개인정보**: ccusage 출력만 사용 — 대화 내용/프롬프트 절대 처리하지 않음
2. **수치 반올림**: 표시는 반올림하되 원본 값은 파일에 보관
3. **익명화 옵션**: 리포트 발행 전 이름 제거 원하면 `--anonymous` 사용 시 `A/B/C/D` 치환 (선택)
4. **비교 편향**: 사용자 수가 적을수록 아웃라이어 영향 큼 — 4명 미만은 경고

---

## 팀 운영 권장 주기

- **월 1회 재측정** 권장
- 신규 채용자 합류 시 baseline 수집
- Model 가격/출시 변동 시 재계산 (가격표는 커맨드 내 하드코딩 → 업데이트 필요)
