---
description: 코드 변경으로 영향받는 HTTP 엔드포인트를 추적합니다
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git symbolic-ref:*), Grep, Glob, Read
argument-hint: [파일 경로 또는 티켓 ID]
---

# 영향받는 엔드포인트 추적

코드 변경 사항을 분석하여 영향받는 모든 HTTP 엔드포인트를 찾아냅니다.

## 분석 절차

### 1단계: 변경 파일 목록 수집

베이스는 `main`과 `master`를 모두 지원하며 다음 순서로 선택한다:

1. `git symbolic-ref --quiet refs/remotes/origin/HEAD`가 유효한 `refs/remotes/origin/main` 또는 `refs/remotes/origin/master`를 반환하면 우선 사용한다.
2. 없으면 `refs/heads/main`, `refs/heads/master`, `refs/remotes/origin/main`, `refs/remotes/origin/master` 순서로 `git rev-parse --verify "${candidate}^{commit}"`가 성공하는 첫 ref를 선택한다.
3. 선택한 ref를 `BASE_REF`, 마지막 경로 요소(`main` 또는 `master`)를 `BASE_BRANCH`로 사용하고 선택한 베이스를 출력한다. fetch는 필요하지 않다.
4. 후보가 모두 없으면 브랜치 비교를 실행하지 않고 베이스를 찾지 못했다고 안내한다.

**우선순위 순서로 변경 파일을 수집:**

1. `$ARGUMENTS`가 특정 파일 경로이면 해당 파일만 대상
2. 스테이징된 파일이 있으면: `git diff --staged --name-only`
3. 유효한 `BASE_REF`가 있고 현재 브랜치가 `BASE_BRANCH`와 다르면: `git diff "$BASE_REF"...HEAD --name-only` (비어 있으면 다음 순위로 이동)
4. 스테이징 안 된 변경이 있으면: `git diff --name-only`
5. 위 모두 없으면 사용자에게 안내

### 2단계: 변경 파일 분류

각 변경 파일을 역할별로 분류:

| 역할 | 경로 패턴 | 추적 방향 |
|------|-----------|-----------|
| **Controller** | `Controllers/` | → 직접 Routes.php에서 라우트 매칭 |
| **Service** | `Services/` | → 어떤 Controller가 이 Service를 사용하는지 검색 |
| **DAO/Model** | `Models/`, `DAO.php` | → 어떤 Service가 이 DAO를 사용하는지 검색 |
| **Repository** | `Repositories/` | → 어떤 Service가 이 Repository를 사용하는지 검색 |
| **DTO** | `DTO/` | → 어떤 Service/Controller가 이 DTO를 사용하는지 검색 |
| **Entity** | `Entities/` | → 어떤 DAO/Service가 이 Entity를 사용하는지 검색 |
| **Enum/Const** | `Enums/`, `Constants/` | → 사용처 전체 검색 |
| **Library** | `Libraries/` | → 사용처 전체 검색 |
| **Routes** | `Config/Routes.php` | → 해당 파일 내 모든 라우트가 영향 |
| **Config** | `Config/` (Routes 제외) | → 사용처 검색 |

### 3단계: 의존성 역추적 (Upstream Tracing)

변경 파일에서 **Controller까지** 역방향으로 추적:

```
변경된 DAO/Entity
  ↑ Grep: 클래스명으로 검색
Service (이 DAO를 사용하는)
  ↑ Grep: 클래스명으로 검색
Controller (이 Service를 사용하는)
  ↑ Routes.php에서 매칭
HTTP Endpoint
```

**추적 방법:**
1. 변경 파일의 **클래스명** 추출 (파일명에서 `.php` 제거)
2. `Grep`으로 해당 클래스명이 사용되는 파일 검색
   - `new ClassName` 패턴
   - `use Namespace\ClassName` 패턴
   - 함수 파라미터 타입힌트
3. 찾은 파일이 Controller가 아니면 → 다시 2번 반복 (최대 3단계)
4. Controller를 찾으면 → 4단계로

### 4단계: Controller → Route 매칭

찾은 Controller의 엔드포인트를 확인:

1. Controller 클래스명에서 **모듈** 판별
   - `App\Mail\Controllers\` → `app/Mail/Config/Routes.php`
   - `App\Contact\Controllers\` → `app/Contact/Config/Routes.php`
   - `App\Controllers\` → `app/Config/Routes.php`
   - 기타 모듈도 동일 패턴
2. 해당 모듈의 `Config/Routes.php`에서 **Controller명::메서드명** 검색
3. 매칭된 라우트의 HTTP Method + Path 추출

### 5단계: 결과 출력

## 출력 포맷

```markdown
# 영향받는 엔드포인트 분석

## 변경 파일 (N개)
| 파일 | 역할 |
|------|------|
| `app/Mail/Services/Message/ReadService.php` | Service |
| `app/Mail/Models/IndexDAO.php` | DAO |

## 의존성 추적
```
IndexDAO.php
  ↑ ReadService.php (new IndexDAO)
    ↑ ReadController.php (new ReadService)
      ↑ Routes: GET /mail/mailboxes/(:segment)/messages/(:num)
```

## 영향받는 엔드포인트 (N개)

| Method | Endpoint | Controller | 영향 경로 |
|--------|----------|------------|-----------|
| GET | `/api/v2/mail/mailboxes/{mailboxId}/messages/{messageId}` | ReadController::messageShow | IndexDAO → ReadService → ReadController |
| GET | `/mail/mailboxes/{mailboxId}/messages/{messageId}` | ReadController::messageShow | IndexDAO → ReadService → ReadController |

## 테스트 체크리스트
- [ ] `GET /api/v2/mail/mailboxes/{mailboxId}/messages/{messageId}` 정상 응답 확인
- [ ] `GET /mail/mailboxes/{mailboxId}/messages/{messageId}` 정상 응답 확인
```

## 규칙

- **읽기 전용** — 코드 수정, 커밋, 푸시 없음
- 추적 깊이는 최대 **3단계** (DAO → Service → Controller)
- 동일 엔드포인트가 여러 API 버전에 있으면 **모두 표시**
- `setAutoRoute(true)` 기반 자동 라우팅도 고려하되, 명시적 라우트 우선
- 변경 파일이 10개 이상이면 모듈별로 그룹핑하여 표시
- 비HTTP 영향 (Queue, Cron, CLI 등)도 발견되면 별도 섹션으로 표시
