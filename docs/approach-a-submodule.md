# Approach A: Git Submodule 방식

> 현재는 Approach B (글로벌 clone + `~/.claude`·`~/.codex` 로 symlink, 레포별로는 `install.sh init` 으로 CLAUDE.md 만 생성)를 사용 중.
> 향후 팀 공유가 필요할 때 이 방식으로 전환 검토.

## 구조

```
my-project/
├── .claude-setting/     ← git submodule (agcoco)
├── .claude/
│   ├── commands/ → .claude-setting/commands/  (symlink)
│   ├── agents/   → .claude-setting/agents/claude-code/  (symlink)
│   └── CLAUDE.md        ← 프로젝트별 커스텀 (템플릿에서 생성)
└── src/
```

## Pros

| 장점 | 설명 |
|------|------|
| Self-contained | 레포 clone만 하면 모든 설정이 따라옴 (다른 머신, 동료도 즉시 사용) |
| 버전 고정 | 레포마다 agcoco의 특정 커밋을 pin — 업데이트 시점을 레포별로 제어 |
| CI/협업 친화적 | 팀원이 `git submodule update --init`만 하면 동일 환경 |
| 이식성 | dev server, 새 머신에서도 별도 setup 불필요 |

## Cons

| 단점 | 설명 |
|------|------|
| Submodule 복잡성 | `git submodule update`, 깜빡하면 detached HEAD, PR 시 submodule 변경 노이즈 |
| 업데이트 번거로움 | 10개 레포에서 agcoco 올리려면 각각 submodule update + commit 필요 |
| 레포 오염 | 프로젝트 git history에 submodule 커밋이 섞임 |
| 개인 설정 공유 문제 | 팀 레포에 개인 AI 설정이 submodule로 들어가면 어색할 수 있음 |

## 전환 시 필요한 작업

1. `install.sh`에 `--submodule` 옵션 추가
2. `.gitmodules` 설정 자동 생성
3. per-repo `.claude/` 디렉토리 초기화 로직 변경
4. 기존 글로벌 symlink → 프로젝트 로컬 symlink 전환

## 적합한 상황

- 팀과 AI 설정을 공유해야 할 때
- 레포별로 다른 커맨드 버전을 써야 할 때
- dev server가 여러 대이고 환경 재현이 중요할 때
- CI에서 AI 설정이 필요할 때

## 참고

- humanlayer는 이 방식에 가까움 (monorepo 내 `.claude/` 직접 포함)
- 영감: [humanlayer/humanlayer](https://github.com/humanlayer/humanlayer) `.claude/commands/`
