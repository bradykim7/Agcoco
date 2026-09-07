# Hooks (한국어)

[`hooks/`](../hooks/) 의 bash 스크립트는 Claude Code 의 hook 시스템에 연결됩니다. 각 스크립트는 특정 라이프사이클 시점에 실행되며 다음을 수행할 수 있습니다:

- **차단** (`PreToolUse` 에서 `exit 2`),
- **컨텍스트 주입** (`SessionStart` 에서 일반 텍스트 stdout 출력 시),
- **차단 사유 전달** (`PreToolUse` 에서 `exit 2`이면 stderr 가 Claude 에 전달).

`install.sh` 가 `~/.claude/hooks/` 로 심링크합니다. 실제 hook 등록은 `~/.claude/settings.json` 에 존재.

> English: [hooks.en.md](./hooks.en.md)

## 목록

| 스크립트 | 이벤트 | 유형 | 용도 |
|----------|--------|------|------|
| [`block-dangerous-git.sh`](../hooks/block-dangerous-git.sh) | PreToolUse: Bash | **블로킹** | `git commit`, `git push`, `git filter-repo`, `git reset --hard` 등 거부 — 커밋·푸시는 승인 여부와 관계없이 사용자 직접 실행 |
| [`session-start-ticket-context.sh`](../hooks/session-start-ticket-context.sh) | SessionStart | 컨텍스트 주입 | 브랜치가 JIRA 티켓 패턴이면 해당 티켓 문서 자동 노출. 공용 티켓 문서 루트를 우선 사용하고(`$TICKET_DOCS_ROOT` 로 지정, 미지정 시 상위 디렉터리에서 `issue/` 탐색), 없으면 `.plans/`, `.handoffs/`, `.research/` 에서 티켓명이 들어간 파일을 찾는다 |

## Hook 이벤트 모델 (요약)

| 이벤트 | 발화 시점 | 이 저장소의 동작 |
|--------|-----------|------------------|
| `PreToolUse` | 도구 실행 직전 | `exit 2`로 도구 호출 차단, stderr로 사유 전달. JSON 결정 없이 `exit 0`이면 일반 권한 검사가 이어짐. |
| `SessionStart` | 세션 시작 | 일반 텍스트 stdout을 컨텍스트에 추가. 세션 시작은 차단하지 않음. |

다른 non-zero 종료코드는 그 자체로 차단을 의미하지 않는다. `Stop`은 `exit 2`로 종료를 막을 수 있지만, 이 저장소에는 등록되어 있지 않다. [공식 훅 문서](https://code.claude.com/docs/en/hooks#exit-code-output) 참고.

## 규칙

- Shebang: `#!/usr/bin/env bash`.
- `PreToolUse: Bash` hook 은 stdin 으로 JSON 입력 수신 — `jq -r '.tool_input.command'` 로 추출.
- 빠르게 (< ~100ms). 매 도구 호출마다 실행됨.
- Git 차단기는 jq/Python/shfmt 누락이나 검사 실패 시 `exit 2`로 차단한다. `exit 0`으로 통과시키지 않는다. 정보 제공용 세션 훅은 관련 컨텍스트가 없으면 `exit 0`으로 끝난다.
- 이벤트와 종료코드에 맞춰 출력한다. 세션 컨텍스트는 stdout, Git 명령 차단 사유는 stderr를 사용한다.

## 새 hook 추가

1. `your-hook.sh` 를 [`hooks/`](../hooks/) 에 작성 후 `chmod +x`.
2. `./install.sh` 재실행 → `~/.claude/hooks/` 로 심링크.
3. `~/.claude/settings.json` 해당 이벤트 아래 등록:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         { "matcher": "Bash", "hooks": [{ "type": "command", "command": "$HOME/.claude/hooks/your-hook.sh" }] }
       ]
     }
   }
   ```
4. 이벤트 발화로 테스트 → exit code, stdout, stderr 동작 확인.

## 이 hook 들이 존재하는 이유

- **`block-dangerous-git.sh`** — 글로벌 메모리 규칙: 커밋·푸시는 승인 여부와 관계없이 사용자 직접 실행. 세션 프롬프트가 잊어도 hook 이 강제.
- **`session-start-ticket-context.sh`** — 사용자가 매번 연결 자료 첨부할 필요 없이 티켓 컨텍스트 자동 복원.

Git 차단기는 Python 3, jq, [shfmt 3](https://github.com/mvdan/sh#shfmt)가 필요하다(macOS: `brew install shfmt`). 수동 복사 시 `git-command-guard.py`를 셸 훅과 같은 디렉터리에 둔다. 입력을 실행하지 않고 shfmt의 Bash 구문 트리를 읽어 주석·리다이렉션·따옴표로 감싼 heredoc 본문과 실제 명령을 구분하며, 중첩된 명령 치환도 검사한다. 실행 파일명·Git 작업·셸 `-c` 스크립트를 변수 등으로 구성해 정적으로 확인할 수 없으면 차단한다. 별칭·외부 스크립트까지 통제하려면 실행 단계의 별도 제한이 필요하다.
