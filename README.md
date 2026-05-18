# PromptPropulserClaude

**Contextual cognition orchestration layer for LLMs**

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-134%20passed-green)]()
[![License](https://img.shields.io/badge/license-MIT-orange)]()

PPC optimizes how LLMs receive, interpret, and prioritize context without modifying the base model. It acts as cognitive middleware — analyzing prompts, detecting constraints, reinforcing attention, and evaluating output quality via LLM-as-Judge.

---

## What is PromptPropulserClaude?

LLMs don't "think" like humans. They operate on probabilistic attention, semantic patterns, and token prediction. This causes common failures: forgetting constraints mid-generation, ignoring critical details, drifting from the task, producing generic answers, and losing context in long prompts.

PPC solves this through an **Attention Reinforcement Engine (ARE)** that redistributes critical information in the prompt to increase attentional weight, plus a **Constraint Lock System** that makes restrictions non-negotiable, **Semantic Echo** for context reformulation, a **Reflection Pipeline** for self-evaluation, and an **LLM-as-Judge** that uses Claude itself to score output quality.

PPC is not a chatbot, a prompt wrapper, or a model fine-tuner. It is a **contextual cognition orchestration layer** — middleware between user intent and model execution.

### Pipeline

```
User Input
  ↓
Intent Analyzer → Constraint Classifier → Complexity Scorer
  ↓
Constraint Lock → Semantic Echo → Attention Reinforcement → Compression
  ↓
Optimized Prompt → Claude
  ↓
LLM-as-Judge (Claude Haiku) → Quality Score → Validated Response
```

---

## Quick Start

### Install as Skill (One Command)

```bash
# Linux / macOS
curl -sSL https://raw.githubusercontent.com/Pochonski/promptpropulser/master/install.sh | bash

# Windows (PowerShell)
iwr -Uri https://raw.githubusercontent.com/Pochonski/promptpropulser/master/install.ps1 -OutFile install.ps1; ./install.ps1
```

Or manually:

```bash
git clone https://github.com/Pochonski/promptpropulser ~/.claude/skills/promptpropulser
```

### Supported Agents

| Agent | Skill Path |
|-------|-----------|
| **Claude Code** | `~/.claude/skills/promptpropulser/` |
| **Cursor** | `~/.cursor/skills/promptpropulser/` |
| **OpenCode** | `~/.config/opencode/skills/promptpropulser/` |
| **OpenAI Codex** | `~/.codex/skills/promptpropulser/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/promptpropulser/` |

The install script copies `SKILL.md` to all detected agent directories.

### Usage

Just chat normally. PPC auto-detects the mode from your prompt:

```text
You: "Haz una API FastAPI sin base de datos en Python 3.12"
PPC:  [auto-detects code mode → locks constraints → reinforces → responds]

You: "Audita la seguridad de este endpoint JWT"
PPC:  [auto-detects brutal mode → maximum reinforcement → contradiction attack]

You: "Explicame Docker como si tuviera 10 anos"
PPC:  [auto-detects teacher mode → progressive explanation → analogies]
```

No commands needed. The skill activates when keywords match.

### Force a specific mode

```text
/ppc brutal — Analiza este sistema OAuth2
/ppc focus — Migra esto sin cambiar el esquema ni usar ORM
/ppc code — Implementa un rate limiter sin Redis
```

---

### Advanced: Python CLI + API

For programmatic use with benchmarks, FastAPI server, and LangChain integration:

```bash
pip install promptpropulser

export ANTHROPIC_API_KEY="sk-ant-..."

ppc --run code "Crea una API FastAPI sin base de datos"
ppc --ab brutal "Audita la seguridad de este JWT"
ppc --retry focus "Migra sin cambiar el esquema"

# Self-improvement loop (auto-retry on low scores)
ppc --retry focus "Migra este servicio a AWS sin usar Docker ni cambiar el esquema de DB"
```

---

## Modes

| Mode | Use Case | Reflection | Reinforcement |
|------|----------|-----------|---------------|
| `basic` | Simple queries, minimal overhead | 0 | low |
| `reflection` | Deep reasoning, logic validation | 3 | medium |
| `code` | Programming: bugs, imports, edge cases, compatibility | 2 | aggressive |
| `architect` | System design, dependency mapping, scalability | 2 | aggressive |
| `brutal` | Hypercritical security/architecture audit | 4+ | maximum |
| `focus` | Aggressive constraint retention, reduced creativity | 1 | aggressive |
| `teacher` | Progressive explanations with analogies | 1 | low |
| `compress` | Token reduction, deduplication | 0 | none |

---

## CLI Reference

```
ppc <mode> "<prompt>" [flags]

Modes: basic | reflection | code | architect | brutal | focus | teacher | compress

Core Flags:
  --run              Optimize + send to Claude + LLM Judge evaluation
  --ab               A/B test: raw prompt vs PPC-optimized
  --retry            Self-improvement loop (auto-retry up to 3x on low scores)
  --verbose          Full analysis output with metadata
  --hybrid           Optimized prompt + short summary
  --json             JSON output

LLM Control:
  --api-key KEY      Anthropic API key
  --model MODEL      Claude model (default: claude-sonnet-4-6)
  --base-url URL     Custom API base URL for proxies
  --system-prompt P  Path to .md system prompt file
  --no-judge         Use keyword critic instead of LLM Judge (faster, less accurate)

Pipeline Control:
  --reinforcement    none | low | medium | aggressive | maximum
  --reflection-depth 0-5
  --compress         Force compression on
  --token-budget N   Token budget (default: 4000)
  --save-session     Save SessionLog to sessions/
  --judge-model M    Judge model (default: claude-haiku-4-5-20251001)

Pipe input:
  echo "Explicame Docker" | ppc teacher --run
```

---

## FastAPI Server

```bash
pip install promptpropulser[server]
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/optimize` | Optimize a prompt, return optimized version |
| `POST` | `/generate` | Optimize + send to Claude + judge + return response |
| `POST` | `/ab` | A/B test: raw vs PPC with judge scores |
| `GET` | `/health` | Health check |
| `GET` | `/modes` | List available modes with config |
| `GET` | `/sessions` | List saved session logs |

### Example

```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{"mode":"code","prompt":"Crea una API FastAPI sin base de datos"}'
```

---

## Docker

```bash
docker build -t promptpropulser .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY promptpropulser
```

Or with compose:

```yaml
services:
  ppc:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

---

## LangChain Integration

```python
from ppc.integration.langchain import PPCPromptTemplate, PPCOptimizer

# Standalone: optimize any prompt
template = PPCPromptTemplate(mode="code")
optimized = template.format(input="Haz una API en FastAPI sin base de datos")

# As a chain step
optimizer = PPCOptimizer(mode="brutal")
prompt = optimizer("Audita la seguridad de este JWT")
```

---

## LLM-as-Judge

PPC uses Claude Haiku as an impartial evaluator that scores responses on four dimensions:

| Dimension | What it measures |
|-----------|-----------------|
| **constraint_adherence** | All locked constraints respected? Understands negation context ("SIN Docker" = compliant) |
| **clarity** | Well-structured, easy to follow, properly formatted |
| **accuracy** | Factually correct, technically sound, no hallucinations |
| **efficiency** | Concise without losing quality, proportional to task |

Unlike keyword-based critics, the LLM Judge understands:
- Negation context ("without X" vs "using X")
- Code quality beyond surface patterns
- Proportional response length (complex tasks merit thorough answers)
- Real factual accuracy, not just keyword presence

Disable with `--no-judge` for zero-cost evaluation using fast keyword heuristics.

---

## Benchmark Results

24 prompts across 8 modes, each tested RAW (direct to Claude) vs PPC (optimized pipeline), scored by LLM-as-Judge (Claude Haiku, temperature=0).

| Metric | Value |
|--------|-------|
| PPC Win Rate | **41.7%** |
| Accuracy Delta | **+0.12** |
| Clarity Delta | **+0.21** |
| Efficiency Delta | **+0.17** |

### Per-Mode Performance

| Mode | RAW Avg | PPC Avg | Delta | Wins |
|------|---------|---------|-------|------|
| focus | 9.3 | 9.8 | **+0.42** | 3/3 |
| compress | 9.6 | 9.9 | **+0.33** | 2/3 |
| code | 9.5 | 9.8 | **+0.25** | 1/3 |
| teacher | 9.2 | 9.3 | +0.17 | 1/3 |
| architect | 8.9 | 9.0 | +0.08 | 1/3 |
| reflection | 9.2 | 9.3 | +0.08 | 1/3 |
| basic | 9.8 | 9.8 | 0.00 | 1/3 |

- **Focus mode** shows strongest improvement: aggressive constraint retention + LLM Judge correctly identifies compliance (keyword critics historically misread repeated constraints as violations).
- **Compress mode**: Token reduction improves clarity and efficiency without losing quality.
- **Simple prompts** (basic): PPC matches raw — zero degradation.

Full benchmark data in `data/benchmark_llm_judge_results.json`.

---

## Architecture

```
ppc/
├── engine/           # Orchestrator + Pipeline executor
├── analyzers/        # Intent, Constraint, Complexity (0-100 score)
├── transformers/     # Lock, Echo, Reinforcement, Compression
├── reflection/       # 4-stage self-evaluation
├── critic_llm.py     # LLM-as-Judge (Claude Haiku)
├── delivery/         # Output formatter (transparent/hybrid/verbose)
├── config/           # Modes, thresholds, heuristics, rules, guardrails
├── schemas/          # Input/Output/SessionLog dataclasses
├── integration/      # Anthropic client, LangChain adapter
├── loop.py           # Self-improvement loop (run_once / run_until_pass)
├── session_store.py  # JSON/CSV persistence
├── benchmark.py      # 24-prompt benchmark runner
│
prompts/
├── system_prompt.md  # Executable system prompt for Claude (~700 lines)
└── few_shot/         # 8 examples (1 per mode)
│
server.py             # FastAPI REST API (6 endpoints)
cli.py                # Full CLI with --run, --ab, --retry
Dockerfile
pyproject.toml        # PyPI-ready package config
data/                 # Benchmark dataset + results
tests/                # 134 unit tests
```

---

## How It Works

### 1. Intent Analysis
Detects the primary goal (create, fix, explain, analyze, design...), secondary goals, domain (coding, architecture, cybersecurity, writing, chat), and signal triggers.

### 2. Constraint Classification
Pattern-based detection of hard constraints ("no uses", "sin", "obligatorio", "mantén") → locked. Soft constraints ("preferiblemente", "si puedes") → preferred. Auto-classifies constraint type: technological, structural, format, length, compatibility, style, security, architecture.

### 3. Complexity Scoring
5-component weighted formula (0-100): constraint count, prompt length, ambiguity, reasoning depth, domain complexity. Determines pipeline intensity.

### 4. Attention Reinforcement Engine (ARE)
Strategically redistributes critical information: intro reinforcement (primacy effect), middle checkpoint, final reminders (recency effect), priority stacking, pre-response validation checklists.

### 5. Semantic Echo
Reformulates constraints without verbatim repetition. "No uses React" → "The solution must avoid React frameworks and dependencies entirely." Increases contextual activation without appearing redundant.

### 6. Constraint Lock
Converts critical restrictions into immutable blocks pinned at top and bottom of the prompt. Prevents the model from forgetting constraints during long generations.

### 7. Reflection Pipeline
4-stage self-evaluation: intent validation, constraint validation, quality analysis, failure simulation.

### 8. LLM-as-Judge
Claude Haiku evaluates the final response on constraint adherence, clarity, accuracy, and efficiency. Temperature=0 for deterministic scoring. JSON-structured output. Fallback to keyword critic on parse failure.

---

## Development

```bash
git clone https://github.com/your-org/promptpropulser
cd promptpropulser
pip install -e ".[dev]"

# Run all tests
python -m pytest tests/ -v

# 134 tests across 13 test files
# Coverage: schemas, config, analyzers, transformers, reflection,
#           critic (keyword + LLM judge), loop, integration, pipeline, modes
```

---

## Philosophy

PPC does not replace the model's reasoning capability. PPC maximizes the quality of the context the model receives.

**We optimize:**
- Attentional focus (primacy + recency effects)
- Instruction persistence across long generations
- Constraint stability against "forgetting"
- Semantic priority weighting

**We do NOT:**
- Modify model weights
- Train or fine-tune
- Replace the underlying LLM

PPC is a **contextual cognition orchestration layer** — middleware between user intent and model execution.

---

## License

MIT
