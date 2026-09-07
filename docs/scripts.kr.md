# Scripts (한국어)

[`scripts/`](../scripts/) 의 독립 실행 셸·Python 헬퍼 — 인스톨러, 셋업 유틸, 일회성 자동화. `hooks/` (Claude Code 가 자동 호출) 와 `commands/` (`/<이름>` 으로 호출) 와 달리, 이 디렉터리의 스크립트는 사용자가 터미널에서 직접 실행합니다.

> English: [scripts.en.md](./scripts.en.md)

## 목록

| 스크립트 | 실행 방법 | 용도 |
|----------|-----------|------|
| [`jira-daily-setup.sh`](../scripts/jira-daily-setup.sh) | `./scripts/jira-daily-setup.sh` | `/jira-daily` 용 macOS LaunchAgent 대화형 설치. 자동 감지된 `HOME` · node 경로 · 작업 디렉터리로 헤드리스 스케줄링 (보통 하루 2회). |
| [`check-plugin-sync.sh`](../scripts/check-plugin-sync.sh) | `bash scripts/check-plugin-sync.sh` | 커맨드·스킬·에이전트 사본, 미배포 커맨드의 제외 등록, 커맨드가 참조하는 커스텀 에이전트 누락을 검사. 드리프트나 누락이 있으면 종료코드 1. |
| [`check-agent-regressions.py`](../scripts/check-agent-regressions.py) | `python3 -B scripts/check-agent-regressions.py` | 잘못된 응답과 동명 입력 파일 처리의 오프라인 CLI 검사. API 호출 없음. |
| [`check-shell-regressions.py`](../scripts/check-shell-regressions.py) | `python3 -B scripts/check-shell-regressions.py` | Git·홈 삭제 차단, 시간 파싱, 백업 보존, init, 플러그인 검사기 회귀검사. 실제 삭제나 launchd 등록 없음. |

저장소 루트에서 Python 3.10+, Bash, Git, jq, shfmt 3로 실행한다(macOS: `brew install shfmt`). Anthropic 응답을 대체하므로 API 키와 SDK 설치는 필요하지 않다. Jira 설치기는 시간을 10진수로 처리한다(`08:30` 허용, `08:99` 거부).

## 규칙

- 언어에 맞는 shebang: `#!/usr/bin/env bash` 또는 `#!/usr/bin/env python3`.
- 실행 권한: `chmod +x scripts/your-script.sh`.
- 헤더 주석에 prereqs 명시.
- 깨끗한 머신에서도 동작하도록 하드코드 경로 대신 대화형 프롬프트 선호.
- 플랫폼 종속이면 검증: `[ "$(uname)" = "Darwin" ] || { echo "macOS only"; exit 1; }`.

## 어디에 둘지

| 목적 | 위치 |
|------|------|
| Claude 내에서 `/<이름>` 으로 호출 | [`commands/`](../commands/) |
| Claude Code 라이프사이클 이벤트로 발화 | [`hooks/`](../hooks/) |
| 터미널에서 사용자가 수동 실행 | [`scripts/`](../scripts/) ← 여기 |
| `install.sh` 가 소비하는 도구 등록 | [`tools/`](../tools/) |

## 새 스크립트 추가

1. [`scripts/`](../scripts/) 에 파일 추가 후 `chmod +x scripts/your-script.sh`.
2. 헤더 주석에 prereqs + 사용법 작성.
3. 일회성 셋업이면 저장소 `README.md` 의 "Setup" 섹션에 언급.
4. 심링크 불필요 — 위 예시처럼 저장소에서 직접 실행.
