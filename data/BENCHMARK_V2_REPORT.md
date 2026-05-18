# PromptPropulserClaude v1.1 — Benchmark v2 Report

**Date**: 2026-05-18
**Model**: claude-sonnet-4-6 (generation) + claude-haiku-4-5-20251001 (judge)
**Prompts**: 12 (selected hardest from 24-prompt v2 dataset)
**Evaluator**: LLM-as-Judge (Claude Haiku, temperature=0)

---

## Executive Summary

Benchmark v2 was designed with **genuinely hard prompts** — each containing 2-3 gotchas and 3-5 locked constraints. Unlike v1 where 9/24 prompts were trivial, v2 forces differentiation between raw and PPC.

**Result: PPC shows strong gains (+0.5 to +0.8) on architecture, compression, and reflection modes. But catastrophic losses (-3.6 to -5.2) on complex code generation tasks when PPC overhead competes with Claude's output token budget.**

The v2 benchmark revealed the single most important design insight in this project: **PPC's inline constraint enforcement is beneficial for structural/semantic tasks but harmful for generative tasks where the output itself needs full token capacity.**

---

## Overall Results

| Metric | v1 LLM Judge | v2 LLM Judge | Change |
|--------|:---:|:---:|:---:|
| PPC Win Rate | 41.7% | 41.7% | 0% |
| Constraint Delta | -0.38 | **-1.58** | -1.20 |
| Accuracy Delta | +0.12 | **-1.58** | -1.70 |
| Clarity Delta | +0.21 | -0.08 | -0.29 |
| Efficiency Delta | +0.17 | -0.17 | -0.34 |

The overall numbers declined because v2 hard code prompts dominated the results. When we segment by task type, a different picture emerges.

---

## Per-Mode Results (v1 vs v2, LLM Judge)

| Mode | v1 Delta | v2 Delta | Change | Analysis |
|------|:---:|:---:|:---:|-----------|
| **compress** | +0.33 | **+0.75** | +0.42 | Best mode. Consistently wins. Token reduction + constraint preservation. |
| **architect** | +0.08 | **+0.50** | +0.42 | Hard architecture prompts show PPC benefit clearly. |
| **reflection** | +0.08 | **+0.25** | +0.17 | Multi-bug analysis improves with constraint emphasis. |
| **teacher** | +0.17 | 0.00 | -0.17 | Hard teaching prompts (350-word limit) neutralize PPC. |
| **brutal** | -1.08 | **+0.12** | +1.20 | Major recovery. Hard security prompts = PPC structure helps. |
| **focus** | +0.42 | **-0.62** | -1.04 | Multi-constraint refactoring: overhead hurts. |
| **code** | +0.25 | **-3.58** | -3.83 | **Catastrophic.** Complex code generation + PPC overhead = failure. |

---

## Key Findings

### 1. Compress Mode is the Undisputed Winner

Both v1 (+0.33) and v2 (+0.75) show PPC consistently improves token-heavy prompts. The 400-word e-learning recommendation prompt was compressed from 350 tokens to core constraints (no collaborative filtering, <100ms, explainable, no cloud). Claude's raw response included unnecessary preamble; PPC's response was direct and constraint-compliant.

### 2. Code Mode Collapse — The Token Budget Problem

The v2 code prompts (merge sort from scratch, sliding window rate limiter, JSON parser from scratch) are **genuinely hard code generation tasks** that need every available output token. PPC injected 80-150 tokens of constraint lock + echo blocks. This consumed 10-20% of the output budget that Claude needed for the actual code.

Result: PPC responses were shorter, missed edge cases, and scored poorly with the LLM Judge on accuracy.

```
code_01: merge_sorted_arrays without heapq — RAW 10.0, PPC 4.8 (-5.2)
code_03: JSON parser from scratch — RAW 7.8, PPC 3.8 (-4.0)
code_02: rate limiter sliding window — RAW 9.0, PPC 7.5 (-1.5)
```

**Root Cause**: Code generation tasks need constraints injected as **system-level instructions** (which don't consume output tokens), not as inline lock blocks that compete with the code for Claude's response budget.

### 3. Brutal Mode Recovered

In v1, brutal mode scored -1.08 due to one catastrophic prompt (brutal_02: PPC over-optimized a SQL injection audit, reducing response from 1024 to 291 tokens). In v2, harder security prompts with genuine multi-vector attacks showed PPC's structure helps Claude be more thorough: +0.12.

### 4. Focus Mode Flipped Negative

v1 focus mode showed the strongest PPC improvement (+0.42) because the keyword critic stopped giving false positives. But v2 harder focus prompts — real code refactoring with 5 simultaneous constraints + line limits — showed PPC overhead consuming output capacity.

### 5. Architecture Mode Improved with Hardness

v1 architecture prompts were too easy (general design). v2 added real constraints (1000tx/s, no Kafka, no 2PC, <200ms p99) that benefit from PPC's constraint emphasis. Delta: +0.08 → +0.50.

---

## Critical Design Insight

```
Task Type          | PPC Impact | Why
-------------------|-----------|-----------------------------------------
Compression        | STRONG +  | Token reduction = always beneficial
Architecture       | MODERATE +| Constraints improve structure
Reflection         | MODERATE +| Multi-bug emphasis helps
Security Audit     | NEUTRAL   | Structure helps, but overhead can hurt
Teaching           | NEUTRAL   | Word limits neutralize PPC
Focus (code)       | MODERATE -| Overhead competes with output
Code (complex)     | STRONG -  | Token budget collision kills quality
```

**The fundamental insight**: When the output **IS** the task (code, refactoring), PPC's inline blocks steal tokens from Claude. When the output is **ABOUT** the task (design, explanation, audit), PPC's structure guides Claude without competing for output tokens.

---

## Recommended Fix for v1.2

### Code Mode — System-Level Constraints

Instead of injecting LOCKED CONSTRAINTS as inline text blocks that consume output tokens, code mode should pass constraints as the **system prompt** parameter:

```python
# v1.1 (current) — constraints eat output tokens
optimized_prompt = """
LOCKED CONSTRAINTS: no heapq, no sort()
PRIMARY TASK: Implement merge_sorted_arrays...
[ECHO] Do not use heapq...
"""

# v1.2 (proposed) — constraints as system prompt
system_prompt = """
CONSTRAINTS: no heapq, no sort(). Type hints required.
"""
user_prompt = "Implement merge_sorted_arrays(arrays)..."
```

This keeps Claude's full output budget for code while ensuring constraints are respected through the system channel.

### Implement as mode flag

Add `constraint_channel` to ModeConfig: `"inline"` | `"system"`. Code and focus modes default to `"system"`. All others keep `"inline"`.

---

## Files Generated

| File | Description |
|------|-------------|
| `data/benchmark_v2_prompts.json` | 24 hard prompts (3 per mode), each with 2-3 gotchas |
| `data/benchmark_v2_subset_results.json` | Results for 12 hardest prompts |
| `tools/compare_v1_v2.py` | v1 vs v2 comparison script |
| `tools/run_v2_quick.py` | Quick benchmark runner |
| `data/BENCHMARK_V2_REPORT.md` | This report |

---

## Conclusion

Benchmark v2 succeeded in its goal: **it found where PPC genuinely helps and where it hurts**. The architectural insight — inline vs system-level constraint injection — is actionable and would likely fix the code mode collapse.

PPC is not a universal optimizer. It is a **task-dependent contextual enhancer** that works best when the output is ABOUT constraints (design, explanation) and worst when the output IS the constraint (code, refactoring). The v1.2 fix would make PPC task-aware and likely unlock stronger performance across all modes.
