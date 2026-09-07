# Sub-agents

Specialized agents that Claude Code spawns via the `Agent` tool. Each `.md` under [`agents/claude-code/`](../agents/claude-code/) is a self-contained agent definition — name, description, model, and system prompt.

In this repo, Claude delegates to these agents inside command workflows, using each agent's `description` to match the task. See the routing rules in [AGENTS.md](../AGENTS.md).

> 한국어: [agents.kr.md](./agents.kr.md)

## Inventory

### Codebase exploration
| Agent | Model | Use when |
|-------|-------|----------|
| [`codebase-locator`](../agents/claude-code/codebase-locator.md) | sonnet | "Where does X live?" — Super Grep/Glob for finding files |
| [`codebase-analyzer`](../agents/claude-code/codebase-analyzer.md) | sonnet | "How does X work?" — trace data flow, explain logic |
| [`codebase-pattern-finder`](../agents/claude-code/codebase-pattern-finder.md) | sonnet | "How is X done elsewhere?" — find similar implementations with concrete code |

### Review & analysis
| Agent | Model | Use when |
|-------|-------|----------|
| [`architecture-review`](../agents/claude-code/architecture-review.md) | opus | Review architecture proposals for scalability, resilience, security boundaries, failure isolation |
| [`pr-review-assistant`](../agents/claude-code/pr-review-assistant.md) | sonnet | Risk-focused PR review — backward compat, security, perf, null handling, observability |
| [`endpoint-analysis`](../agents/claude-code/endpoint-analysis.md) | sonnet | Analyze an API endpoint — behavior, contracts, validation, test cases |
| [`consistency-check`](../agents/claude-code/consistency-check.md) | haiku | Compare two datasets/snapshots; classify mismatches by severity |

### Docs & research
| Agent | Model | Use when |
|-------|-------|----------|
| [`docs-locator`](../agents/claude-code/docs-locator.md) | sonnet | Find past handoffs / plans / research docs |
| [`docs-analyzer`](../agents/claude-code/docs-analyzer.md) | sonnet | Extract high-value insights from a past handoff/plan/research doc |
| [`document-summarizer`](../agents/claude-code/document-summarizer.md) | haiku | Normalize a doc into decisions / risks / next actions / open questions |
| [`web-search-researcher`](../agents/claude-code/web-search-researcher.md) | sonnet | Web search for modern docs, best practices, comparisons |

### PR generation
| Agent | Model | Use when |
|-------|-------|----------|
| [`pr-description-generator`](../agents/claude-code/pr-description-generator.md) | haiku | Compose PR description from git changes + commits + linked tickets |

## Model selection rationale

- **`opus`** — multi-step reasoning, risk analysis, cross-cutting reviews.
- **`sonnet`** — most exploration, analysis, and writing work.
- **`haiku`** — bounded, structural tasks (summarize, compare, format). Fast and cheap.

If you build a new agent, pick the cheapest tier that gives correct output on your evals.

## Conventions

- Filename = `name:` field in frontmatter (kebab-case).
- The `description:` field describes when Claude should invoke the agent — write it as routing copy ("Use this agent when…"), not generic prose.
- Include 2–3 example inputs in the description so Claude pattern-matches reliably.

## Adding a new agent

1. Create `your-agent.md` in [`agents/claude-code/`](../agents/claude-code/) with frontmatter:
   ```yaml
   ---
   name: your-agent
   description: Use this agent when … Examples: "...", "...", "..."
   model: sonnet
   tools: Read, Grep, Glob, Bash
   ---
   ```
2. Write the system prompt body. Keep it focused — one job per agent.
3. Re-run `./install.sh` to symlink to `~/.claude/agents/`.

## Python API agents

Five separate CLI implementations live in [`agents/python/`](../agents/python/). Each requires Python 3.10+, the `anthropic` SDK, and `ANTHROPIC_API_KEY`; even `--demo` calls the API. Invalid JSON/schema responses fail before result storage. See each agent’s README and the [offline checks](scripts.en.md).
