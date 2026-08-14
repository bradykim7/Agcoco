# Hooks (한국어)

[`hooks/`](../hooks/) 의 bash 스크립트는 Claude Code 의 hook 시스템에 연결됩니다. 각 스크립트는 특정 라이프사이클 시점에 실행되며 다음을 수행할 수 있습니다:

- **차단** (블로킹 hook 에서 non-zero exit),
- **컨텍스트 주입** (Stop / SessionStart hook 에서 stdout 출력 시),
- **운영자 경고** (stderr 는 사람에게 노출).

`install.sh` 가 `~/.claude/hooks/` 로 심링크합니다. 실제 hook 등록은 `~/.claude/settings.json` 에 존재.

> English: [hooks.en.md](./hooks.en.md)

## 목록

| 스크립트 | 이벤트 | 유형 | 용도 |
|----------|--------|------|------|
| [`block-dangerous-git.sh`](../hooks/block-dangerous-git.sh) | PreToolUse: Bash | **블로킹** | `git commit`, `git push`, `git filter-repo`, `git reset --hard` 등 거부 — 사람 승인 필요 |
| [`session-start-ticket-context.sh`](../hooks/session-start-ticket-context.sh) | SessionStart | 컨텍스트 주입 | 브랜치가 JIRA 티켓 패턴이면 `.plans/`, `.handoffs/`, `.research/`, `testjob/<ticket>/` 자료 자동 노출 |

## Hook 이벤트 모델 (요약)

| 이벤트 | 발화 시점 | stdout 행선지 | 블로킹? |
|--------|-----------|--------------|---------|
| `PreToolUse` | 도구 실행 직전 | (exit 이 0 이면 무시) | 가능 — non-zero exit 시 도구 호출 취소 |
| `Stop` | Claude 턴 종료 후 | 다음 컨텍스트에 추가 | 아니오 |
| `SessionStart` | 새 세션 시작 | 세션 컨텍스트에 추가 | 아니오 |

## 규칙

- Shebang: `#!/usr/bin/env bash`.
- `PreToolUse: Bash` hook 은 stdin 으로 JSON 입력 수신 — `jq -r '.tool_input.command'` 로 추출.
- 빠르게 (< ~100ms). 매 도구 호출마다 실행됨.
- 의존성 누락 대비 가드: `command -v jq >/dev/null || exit 0`.
- Claude 향 힌트는 **stdout**, 운영자 향 경고는 **stderr**.

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

- **`block-dangerous-git.sh`** — 글로벌 메모리 규칙: git commit / push 는 사람 승인 필요. 세션 프롬프트가 잊어도 hook 이 강제.
- **`session-start-ticket-context.sh`** — 사용자가 매번 연결 자료 첨부할 필요 없이 티켓 컨텍스트 자동 복원.
