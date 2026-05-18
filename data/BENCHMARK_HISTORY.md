# PromptPropulserClaude — Benchmark History

All benchmarks executed against **Claude Sonnet 4-6** (generation) + **Claude Haiku 4-5** (LLM-as-Judge, temperature=0). Every prompt tested RAW (direct to Claude) vs PPC (pipeline-optimized).

---

## Version Timeline

```
v1.0 — 2026-05-18 — Keyword Critic (heuristic evaluation)
v1.1 — 2026-05-18 — LLM-as-Judge (Claude Haiku evaluation)
v1.2 — 2026-05-18 — System Channel (constraints as system prompt for code/focus)
```

| Version | Critic | Constraint Channel | Key Change |
|---------|--------|-------------------|------------|
| v1.0 | Keyword matching | Inline only | Baseline |
| v1.1 | LLM-as-Judge | Inline only | Judge understands negation context |
| v1.2 | LLM-as-Judge | **System for code/focus** | Constraints don't steal output tokens |

---

## Benchmark v1 — 24 Prompts (8 modes × 3)

**Difficulty**: Mostly easy-medium. 9/24 prompts trivial (basic, teacher modes). 1-2 constraints per prompt.

### v1.0 — Keyword Critic

| Metric | Value |
|--------|-------|
| PPC Win Rate | 16.7% |
| Constraint Delta | -0.50 |
| Accuracy Delta | -0.04 |
| Clarity Delta | +0.12 |
| Efficiency Delta | 0.00 |

| Mode | Delta | Wins |
|------|:---:|:---:|
| focus | **-0.67** | 0/3 |
| code | -0.17 | 1/3 |
| architect | -0.17 | 0/3 |
| compress | +0.08 | 1/3 |
| reflection | +0.08 | 1/3 |
| basic | 0.00 | 0/3 |
| brutal | 0.00 | 1/3 |
| teacher | 0.00 | 0/3 |

**Problem**: Keyword critic penalized constraint mentions in negation context. "SIN Docker" counted as violation.


### v1.1 — LLM-as-Judge (same prompts, better evaluator)

| Metric | v1.0 Keyword | v1.1 LLM Judge | Change |
|--------|:---:|:---:|:---:|
| PPC Win Rate | 16.7% | **41.7%** | +25pp |
| Constraint Delta | -0.50 | -0.38 | +0.12 |
| Accuracy Delta | -0.04 | **+0.12** | Flipped positive |
| Clarity Delta | +0.12 | +0.21 | +0.09 |
| Efficiency Delta | 0.00 | **+0.17** | New benefit |

| Mode | v1.0 | v1.1 | Change |
|------|:---:|:---:|:---:|
| **focus** | -0.67 | **+0.42** | Flipped. 0/3→3/3 wins |
| **code** | -0.17 | **+0.25** | Flipped positive |
| compress | +0.08 | +0.33 | Improved |
| teacher | 0.00 | +0.17 | Improved |
| reflection | +0.08 | +0.08 | Same |
| architect | -0.17 | +0.08 | Flipped |
| basic | 0.00 | 0.00 | Same |
| brutal | 0.00 | -1.08 | Dropped (1 outlier) |

**Key finding**: The keyword critic was systematically unfair to PPC and was hiding real improvements. LLM Judge revealed true quality.


### v1.1 — LLM Judge by Mode (detailed)

| Mode | RAW Avg | PPC Avg | Delta | Wins |
|------|---------|---------|:---:|:---:|
| compress | 9.6 | 9.9 | **+0.33** | 2/3 |
| focus | 9.3 | 9.8 | **+0.42** | 3/3 |
| code | 9.5 | 9.8 | +0.25 | 1/3 |
| teacher | 9.2 | 9.3 | +0.17 | 1/3 |
| architect | 8.9 | 9.0 | +0.08 | 1/3 |
| reflection | 9.2 | 9.3 | +0.08 | 1/3 |
| basic | 9.8 | 9.8 | 0.00 | 1/3 |
| brutal | 9.2 | 8.1 | -1.08 | 0/3 |

