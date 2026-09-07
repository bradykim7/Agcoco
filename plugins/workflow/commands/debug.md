---
description: 구조적 디버깅 — 로그, git 상태, 파일 상태를 병렬 조사하여 원인 분석
allowed-tools: Read, Glob, Grep, Bash(git log:*), Bash(git diff:*), Bash(git status:*), Bash(git branch:*), Bash(cat:*), Bash(ls:*), Bash(tail:*), Bash(ps:*), Bash(find:*), Bash(docker:*), Agent
argument-hint: [문제 설명 또는 계획서/티켓 파일 경로]
---

# Debug (구조적 디버깅)

문제를 체계적으로 조사합니다. 로그, git 상태, 파일 상태를 병렬로 확인하고 근본 원인을 분석합니다.
humanlayer의 debug 워크플로우에서 영감을 받았으며, 어떤 프로젝트에서든 사용 가능합니다.

**핵심 원칙: 읽기 전용 조사만 수행. 파일 수정은 하지 않습니다.**

---

## 실행 시작

### 계획서/티켓 파일과 함께 실행할 때

```
[파일명]과 관련된 이슈를 디버깅합니다.

어떤 문제가 발생했나요?
- 무엇을 테스트/구현하려 했나요?
- 무엇이 잘못됐나요?
- 에러 메시지가 있나요?
```

### 파라미터 없이 실행할 때

```
현재 이슈를 디버깅합니다.

문제를 설명해 주세요:
- 어떤 작업 중이었나요?
- 구체적으로 무엇이 발생했나요?
- 마지막으로 정상 동작한 시점은?

로그, git 상태, 파일 상태 등을 조사하여 원인을 파악합니다.
```

---

## Step 1: 문제 이해

사용자가 문제를 설명하면:

1. **제공된 컨텍스트 읽기** (계획서, 티켓 파일)
   - 무엇을 구현/테스트 중이었는지 파악
   - 기대 동작 vs 실제 동작 식별

2. **빠른 상태 확인**
   - 현재 git 브랜치와 최근 커밋
   - 미커밋 변경사항
   - 문제 발생 시점

---

## Step 2: 병렬 조사

**3개의 에이전트를 동시 실행하여 조사 (아래 두 커스텀 에이전트와 범용 에이전트):**

### `codebase-analyzer` — 로그 확인
프로젝트 유형에 따라 로그 위치를 탐색:

```
탐색 경로 (프로젝트에 맞게 자동 판단):
- 애플리케이션 로그 (storage/logs/, logs/, var/log/)
- Docker 로그: docker logs <container> --tail 100
- 프레임워크별 로그 (Laravel, Spring, Django 등)
- 에러 로그, 액세스 로그
- stdout/stderr 출력

할 일:
1. 최근 로그에서 에러, 경고, 예외 검색
2. 스택 트레이스 확인
3. 반복되는 에러 패턴 식별
반환: 타임스탬프와 함께 핵심 에러/경고
```

### `codebase-locator` — Git & 파일 상태
```
할 일:
1. git status — 현재 상태
2. git log --oneline -10 — 최근 커밋
3. git diff — 미커밋 변경
4. 기대되는 파일 존재 여부 확인
5. 설정 파일 이상 여부 확인 (.env, config 등)
반환: Git 상태 및 파일 이슈
```

### 범용 에이전트 — 프로세스 & 서비스 상태
```
할 일:
1. 관련 프로세스 실행 확인 (ps aux | grep ...)
2. 포트 점유 확인 (lsof -i :PORT)
3. Docker 컨테이너 상태 (해당 시)
4. 의존 서비스 연결 상태 (DB, Redis 등)
반환: 서비스 상태 및 이상 소견
```

---

## Step 3: 디버그 리포트 제시

조사 결과를 기반으로 구조화된 리포트:

```markdown
## 디버그 리포트

### 문제 요약
[증거 기반 이슈 설명]

### 발견된 증거

**로그에서:**
- [타임스탬프 + 에러/경고]
- [패턴 또는 반복 이슈]

**Git/파일에서:**
- [관련 있을 수 있는 최근 변경]
- [파일 상태 이슈]

**프로세스/서비스에서:**
- [서비스 상태]
- [연결 문제]

### 추정 원인
[증거 기반 가장 유력한 설명]

### 해결 방안

1. **먼저 시도:**
   ```bash
   [구체적 명령 또는 조치]
   ```

2. **그래도 안 되면:**
   - [대안 1]
   - [대안 2]

### 조사 범위 밖
일부 이슈는 직접 확인이 필요할 수 있습니다:
- 브라우저 콘솔 에러 (F12)
- 외부 서비스 상태
- 네트워크/방화벽 이슈
```

---

## 프로젝트별 빠른 참고

### Java/Spring 프로젝트
```bash
tail -100 logs/application.log
grep -r "Exception\|ERROR" logs/
cat src/main/resources/application.yml
```

### PHP/Laravel 프로젝트
```bash
tail -100 storage/logs/laravel.log
grep -r "Exception\|Fatal" storage/logs/
cat .env | grep -v PASSWORD
```

### Node.js 프로젝트
```bash
cat package.json | grep -A5 scripts
ls node_modules/.package-lock.json 2>/dev/null
npm test 2>&1 | tail -50
```

### Docker 프로젝트
```bash
docker ps -a
docker logs <container> --tail 100
docker-compose config
```

### Python 프로젝트
```bash
cat requirements.txt
python -c "import sys; print(sys.version)"
grep -r "Traceback\|Error" logs/ 2>/dev/null
```

---

## 주의사항

- **읽기 전용** — 이 커맨드는 조사만 수행, 코드 수정 없음
- **문제 설명 필수** — 무엇이 잘못됐는지 알아야 조사 가능
- **파일 전체 읽기** — 컨텍스트 파일은 limit/offset 없이 전체 읽기
- **메인 컨텍스트 절약** — 깊은 조사는 서브에이전트에 위임
