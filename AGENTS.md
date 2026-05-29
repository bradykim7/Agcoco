# Global Agent Memory

Canonical agent context shared by every CLI that follows the `AGENTS.md` convention. `install.sh` symlinks this file to:

- `~/.claude/CLAUDE.md` — Claude Code (loaded every session)
- `~/.codex/AGENTS.md` — Codex CLI (when installed)
- `CLAUDE.md` (sibling in this repo) → symlink to `AGENTS.md` so local Claude Code sessions in `agcoco/` also see it

Keep it tight — it's always in context.

## Repo structure

| Directory | Purpose |
|-----------|---------|
| `commands/` | Slash command markdown files → symlinked to `~/.claude/commands/` |
| `skills/` | Skill SKILL.md files → symlinked to `~/.claude/skills/` |
| `hooks/` | PreToolUse/SessionStart hook scripts → symlinked to `~/.claude/hooks/` |
| `plugins/` | Claude Code plugin marketplace structure |
| `agents/` | Agent definition files |
| `tools/` | Install script tool registry |
| `scripts/` | Standalone shell helpers (e.g., `jira-daily-setup.sh` for launchd) |

## Setup & plugin install

```bash
# 개인 설치 (심링크 방식)
./install.sh

# 플러그인 마켓플레이스로 설치
/plugin marketplace add mskim/Agcoco
/plugin install engineering-skills@agcoco
/plugin install workflow@agcoco
```

## Routing: command vs agent vs skill

| Type | Who invokes | When |
|------|-------------|------|
| **Command** (`/foo`) | User explicitly | Full workflow with multiple steps |
| **Agent** | Claude auto-spawns inside a command | Specialized single task (codebase search, doc analysis) |
| **Skill** | Auto-fires from user phrasing | When user's words match the skill's `description` field |

**Default precedence**: if user invokes a command, run it. Otherwise check if a skill should auto-fire. Use agents only for delegation inside commands.

## Intent routing — natural phrasing → action

User does not memorize slash names. When their words match an intent below, **act on it without being told**. Match phrases in either Korean or English.

**Confidence model:**
- **(A) Auto-fire** — read-only or unambiguous. Just run it.
- **(S) Suggest+confirm** — modifies files, high-blast-radius, or ambiguous. Ask first: "Looks like you want `X` — run it?"

Type legend: **(cmd)** slash command · **(skill)** auto-firing skill · **(agent)** internal subagent I spawn.

### Planning lifecycle
- `/create-plan` (cmd, S) — "plan this", "let's design X", "구현 계획 짜자", "설계해보자"
- `/iterate-plan` (cmd, S) — "update the plan", "계획 수정", "이 피드백 반영해서 계획 다시"
- `/implement-plan` (cmd, S) — "implement phase by phase", "Phase 1부터 시작", "계획대로 구현"
- `/validate-plan` (cmd, A) — "did we hit the goals", "계획 검증", "성공 기준 확인"
- `to-prd` (skill, A) — "turn this into a PRD", "PRD로 정리"
- `to-issues` (skill, A) — "break into issues", "이슈로 나눠줘"
- `grill-me` (skill, A) — "grill me on this", "interview me", "이 계획 그릴해줘"
- `grill-with-docs` (skill, A) — "stress-test against docs", "도메인 모델로 검증"
- `triage` (skill, A) — "triage these issues", "이슈 분류"

