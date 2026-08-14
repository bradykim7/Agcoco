---
description: 작업 마무리 — 커밋 메시지 추천 + PR 설명 생성 한번에 실행
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git add:*), Bash(git commit:*), Bash(cat:*), Bash(ls:*), Read, Glob, Grep
argument-hint: [티켓ID 또는 생략(자동감지)]
---

# 작업 마무리 (workfinish)

커밋 메시지 추천 + PR 설명 생성을 한번에 실행합니다.
`/commit-mailplug` + `/pr-description`를 순차 실행하는 메타 커맨드입니다.

## 실행 흐름

각 Step 완료 후 사용자 확인을 받고, 다음 Step으로 진행합니다.

### Step 1 — 티켓 ID 감지 & 상태 확인

1. `git branch --show-current` → 티켓 ID 추출
2. `$ARGUMENTS`가 있으면 티켓 ID로 사용
3. `git status`로 스테이징 상태 확인
4. `git diff --staged`로 스테이징된 변경 확인
5. 스테이징된 파일이 없으면:
   - `git diff`로 변경 파일 표시
   - 사용자에게 스테이징 안내 후 대기

출력:
```
📌 티켓: WM-XXXXX (브랜치: feature/WM-XXXXX)

스테이징 상태:
  M app/Mail/Models/IndexDAO.php
  M app/Mail/Services/Message/ReadService.php
  A app/Mail/DTO/NewDTO.php
```

### Step 2 — 커밋 메시지 추천

`git log --oneline -10`으로 최근 스타일 확인 후 추천:

```
✨ 추천 커밋 메시지:
feat(WM-XXXXX): 자동완성에서 Google 계정 제외 처리

📝 대안:
1. fix(WM-XXXXX): 자동완성 Google 계정 필터링 추가
2. refactor(WM-XXXXX): 자동완성 쿼리에 account_type 조건 추가

번호를 선택하거나 수정 요청해주세요.
커밋 없이 PR 설명만 생성하려면 "skip"이라고 해주세요.
```

**커밋 타입 결정 기준:**

| 타입 | 사용 시점 |
|------|-----------|
| `feat` | 새 기능 추가, 기존 기능 확장 |
| `fix` | 버그 및 오류 수정 |
| `hotfix` | 프로덕션 긴급 버그 수정 |
| `refactor` | 동작 변경 없는 코드 구조 개선 |
| `docs` | 문서만 변경 |
| `style` | 포맷팅, 세미콜론 등 (로직 변경 없음) |
| `perf` | 성능 향상 |
| `test` | 테스트 추가/수정 |
| `build` | 빌드/의존성 변경 |
| `ci` | CI/CD 변경 |
| `chore` | 유지보수, 잡무 |

**규칙:**
- 설명은 한국어
- 50자 이내 권장 (최대 72자)
- "~추가", "~수정", "~삭제", "~개선" 등 명사형 종결

### Step 3 — 커밋 실행 (사용자 승인 시에만)

사용자가 메시지를 선택/수정하면:
1. `git commit -m "type(TICKET): 메시지"` 실행
2. 커밋 결과 표시

**사용자가 "skip"하면 커밋 없이 Step 4로 이동.**

### Step 4 — PR 설명 생성

`git diff master...HEAD`와 `git log master...HEAD`를 분석하여 PR 설명 생성:

```markdown
# PR: {TICKET-ID} — {한줄 요약}

## Jira
- https://jira.example.com/browse/{TICKET-ID}

## 요약
- {bullet point 1}
- {bullet point 2}

## 변경 사항

### 1) {변경 그룹}
- **파일**: `{path}`
  - {변경 설명}

## 영향 범위 / 주의사항
- {impact}

## 테스트 플랜
- [ ] {test item 1}
- [ ] {test item 2}
```

### Step 5 — 최종 출력

```
=== WM-XXXXX workfinish 완료 ===

✓ 커밋: feat(WM-XXXXX): 자동완성에서 Google 계정 제외 처리
✓ PR 설명 생성 완료 (위 내용 복사하여 사용)

다음 단계:
  git push origin feature/WM-XXXXX
  → GitHub에서 PR 생성 시 위 설명 붙여넣기
```

## 규칙

- 커밋은 **사용자 승인 시에만** 실행 — 자동 커밋 절대 금지
- JWT/API 키를 채팅·PR에 절대 노출하지 않음
- PR 설명은 한국어 (팀 Format A)
- 변경 사항은 모듈/영역별 그룹핑
- 파일 경로는 backtick 사용
- 테스트 플랜은 checkbox 형식
