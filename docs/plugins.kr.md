# Plugins (한국어)

[`plugins/`](../plugins/) 의 Claude Code 플러그인 마켓플레이스 번들. 각 하위 디렉터리는 독립 플러그인 — `.claude-plugin/plugin.json` 매니페스트 + `commands/`, `agents/`, `skills/` 묶음.

마켓플레이스 UI 로 설치:

```bash
/plugin marketplace add bradykim7/Agcoco
/plugin install <플러그인명>@agcoco
```

최상위 [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) 이 디렉터리의 모든 플러그인을 광고합니다.

> English: [plugins.en.md](./plugins.en.md)

## 목록

| 플러그인 | 구성 | 용도 |
|----------|------|------|
| [`planning`](../plugins/planning/) | commands + agents | 계획 라이프사이클 — `create-plan`, `implement-plan`, `iterate-plan`, `validate-plan` + 서브에이전트 8개 동봉 |
| [`workflow`](../plugins/workflow/) | commands + agents | 핵심 메타 — `workfinish`, `debug`, `research`, `ask-codex`, `handoff`, `resume-handoff` + 서브에이전트 5개 동봉 |
| [`testing`](../plugins/testing/) | commands | 영향 엔드포인트 추적 — `affected-endpoints` |
| [`git-tools`](../plugins/git-tools/) | commands + skills | 커밋 & PR — `commit-mailplug`, `commit-suggest`, `pr-description` + `git-guardrails`, `setup-pre-commit` |
| [`engineering-skills`](../plugins/engineering-skills/) | skills | 엔지니어링 워크플로우 스킬 (11개) — `setup-matt-pocock-skills`, `diagnose`, `tdd`, `triage`, `to-prd`, `to-issues`, `zoom-out`, `improve-codebase-architecture`, `prototype`, `grill-with-docs`, `grill-me` |
| [`claude-usage`](../plugins/claude-usage/) | commands | Claude 사용량 분석 — `claude-usage-collect`, `claude-usage-analyze` |

## 플러그인 vs. 개인 설치

| 설치 방식 | 행선지 | 적합한 경우 |
|-----------|--------|------------|
| `./install.sh` (심링크) | `~/.claude/commands/`, `~/.claude/skills/`, `~/.claude/hooks/` | 본인 사용 — 모든 커맨드·스킬·hook 한번에 |
| `/plugin install <이름>@agcoco` | 플러그인이 관리하는 디렉터리 | 묶음 단위 — 특정 테마만 팀에 공유 |

두 방식은 공존 가능. 마켓플레이스는 저장소 전체 클론 없이도 부분 채택을 허용합니다.

## 플러그인 레이아웃

```
plugins/<이름>/
├── .claude-plugin/
│   └── plugin.json          ← name, description, version
├── commands/                ← (선택) 플러그인이 제공하는 슬래시 커맨드
│   └── *.md
├── agents/                  ← (선택) 플러그인이 제공하는 서브에이전트
│   └── *.md
└── skills/                  ← (선택) 플러그인이 제공하는 스킬
    └── <스킬명>/
        └── SKILL.md
```

## 새 플러그인 추가

1. `plugins/your-plugin/.claude-plugin/plugin.json` 생성:
   ```json
   {
     "name": "your-plugin",
     "description": "한 줄 요약",
     "version": "1.0.0"
   }
   ```
2. 매니페스트 옆에 `commands/` 또는 `skills/` 배치. 참조하는 커스텀 에이전트는 `agents/`에 동봉하고, 재배포하는 스킬의 원본 라이선스 고지도 포함한다.
3. [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) 에 플러그인 등록.
4. 사용자는 `/plugin install your-plugin@agcoco` 로 설치.

배포 전에 `bash scripts/check-plugin-sync.sh`로 커맨드·스킬·에이전트 사본과 에이전트 의존성 누락을 확인한다.

변경한 팩은 배포 전에 `.claude-plugin/plugin.json`의 `version`을 올린다. 저장소에 새 커밋이 있어도 버전이 같으면 기존 설치는 캐시된 사본을 유지한다. [공식 버전 결정 문서](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels) 참고.
