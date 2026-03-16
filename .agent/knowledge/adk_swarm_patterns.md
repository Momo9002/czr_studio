# ADK Swarm Patterns — Knowledge Base

> What we learned building the Aura swarm. Reference for all future swarm work.

---

## Core Primitives

| Primitive | What it does | When to use |
|---|---|---|
| `LlmAgent` | Single LLM call with a prompt + optional tools | Any atomic task: write, score, search, summarize |
| `SequentialAgent` | Runs sub_agents one after another, shared state | Linear pipelines where each step depends on the previous |
| `ParallelAgent` | Runs sub_agents simultaneously | Independent tasks — scoring N items, generating N variants |
| `LoopAgent` | Repeats sub_agents until `escalate_to_parent=True` or max iterations | Quality loops: validate → revise → validate until good enough |
| `BaseAgent` | Custom Python class with `_run_async_impl` | Runtime decisions: dynamic spawning, conditional branching, external API calls |

---

## How Agents Communicate

**They don't call each other directly. They share session state.**

```python
# Agent A writes
output_key="raw_prospects"   # → ctx.session.state["raw_prospects"]

# Agent B reads
instruction="Read {raw_prospects} and score each one."
```

- Every `LlmAgent` has one `output_key` — it writes its output there
- Every subsequent agent reads from state via `{key_name}` in its instruction
- `cost_log` and `quality_log` are appended to state by every agent call
- State is saved to disk via `save_run_log()` at end of run

---

## The 4 Real Patterns We Use

### Pattern 1 — Sequential Pipeline
```
A → B → C → D
```
Each agent reads the previous agent's output_key.
Used by: all 4 sub-swarms (LeadGen, Proposal, SiteBuild, Retention)

### Pattern 2 — Quality Loop (LoopAgent)
```
Writer → [Validator → Reviser] loop until score ≥ threshold or max iterations
```
- ValidatorAgent sets `escalate_to_parent = true` in state when satisfied
- LoopAgent sees this and exits
- `max_iterations` is the cost control knob
- Used by: `DmQualityLoop`, `ProposalQualityLoop`

### Pattern 3 — Dynamic Auto-Spawning (BaseAgent)
```python
class DynamicAgent(BaseAgent):
    async def _run_async_impl(self, ctx):
        async for event in discovery_agent.run_async(ctx): yield event
        items = parse(ctx.session.state["discovered_items"])   # runtime data
        parallel = ParallelAgent(sub_agents=[make_agent(i) for i in items])
        async for event in parallel.run_async(ctx): yield event
```
- Sub-agents are created INSIDE `_run_async_impl`, not at build time
- Width of the tree (N parallel agents) is determined by runtime data
- Google calls this "Dynamic Agent Selection" — requires `BaseAgent`
- Used by: `DynamicProfilerAgent` in `lead_gen`

### Pattern 4 — Outer Feedback Loop (Meta Swarm)
```
Aura runs → writes logs → Meta reads logs → Meta rewrites Aura → repeat
```
- Two separate swarms connected by the filesystem (`output/logs/*.json`)
- Meta uses `adk eval` with golden examples to validate before deploying
- Trigger: weekly cron OR when rolling avg quality < 7.5

---

## Cost Control Knobs

| Knob | Where | Typical value |
|---|---|---|
| `max_output_tokens` | `GenerateContentConfig` per agent | 250–600 (flash), 2000–4000 (pro code gen) |
| `max_iterations` | `LoopAgent` | 3 (quality loops) |
| Model selection | per agent | Flash for everything, Pro only for SiteDevAgent |
| Cost cap | In orchestrator before spawning | `if total_cost > $0.50: abort` |

**Typical costs:**
- Full lead gen run (5 prospects, quality loop): ~$0.013
- Full site build (with Pro model): ~$0.15–0.30
- Meta audit + fix run: ~$0.05

---

## Key Rules for Every New Agent

1. **Always set `output_key`** — agents that don't write to state are dead ends
2. **Always set `max_output_tokens`** — prevents runaway API bills
3. **Log cost + quality** — `append_cost_log()` / `write_quality_log()` from `swarm/tools/logging_tools.py`
4. **Use `escalate_to_parent = true`** in state to exit a LoopAgent early
5. **Name agents clearly** — name shows in ADK traces and cost logs
6. **Instructions use `{key_name}` syntax** to read from state — no need to pass data explicitly

---

## Native ADK Eval (for Meta)

```bash
adk eval swarm/orchestrator.py swarm/evals/dm_evalset.json \
  --config swarm/evals/eval_config.json
```

Built-in metrics:
- `response_match_score` — ROUGE-1 lexical similarity vs reference
- `final_response_match_v2` — LLM-judged semantic equivalence
- `rubric_based_final_response_quality_v1` — custom rubric scoring

Golden examples live in `swarm/evals/`. Add one per agent type that produces user-facing output.

---

## When to Use Which Agent Type

```
Single LLM call with clear input/output      → LlmAgent
Run multiple things in order                 → SequentialAgent
Run multiple things at the same time         → ParallelAgent
Run until quality threshold is met           → LoopAgent
Decide at runtime what agents to spawn       → BaseAgent (custom)
Orchestrate top-level routing by phase/state → BaseAgent (custom)
```

---

## Anti-Patterns to Avoid

- ❌ **PreloadRequired** — don't use `ParallelAgent` at build time when data comes from a previous agent. Use `BaseAgent` to spawn dynamically instead.
- ❌ **God Agent** — one agent doing everything. Keep each agent focused on one job.
- ❌ **No output_key** — agents that only print or return None break the pipeline.
- ❌ **Pro model everywhere** — Flash is 10× cheaper and sufficient for all non-code tasks.
- ❌ **Unbounded loops** — always set `max_iterations` on `LoopAgent`.
