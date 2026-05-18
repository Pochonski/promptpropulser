# PromptPropulserClaude

**Contextual cognition orchestration layer for LLMs**

[![Tests](https://img.shields.io/badge/tests-134%20passed-green)]()
[![License](https://img.shields.io/badge/license-MIT-orange)]()

PPC is a **skill for coding agents** that makes LLMs obey constraints, detect intent, and self-critique their responses. Drop it into Claude Code, Cursor, or OpenCode — no API keys, no install, no Python. Just chat and PPC activates automatically.

---

## Quick Start

### One command

```bash
# Linux / macOS
curl -sSL https://raw.githubusercontent.com/Pochonski/promptpropulser/master/install.sh | bash

# Windows
iwr https://raw.githubusercontent.com/Pochonski/promptpropulser/master/install.ps1 -OutFile install.ps1; ./install.ps1
```

Or clone manually:

```bash
git clone https://github.com/Pochonski/promptpropulser ~/.claude/skills/promptpropulser
```

### Supported agents

| Agent | Path |
|-------|------|
| **Claude Code** | `~/.claude/skills/promptpropulser/` |
| **Cursor** | `~/.cursor/skills/promptpropulser/` |
| **OpenCode** | `~/.config/opencode/skills/promptpropulser/` |
| **OpenAI Codex** | `~/.codex/skills/promptpropulser/` |
| **Google Antigravity** | `~/.gemini/antigravity/skills/promptpropulser/` |

The skill file is `SKILL.md` — a single markdown file with YAML frontmatter that the agent reads on startup.

---

## What It Does

LLMs fail in predictable ways: they forget restrictions, drift from the task, lose context in long prompts. PPC fixes this by rewriting how the model **receives and prioritizes** instructions — without touching model weights.

```
You:  "Haz una API sin base de datos, compatible con Python 3.12"
                                                                    
PPC:  [detects constraints: NO database, Python 3.12]               
      [locks them as non-negotiable]                                 
      [echoes them semantically]                                     
      [builds pre-response validation checklist]                     
      [sends optimized prompt to Claude]                             
                                                                    
Claude:  def app():                                                  
             # Python 3.12 type hints
             # In-memory storage — no database
             return FastAPI()
```

**PPC doesn't generate better answers. PPC gives Claude a better question.**

---

## How the Skill Works

There are no commands. You chat normally and PPC auto-detects which mode to activate from your prompt:

### Auto-Detection Triggers

| You say... | PPC activates |
|------------|---------------|
| `codigo`, `API`, `funcion`, `bug`, `implementa`, `FastAPI`, `endpoint` | **code** — validates syntax, imports, edge cases |
| `seguridad`, `vulnerabilidad`, `audita`, `exploit`, `hack`, `JWT` | **brutal** — contradiction attack, tries to break own response |
| `arquitectura`, `disena`, `sistema`, `microservicios`, `escalable` | **architect** — modular decomposition, dependency mapping |
| `analiza`, `profundo`, `investiga`, `evalua`, `debug` | **reflection** — multi-pass reasoning, self-critique |
| `explicame`, `paso a paso`, `tutorial`, `ELI5`, `ensenia` | **teacher** — progressive explanation, analogies |
| `rapido`, `breve`, `resumen`, `corto`, `TLDR`, `conciso` | **compress** — token reduction, deduplication |
| `NO uses`, `SIN`, `obligatorio`, `manten`, `no cambies` | **focus** — aggressive constraint retention |
| *(none of the above)* | **basic** — minimal overhead |

The agent loads `SKILL.md` → reads the YAML triggers → applies the matching pipeline. Everything happens in the model's reasoning — no external code runs.

### Force a specific mode

```text
/ppc brutal — Audita este flujo OAuth2
/ppc focus — Migra esto sin cambiar el esquema ni usar Docker
/ppc code — Implementa un rate limiter con sliding window
```

---

## What the Skill Does Internally

When a mode activates, PPC rewrites your prompt before the model processes it:

```
Your prompt:
    "Haz una API en FastAPI sin base de datos"

PPC transforms it into:
    LOCKED CONSTRAINTS (NON-NEGOTIABLE):
      [1] No database usage.
    
    PRIMARY TASK: Create
    
    Create a FastAPI API.
    
    [ECHO] The solution must avoid any database dependency entirely.
    
    PRE-RESPONSE VALIDATION:
      [ ] Verified: no database imports or ORM
      [ ] Verified: no SQLAlchemy, SQLite references
    
    REMINDER: No database usage.
```

Then after generating, PPC runs a **critic self-check**: constraint adherence, accuracy, clarity, efficiency. If any score ≤ 3, it regenerates.

---

## Modes

| Mode | What it does | When to use |
|------|-------------|-------------|
| **code** | Validates syntax, edge cases, imports, compatibility | Programming tasks |
| **brutal** | Contradiction attack, failure simulation, exploit reasoning | Security audits |
| **architect** | Modular decomposition, dependency mapping, scalability analysis | System design |
| **reflection** | Multi-pass reasoning, logic validation, self-critique | Analysis & debugging |
| **teacher** | Progressive explanation, analogies, adaptive complexity | Explanations |
| **focus** | Triple constraint lock, aggressive reinforcement | Constraint-heavy tasks |
| **compress** | Deduplication, filler removal, semantic compression | Long prompts |
| **basic** | Minimal overhead, no reflection | Simple questions |

---

## Why Only a Markdown File?

Because the entire system is **rules** — not code. The Attention Reinforcement Engine (ARE), Semantic Echo, Constraint Lock, Reflection Pipeline, and Critic Engine are all **behaviors** the model executes by following instructions in `SKILL.md`.

The file is structured so the model can execute the pipeline in its own reasoning:
1. Detect intent → 2. Classify constraints → 3. Lock critical rules → 4. Echo semantically → 5. Reinforce attention → 6. Reflect → 7. Deliver

No external runtime needed. The skill works in any agent that reads `SKILL.md`.

---

## Benchmark Results

24 prompts across 8 modes, scored by **LLM-as-Judge** (Claude Haiku evaluates response quality on constraint adherence, accuracy, clarity, efficiency):

| Metric | Value |
|--------|-------|
| PPC Win Rate (vs raw prompt) | **41.7%** |
| Accuracy Delta | **+0.12** |
| Clarity Delta | **+0.21** |
| Efficiency Delta | **+0.17** |

| Mode | RAW Avg | PPC Avg | Delta | Wins |
|------|:---:|:---:|:---:|:---:|
| focus | 9.3 | 9.8 | **+0.42** | 3/3 |
| compress | 9.6 | 9.9 | **+0.33** | 2/3 |
| code | 9.5 | 9.8 | +0.25 | 1/3 |
| teacher | 9.2 | 9.3 | +0.17 | 1/3 |
| architect | 8.9 | 9.0 | +0.08 | 1/3 |
| reflection | 9.2 | 9.3 | +0.08 | 1/3 |
| basic | 9.8 | 9.8 | 0.00 | 1/3 |

Full benchmark history: [`data/BENCHMARK_HISTORY.md`](data/BENCHMARK_HISTORY.md)

---

## Advanced: Python for Production

The Python package (`ppc/`) is the **deterministic implementation** of the same pipeline — useful when you need measurement, APIs, or infrastructure integration.

### CLI

```bash
pip install promptpropulser
export ANTHROPIC_API_KEY="sk-ant-..."

# Optimize + send to Claude + LLM judge
ppc --run code "Crea una API FastAPI sin base de datos"

# A/B test raw vs PPC
ppc --ab brutal "Audita este JWT"

# Self-improvement loop with auto-retry
ppc --retry focus "Migra sin cambiar el esquema"

# Disable LLM judge for zero-cost evaluation
ppc --run --no-judge code "Haz una funcion Python"
```

### FastAPI Server

```bash
pip install promptpropulser[server]
uvicorn server:app --host 0.0.0.0 --port 8000
```

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/optimize` | Optimize a prompt |
| `POST` | `/generate` | Optimize + Claude + Judge |
| `POST` | `/ab` | A/B test raw vs PPC |
| `GET` | `/health` | Health check |
| `GET` | `/modes` | List modes |
| `GET` | `/sessions` | Session history |

### Docker

```bash
docker build -t promptpropulser .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY promptpropulser
```

### LangChain

```python
from ppc.integration.langchain import PPCOptimizer

optimizer = PPCOptimizer(mode="brutal")
prompt = optimizer("Audita este endpoint JWT")
# → send prompt to your existing LangChain LLM
```

---

## Repository Structure

```
promptpropulser/
│
├── SKILL.md              # ← The skill. Drop into any agent.
├── install.sh            # ← One-command install to all agents
├── install.ps1           # ← Same for Windows
│
├── prompts/
│   ├── system_prompt.md  # ← Load manually into claude.ai Projects
│   └── few_shot/         #   8 examples (1 per mode)
│
├── ppc/                  # Python implementation (advanced)
│   ├── engine/           #   Orchestrator + Pipeline executor
│   ├── analyzers/        #   Intent, Constraint, Complexity
│   ├── transformers/     #   Lock, Echo, Reinforcement, Compression
│   ├── config/           #   Modes, thresholds, heuristics, guardrails
│   ├── reflection/       #   4-stage reflection + critic
│   ├── delivery/         #   Output formatter
│   ├── integration/      #   Anthropic client, LangChain
│   ├── benchmark.py      #   24-prompt benchmark runner
│   ├── loop.py           #   Self-improvement loop
│   └── critic_llm.py     #   LLM-as-Judge
│
├── server.py             # FastAPI REST API
├── cli.py                # Full CLI
├── Dockerfile
├── tests/                # 134 unit tests
├── data/                 # Benchmark datasets + reports
├── docs/                 # Architecture specification
└── tools/                # Benchmark comparison scripts
```

---

## Philosophy

PPC does not replace the model's reasoning. PPC maximizes the quality of the context the model receives.

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

## Development

```bash
git clone https://github.com/Pochonski/promptpropulser
cd promptpropulser
pip install -e ".[dev]"
python -m pytest tests/ -v    # 134 tests
```

---

## License

MIT
