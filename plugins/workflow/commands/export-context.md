---
description: 작업 컨텍스트를 마크다운으로 내보내기 — 다른 머신이나 다른 에이전트(Codex 등)가 이어받을 수 있게 보존
allowed-tools: Read, Glob, Grep, Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(date:*), Bash(ls:*), Write
argument-hint: [설명 또는 생략]
---

# Export Context (다른 머신·에이전트로 인계)

현재 세션의 작업 컨텍스트를 문서로 압축하여, 다른 머신이나 다른 에이전트가 이어서 작업할 수 있게 합니다.
같은 도구로 같은 머신에서 이어가는 거라면 이 커맨드 대신 `claude --resume` / `codex resume`을 씁니다.
humanlayer의 create_handoff 워크플로우에서 영감을 받았습니다.

---

## 프로세스

### Step 1: 메타데이터 수집

다음 정보를 자동으로 수집합니다:

```bash
git rev-parse --short HEAD        # 현재 커밋
git branch --show-current         # 현재 브랜치
git status --short                # 변경 상태
date +"%Y-%m-%d %H:%M:%S"        # 현재 시각
basename $(git rev-parse --show-toplevel 2>/dev/null || pwd)  # 프로젝트 이름
```

### Step 2: 핸드오프 문서 작성

`.handoffs/YYYY-MM-DD_HH-MM-SS_description.md` 에 작성합니다.

- `YYYY-MM-DD` — 오늘 날짜
- `HH-MM-SS` — 현재 시각 (24시간 형식)
- `description` — 간단한 kebab-case 설명

예시: `.handoffs/2026-04-08_14-30-00_add-search-filter.md`

### 핸드오프 문서 템플릿

```markdown
---
date: [ISO 형식 날짜+시간]
git_commit: [현재 커밋 해시]
branch: [현재 브랜치]
project: [프로젝트 이름]
status: handoff
---

# Handoff: {간결한 설명}

## 한눈에

{작업 흐름이 비선형이면 현재 위치를 15줄 이내 ASCII 그림으로 — Phase 진행, 바뀐 모듈 간 호출, before→after 중 맞는 것. 선형이면 이 절을 지운다}

## 작업 내용

{작업했던 Task 목록과 각각의 상태 (완료 / 진행중 / 계획됨)}
{구현 계획이 있었다면 어떤 Phase까지 진행했는지 명시}

## 최근 변경

{코드베이스에서 변경한 내용을 file:line 형식으로 기술}

## 핵심 발견사항 (Learnings)

{작업 중 알게 된 중요한 정보 — 패턴, 버그 원인, 다음 작업자가 알아야 할 것들}
{구체적 파일 경로 포함}

## 산출물 (Artifacts)

{생성하거나 수정한 파일 목록 — 계획서, 문서, 설정 파일 등}

## 다음 작업 (Next Steps)

{다음 세션에서 해야 할 작업 목록}
1. [ ] {action item 1}
2. [ ] {action item 2}
3. [ ] {action item 3}

## 기타 참고

{위 카테고리에 들어가지 않지만 전달이 필요한 정보}
```

---

## 작성 지침

- **많은 정보, 적은 코드** — 코드 스니펫보다 `file:line` 참조를 선호
- **정확하고 구체적으로** — 상위 목표와 하위 디테일 모두 포함
- **압축하되 누락 없이** — 컨텍스트를 요약하되 핵심 디테일은 보존
- **큰 코드 블록 금지** — 에러 디버깅 관련이 아니면 diff나 코드 블록 불필요 (`## 한눈에` 그림은 예외)

---

## 완료 시 출력

```
컨텍스트 내보내기 완료: .handoffs/YYYY-MM-DD_HH-MM-SS_description.md

.handoffs/는 gitignore 대상이라 다른 머신으로는 파일을 직접 옮겨야 합니다.
받는 쪽 새 세션에서 이렇게 요청하세요:
"이 문서 읽고, 적힌 상태를 현재 코드와 대조한 뒤 이어서 작업해줘: .handoffs/YYYY-MM-DD_HH-MM-SS_description.md"
```