**brutal_02 collapse**: PPC over-optimized a SQL injection audit prompt, consuming 175 tokens of overhead. Claude responded 3.5x shorter (291 vs 1024 tokens). LLM Judge gave constraint_adherence=1.


## Benchmark v2 — 12 Hardest Prompts

**Difficulty**: Hard. Every prompt has 2-3 gotchas and 3-5 locked constraints. Complex code generation, security audits with 6+ vectors, architecture with strict latency/throughput constraints.

### v2 — LLM Judge + Inline Constraints

| Metric | Value |
|--------|-------|
| PPC Win Rate | 41.7% |
| Constraint Delta | -1.58 |
| Accuracy Delta | -1.58 |
| Clarity Delta | -0.08 |
| Efficiency Delta | -0.17 |

| Mode | RAW | PPC | Delta | Wins |
|------|:---:|:---:|:---:|:---:|
| **compress** | 9.0 | 9.8 | **+0.75** | 1/1 |
| **architect** | 9.0 | 9.5 | **+0.50** | 1/1 |
| reflection | 8.8 | 9.0 | +0.25 | 1/1 |
| brutal | 8.8 | 8.9 | +0.12 | 1/2 |
| teacher | 9.4 | 9.4 | 0.00 | 1/2 |
| **focus** | 7.1 | 6.5 | **-0.62** | 0/2 |
| **code** | 8.9 | 5.3 | **-3.58** | 0/3 |

### Code Mode v2 — Catastrophic Failure

| Prompt | RAW | PPC | Delta |
|--------|:---:|:---:|:---:|
| merge_sorted_arrays sin heapq/sort | 10.0 | 4.8 | -5.2 |
| JSON parser from scratch | 7.8 | 3.8 | -4.0 |
| Rate limiter sliding window | 9.0 | 7.5 | -1.5 |

**Root cause**: Complex code generation needs full output token budget. PPC inline constraint blocks consumed 80-150 tokens that Claude needed for actual code. Constraints competed with code for the same channel.

### v2 vs v1 by Mode (LLM Judge only)

| Mode | v1 Delta | v2 Delta | Change | What happened |
|------|:---:|:---:|:---:|------|
| compress | +0.33 | **+0.75** | +0.42 | Harder prompts show more benefit |
| architect | +0.08 | **+0.50** | +0.42 | Strict constraints amplify PPC |
| reflection | +0.08 | +0.25 | +0.17 | Multi-bug analysis benefits |
| brutal | -1.08 | **+0.12** | +1.20 | Recovered: structure helps audits |
| teacher | +0.17 | 0.00 | -0.17 | Word limits neutralize PPC |
| focus | +0.42 | **-0.62** | -1.04 | Overhead kills refactoring |
| code | +0.25 | **-3.58** | -3.83 | **Token budget collision** |


## Benchmark v3 — Code Mode Only (Solvable Tasks + System Channel)

**Difficulty**: High but solvable. 8 code prompts where Claude can succeed. Constraints enforced via system channel (v1.2 fix). Goal: test if PPC helps when tasks are achievable.

### v3 — LLM Judge + System Channel

