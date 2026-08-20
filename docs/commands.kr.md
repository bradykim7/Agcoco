# Slash Commands (한국어)

Claude Code 슬래시 커맨드. [`commands/`](../commands/) 의 각 `.md` 파일은 `/<파일명>` 으로 호출됩니다.

`install.sh` 가 `commands/` 디렉터리를 `~/.claude/commands/` 로 심링크합니다. 자연어 문구로 자동 발화되는 라우팅 규칙은 [`AGENTS.md`](../AGENTS.md#intent-routing--natural-phrasing--action) 에 있습니다.

> English: [commands.en.md](./commands.en.md)

## 목록

### 계획 라이프사이클
| 커맨드 | 용도 |
|--------|------|
| [`/create-plan`](../commands/create-plan.md) | 구조적 구현 계획 수립 — 조사 → 설계 → 단계별 계획 |
| [`/iterate-plan`](../commands/iterate-plan.md) | 기존 계획서 수정 — 피드백 반영 (리서치 기반) |
| [`/implement-plan`](../commands/implement-plan.md) | 계획서 단계별 구현 — Phase별 자동 검증 게이트 |
| [`/validate-plan`](../commands/validate-plan.md) | 계획서 구현 결과 검증 — 성공 기준 확인 |

### 리서치 · 디버그 · 이해
| 커맨드 | 용도 |
|--------|------|
| [`/research`](../commands/research.md) | 병렬 에이전트로 코드베이스 조사 → 리서치 문서 생성 |
| [`/debug`](../commands/debug.md) | 원인 모를 때 로그/git/파일 병렬 조사 |
| [`/ask-codex`](../commands/ask-codex.md) | 블라인드 교차 검증 — Claude와 Codex가 서로 답을 모르는 상태로 각자 답한 뒤 교차 반론, 이 세션의 Claude는 심판 역할 |

### 테스트
| 커맨드 | 용도 |
|--------|------|
| [`/affected-endpoints`](../commands/affected-endpoints.md) | 코드 변경으로 영향받는 HTTP 엔드포인트 추적 |

### 커밋 & PR
| 커맨드 | 용도 |
|--------|------|
| [`/commit-suggest`](../commands/commit-suggest.md) | 스테이징된 파일 + 히스토리로 커밋 메시지 추천 |
| [`/commit-mailplug`](../commands/commit-mailplug.md) | 팀 컨벤션 커밋 메시지 (티켓 ID 자동 감지) |
| [`/pr-description`](../commands/pr-description.md) | git diff 기반 PR 설명 자동 생성 |
| [`/workfinish`](../commands/workfinish.md) | 커밋 + PR 설명 한번에 — "마무리하자" |

### 세션
| 커맨드 | 용도 |
|--------|------|
| [`/handoff`](../commands/handoff.md) | 다음 세션이 이어 받을 수 있도록 컨텍스트 보존 |
| [`/resume-handoff`](../commands/resume-handoff.md) | 핸드오프 문서에서 작업 재개 |

### Claude 사용량
| 커맨드 | 용도 |
|--------|------|
| [`/claude-usage-collect`](../commands/claude-usage-collect.md) | 본인 ccusage 데이터 추출 → 공유 패키지 생성 |
| [`/claude-usage-analyze`](../commands/claude-usage-analyze.md) | 개인 ROI / 모델 라우팅 / 세션 위생 리포트 |
| [`/claude-usage-report`](../commands/claude-usage-report.md) | 팀원 JSON 수합 → 8개 섹션 통합 리포트 (Confluence 발행 선택) |

### Jira
| 커맨드 | 용도 |
|--------|------|
| [`/jira-daily`](../commands/jira-daily.md) | 오늘 할당된 Jira 이슈 분석 — macOS 알림 + 계획서 생성 |

## 규칙

- 파일명 = 커맨드명 (슬래시 제외).
- frontmatter `description:` 이 위 표에 노출됩니다.
- 한국어/영어 모두 지원 — 라우팅이 두 언어 문구를 매칭합니다.

## 새 커맨드 추가

1. `your-command.md` 를 [`commands/`](../commands/) 디렉터리에 frontmatter 와 함께 작성:
   ```yaml
   ---
   description: /help 및 본 문서에 표시될 한 줄 요약
   ---
   ```
2. 저장소 루트에서 `./install.sh` 재실행 → `~/.claude/commands/` 로 심링크.
3. 자연어 자동 발화가 필요하면 [`AGENTS.md`](../AGENTS.md#intent-routing--natural-phrasing--action) 에 라우팅 한 줄 추가.