### Research, debug, understanding
- `/research` (cmd, A) — "research X", "코드베이스 조사", "어떻게 동작하는지 정리"
- `/debug` (cmd, A) — "broad investigation", "원인 모르겠어 다 봐줘", "병렬 조사"
- `diagnose` (skill, A) — "this is broken/throwing", "에러 난다", "diagnose this", "perf regression"
- `zoom-out` (skill, S — manual-only) — "zoom out", "큰 그림", "bigger picture" *(can't auto-fire — must suggest)*
- `codebase-locator` (agent, A) — "where does X live", "이 코드 어디 있어"
- `codebase-analyzer` (agent, A) — "how does X work", "이 로직 분석해줘"
- `codebase-pattern-finder` (agent, A) — "how is X done elsewhere", "비슷한 패턴 있어"

### TDD, prototype, refactor
- `tdd` (skill, A) — "let's TDD", "red-green-refactor", "테스트부터 짜자"
- `prototype` (skill, A) — "prototype this", "프로토타입", "try a few UI variations"
- `improve-codebase-architecture` (skill, A) — "find refactoring opportunities", "improve architecture", "리팩토링 거리 찾아줘"
- `architecture-review` (agent, A) — "review this architecture", "설계 검토", "design risks?"

### Test
- `/workcheck` (cmd, A) — "work check", "중간 점검", "지금까지 한 거 점검"
- `/affected-endpoints` (cmd, A) — "what's affected by this change", "이 변경 어디 영향"
- `/smoke-test` (cmd, A) — "smoke test", "엔드포인트 테스트"
- `/test-affected` (cmd, A) — "test what's affected", "영향받은 곳 테스트"
- `/branch-diff` (cmd, A) — "compare branches", "브랜치 비교"

### Commit & PR
- `/commit-suggest` (cmd, A) — "suggest commit message", "커밋 메시지 추천", "커밋 메시지 뭐로 할까"
- `/commit-mailplug` (cmd, A) — same intent in team Mailplug repos (TKT-XXX convention, mostly KR)
- `/pr-description` (cmd, A) — "PR description", "PR 설명 만들어줘"
- `/workfinish` (cmd, S) — "wrap up", "마무리하자", "ready to ship", "끝내자"
- `pr-review-assistant` (agent, A) — "review this PR", "PR 리뷰", "find risks in my changes"

### Session
- `/handoff` (cmd, A) — "handoff this session", "인수인계 문서 만들어", "save context"
- `/resume-handoff` (cmd, A) — "resume", "이어서 작업", "pick up where I left off"

### Claude usage
- `/claude-usage-collect` (cmd, A) — "collect my usage", "내 사용량 추출"
- `/claude-usage-analyze` (cmd, A) — "analyze my usage", "내 사용 분석", "ROI 리포트"
- `/claude-usage-report` (cmd, A) — "team usage report", "팀 사용 리포트"

### Jira
- `/jira-daily` (cmd, A) — "오늘 할당된 이슈", "today's jira", "내 티켓 봐줘", "jira 일일 분석"

### Setup
- `setup-matt-pocock-skills` (skill, S — manual-only) — "set up engineering skills", "이 프로젝트 셋업" *(can't auto-fire — must suggest)*
- `setup-pre-commit` (skill, A) — "pre-commit hooks", "Husky 셋업", "lint-staged"
- `git-guardrails-claude-code` (skill, A) — "block dangerous git", "위험한 git 막아줘"

### Personal & writing
- `obsidian-vault` (skill, A) — **requires explicit keyword "Obsidian" / "노트" / "옵시디언" / "note"**. Examples: "save this to Obsidian", "옵시디언에 저장해", "노트로 저장", "find a note", "옵시디언에서 찾아줘". Generic "save this" / "이거 저장해" alone does **not** fire this — ask which destination instead.
- `edit-article` (skill, A) — "edit this article", "글 다듬어줘"
- `writing-fragments` (skill, A) — "ideate", "fragments", "raw material"
- `writing-shape` (skill, A) — "shape these notes into article"
- `writing-beats` (skill, A) — "narrative beats", "as a journey/story"

### Productivity & misc
- `caveman` (skill, A) — "be brief", "caveman mode", "토큰 아껴"
- `write-a-skill` (skill, A) — "create a new skill", "새 스킬 만들어줘"
- `scaffold-exercises` (skill, A) — "scaffold exercises"
- `migrate-to-shoehorn` (skill, A) — "migrate `as` to shoehorn"

### Doc analysis
- `web-search-researcher` (agent, A) — "웹 검색해줘", "최신 문서 찾아봐", "search the web for X", "stack overflow에서 찾아봐", "find docs online"
- `document-summarizer` (agent, A) — "summarize this doc", "이 문서 요약", "extract action items"
- `docs-locator` (agent, A) — "find past plans/handoffs", "이전 핸드오프 찾아줘"
- `docs-analyzer` (agent, A) — "extract insights from this past doc"
- `consistency-check` (agent, A) — "compare these two datasets", "데이터 비교"
- `endpoint-analysis` (agent, A) — "analyze this endpoint", "API 분석"

## Overlap rules (use this, not that)

- **`/debug` vs `diagnose`** — `/debug` for broad parallel investigation when the bug is unknown. `diagnose` (skill) for hard-to-reproduce bugs needing reproduce → minimize → instrument loop. If user names the symptom but not the cause, lean `/debug`. If they say "diagnose this", lean `diagnose`.
- **`/commit-suggest` vs `/commit-mailplug`** — `/commit-mailplug` if repo follows team ticket convention (TKT-XXX) or commits are mostly Korean. Otherwise `/commit-suggest`. When unclear, ask once.
- **`/handoff` (command) only** — there is no `handoff` skill (deleted as duplicate). Always use `/handoff`, paired with `/resume-handoff`.
- **`/create-plan` vs `grill-with-docs` + `to-prd` + `to-issues`** — `/create-plan` is one-shot and faster. The skill chain is incremental and produces persistent artifacts (PRDs + issues). Ad-hoc planning → command; formal scoping → skill chain.
- **`/workfinish` vs piecewise `/commit-suggest` + `/pr-description`** — `/workfinish` runs both. Use it on "wrap up" / "마무리". Use the individual commands when user asks for just one.
- **`obsidian-vault` skill vs proactive Obsidian saving rule below** — the skill only fires when user explicitly says "Obsidian" / "옵시디언" / "노트" / "note". Generic "save this" / "이거 저장해" is ambiguous (handoff? file? Obsidian?) → ask which destination before acting. The proactive rule below is for moments where I notice something worth capturing without being asked.

## Per-repo behavior

- **In `agcoco/`**: read `WORKFLOW.md` upfront before suggesting workflow changes — it's the source of truth for commands/agents/skills inventory.
- **In a fresh project (no `AGENTS.md`/`CLAUDE.md` with `## Agent skills` block)**: suggest running `setup-matt-pocock-skills` skill first to bootstrap context for `tdd`, `triage`, `to-prd`, `to-issues`, `diagnose`, etc.

## HTML / frontend design system

For **any HTML/CSS/frontend UI work** (building a page, component, landing page, styling, "make this look good"), read `/Users/mskim/personal/Agcoco/DESIGN.md` first and follow its design system — color tokens, typography ladder, spacing, components, and do's/don'ts. It's the default house style.

- Use the documented `{token.refs}` (e.g. `{colors.primary}`, `{typography.hero-display}`) — never inline ad-hoc hex/sizes that the spec already defines.
- This is the default, not a straitjacket: if the user asks for a different look or the project clearly has its own system, follow that instead and say so.
- If `DESIGN.md` isn't present at that path (different machine), skip silently — don't error.

## Proactive Obsidian saving

Vault: `$OBSIDIAN_VAULT` (default `$HOME/Obsidian`) — set the env var in your shell config to override.

**When to proactively offer to write a note** (don't wait to be asked):
- Learned a new tool, CLI feature, or platform capability (e.g., Claude Code plugin system)
- Made or discovered an architecture/design decision
- Found a non-obvious pattern, gotcha, or workaround
- Solved a tricky problem with a generalizable lesson

**Which folder:**
- General tech knowledge → `30-Development/`
- Company/team-specific → `20-Company/`
- Unsure → `00-Inbox/`

**Format:** kebab-case filename, frontmatter with `type`, `date`, `tags`. See `obsidian-vault` skill for full conventions.

**Don't write** for: trivial tasks, one-off fixes, things already in the codebase.

## Anti-patterns to avoid

- Don't spawn agents for trivial work (single file read, simple grep) — call the tool directly.
- Don't invoke a skill the user didn't trigger. Skills fire on user phrasing, not your interpretation.
- Don't paraphrase command flows; if `/workcheck` exists for a flow, suggest the command, don't reimplement it manually.

## Behavioral guidelines

**Tradeoff:** These bias toward caution over speed. Use judgment for trivial tasks.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

## Coding principles (laws to lean on)

Curated from [Laws of Software Engineering](https://lawsofsoftwareengineering.com/). Skips the ~20 organizational laws (Brooks, Conway, Peter Principle, etc.) and the ~10 already covered above (YAGNI, KISS, premature optimization, premature DRY, Boy Scout Rule, Least Astonishment). Apply when the situation calls for it — **don't recite, don't over-apply**.

- **Hyrum's Law** — any observable behavior of a sufficiently-used API becomes a contract. When changing return shapes, error messages, ordering, or timing, assume callers depend on it. Grep for callers before "fixing" odd-looking behavior.
- **Postel's Law** — strict in output, liberal in input. **Apply at system boundaries only** (user input, external APIs, parsing). Inside trusted internal code, validate strictly — don't paper over bugs.
- **Law of Leaky Abstractions** — non-trivial abstractions leak. Don't wrap something just to hide it; the caller will eventually need the underlying detail. Wrap only to *remove* complexity, not to disguise it.
- **Law of Demeter** — don't reach through chains (`a.b.c.d.method()`). Tell, don't ask. If you're navigating internals, the boundary is in the wrong place.
- **Pesticide Paradox** — the same tests stop finding bugs over time. When fixing a bug, add a *new kind* of test (boundary, concurrency, malformed input) — not just a regression for that one case.
- **Kernighan's Law** — debugging is twice as hard as writing code. If you write at the limit of your cleverness, you have nothing left for debugging. Default to boring.
- **Tesler's Conservation of Complexity** — complexity moves but doesn't disappear. When "simplifying" code, ask *where the complexity went*. Usually it got pushed to the caller, the schema, or the docs. Move it deliberately, not accidentally.
- **Gall's Law** — complex working systems always evolve from simpler working systems. Don't build the final architecture upfront. Get a thin slice end-to-end first.
- **Pareto (80/20)** — 20% of causes drive 80% of problems. When stuck, locate the 20% before working on the rest.

**Override note:** Boy Scout Rule ("leave code better than you found it") is *deliberately overridden* here — the *Surgical Changes* rule above wins. Don't auto-improve adjacent code.