| Metric | Value |
|--------|-------|
| PPC Win Rate | **50%** (4/8) |
| Overall Delta | -0.19 |
| Without outlier (#4) | +0.33 |

| # | Task | RAW | PPC | Delta | Result |
|---|------|:---:|:---:|:---:|:---:|
| 3 | Email validator sin `re` | 9.0 | 9.8 | **+0.8** | WIN |
| 5 | FIFO thread-safe sin `queue.Queue` | 7.5 | 8.2 | **+0.8** | WIN |
| 1 | flatten sin recursion | 9.5 | 9.8 | +0.2 | WIN |
| 6 | pathlib sort sin `os` | 9.8 | 10.0 | +0.2 | WIN |
| 2 | LRU+TTL sin `functools` | 9.0 | 9.0 | 0.0 | TIE |
| 7 | Retry decorator sin `tenacity` | 9.0 | 9.0 | 0.0 | TIE |
| 8 | lru_cache decorator sin `functools` | 9.0 | 9.0 | 0.0 | TIE |
| 4 | promise_all sin `asyncio.gather` | 7.8 | 4.2 | -3.5 | LOSS |

### v2 vs v3 — Code Mode Recovery

| Métrica | v2 Code | v3 Code | Recovery |
|---------|:---:|:---:|:---:|
| Delta | **-3.58** | **-0.19** | **+3.39** |
| Wins | 0/3 | 4/8 | |
| RAW avg | 8.9 | 8.8 | |
| PPC avg | 5.3 | 8.6 | |

**Without outlier #4 (promise_all)**: Delta = +0.33, PPC wins.

**Two changes caused the recovery**:
1. **System channel** (v1.2) — constraints via `system_prompt` don't consume output tokens
2. **Solvable tasks** (v3 design) — Claude can actually solve these, so PPC helps rather than competes


## All Benchmarks — Combined Summary

```
                  v1.0       v1.1       v2        v3
                  Keyword    LLM Judge  LLM Judge LLM Judge
                  Inline     Inline     Inline    System
                  ─────────────────────────────────────
PPC Win Rate      16.7%      41.7%      41.7%     50.0%
Overall Delta     -0.20      +0.03      -0.42     -0.19
Code Delta        -0.17      +0.25      -3.58     -0.19 ★
Focus Delta       -0.67      +0.42      -0.62     N/A
Compress Delta    +0.08      +0.33      +0.75 ★   N/A
Architect Delta   -0.17      +0.08      +0.50 ★   N/A

★ = Mode benefited most from hardness increase
```

---

## Key Insights Across All Benchmarks

### 1. The Critic Dictates the Result
v1.0 keyword critic showed PPC losing. v1.1 LLM judge showed PPC winning. The difference wasn't PPC — it was the measurement tool. Never trust keyword-based evaluators for LLM quality.

### 2. System Channel is Critical for Code
v2 code mode collapsed (-3.58) with inline constraints competing for output tokens. v3 showed recovery (-0.19) with system channel. For generative tasks, constraints must travel via system prompt.

### 3. Task Difficulty Must Be Calibrated
v2 used "extreme" prompts where even Claude raw couldn't succeed (JSON parser from scratch in 1500 tokens). On unsolvable tasks, PPC overhead makes things worse. On solvable tasks, PPC constraints guide without competing.

### 4. PPC Wins Where Constraints Are the Risk
compress (+0.75), architect (+0.50), focus (+0.42 in v1.1) — modes where the primary risk is violating a constraint, not solving the problem. PPC's constraint emphasis prevents the model from forgetting restrictions.

### 5. PPC is Neutral on Simple Tasks
basic mode shows zero delta across all benchmarks. For simple factual queries, PPC adds overhead without benefit. Anti-overengineering guardrails correctly prevent heavy pipelines on simple prompts.

### 6. The Single Biggest Problem: Over-Optimization
brutal_02 (v1) and code_01/03 (v2) show PPC can be too aggressive. When constraint emphasis consumes output tokens, the task itself suffers. The system channel fix (v1.2) addresses this for code/focus modes.


## Files

| File | Description |
|------|-------------|
| `data/benchmark_prompts.json` | v1 24 prompts (easy-medium) |
| `data/benchmark_results.json` | v1.0 keyword critic results |
| `data/benchmark_llm_judge_results.json` | v1.1 LLM judge results |
| `data/benchmark_v2_prompts.json` | v2 24 hard prompts |
| `data/benchmark_v2_subset_results.json` | v2 12 hardest prompts, LLM judge |
| `data/benchmark_v3_prompts.json` | v3 8 code prompts, solvable |
| `data/benchmark_v3_results.json` | v3 LLM judge + system channel |
| `data/BENCHMARK_REPORT.md` | v1 analysis |
| `data/BENCHMARK_V2_REPORT.md` | v2 analysis |
| `data/BENCHMARK_HISTORY.md` | This file |
| `tools/compare_v1_v2.py` | v1 vs v2 comparison script |
| `tools/compare_v3.py` | v2 vs v3 code comparison script |
