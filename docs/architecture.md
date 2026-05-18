# PromptPropulserClaude v1 — Architecture Specification

A contextual cognition orchestration layer for LLMs.

---

## 1. SYSTEM EXECUTION MODEL

PPC functions as cognitive middleware between user and LLM:

```
User Input → Intent Analyzer → Constraint Classifier → Priority Engine
→ Attention Reinforcement Engine → Semantic Echo Generator
→ Prompt Compression Engine → Reflection Pipeline
→ Final Optimized Prompt → Claude Execution → Critic Engine → Validated Response
```

## 2. INPUT / OUTPUT SPECIFICATION

### Input Schema
```json
{
  "mode": "basic|reflection|code|architect|brutal|focus|teacher|compress",
  "prompt": "user raw prompt",
  "options": {
    "reinforcement_level": "none|low|medium|aggressive|maximum",
    "reflection_depth": 0-5,
    "compression": false,
    "strict_constraints": true,
    "verbosity": "short|medium|long",
    "token_budget": 4000
  }
}
```

### Output Schema
```json
{
  "analyzed_intent": {"primary_goal": "", "secondary_goals": [], "complexity_score": 0-100},
  "constraints": {"locked": [], "soft": [], "detected_types": []},
  "reinforcement": {"level": "", "applied_patterns": []},
  "semantic_echoes": [],
  "optimized_prompt": "",
  "reflection": {"enabled": false, "checks": [], "critic_notes": []},
  "token_usage": {"input_tokens": 0, "optimization_tokens": 0, "final_prompt_tokens": 0}
}
```

## 3. CONSTRAINT DETECTION ENGINE

### Hard Constraint Triggers → LOCKED
no uses, sin, evita, prohibido, nunca, obligatorio, debe, solo usa, mantén, no cambies, no agregues

### Soft Constraint Triggers → SOFT
preferiblemente, idealmente, si puedes, me gustaría, opcional, recomendado

### Signal Triggers
- Compression: rápido, breve, resumen, corto, TLDR
- Deep Analysis: analiza, profundo, investiga, debug
- Security/Brutal: seguridad, vulnerabilidad, hack, exploit
- Teaching: explícame, paso a paso, tutorial, ELI5

## 4. REINFORCEMENT LEVELS

| Level | Intro | Middle | Final | Echoes | Lock |
|-------|-------|--------|-------|--------|------|
| none | 0 | 0 | 0 | 0 | No |
| low | 0 | 0 | 2 | 1 | No |
| medium | 1 | 0 | 2 | 1 | Yes |
| aggressive | 1 | 1 | 2 | 2 | Yes |
| maximum | 2 | 1 | 3 | 3 | Yes |

## 5. CONFLICT RESOLUTION

Priority: Safety > Locked Constraints > User Goals > Format > Style > Verbosity

| Conflict | Resolution |
|----------|-----------|
| corto + paso a paso | Short structured steps |
| seguridad + velocidad | Security overrides |
| sin dependencias + usa X | Framework wins |
| no cambies + refactoriza | Keep structure |

## 6. PROMPT COMPRESSION ENGINE

- Auto-compress if tokens > 2500
- Target reduction: 20-40%
- Remove duplicates > 2 occurrences
- Strip filler phrases
- Preserve intent + locked constraints

## 7. TOKEN BUDGET MANAGEMENT

| Prompt Size | Optimization | Generation |
|-------------|-------------|------------|
| <300 tokens | 15% | 85% |
| 300-2000 | 25% | 75% |
| >2000 | 35% | 65% |

Anti-waste: Never spend more optimization tokens than original prompt length.

## 8. ANTI-OVERENGINEERING GUARDRAILS

1. If tokens < 100: disable deep reflection, brutal, multi-pass
2. Simple prompts → simple pipelines
3. Never maximum reinforcement for casual chat
4. If constraints ≤ 1: no semantic echoes

## 9. REFLECTION PIPELINE

1. Intent Validation — Did I understand correctly?
2. Constraint Validation — Any locked constraint violated?
3. Quality Analysis — Can it be clearer, safer, simpler?
4. Failure Simulation — What would break this?

## 10. SELF-IMPROVEMENT LOOP

Session log tracks: original → optimized_v1 → LLM output → critic score → optimized_v2

### Critic Score (each 0-10)
- constraint_following
- clarity
- accuracy
- efficiency

Regenerate if any critical score ≤ 3.

## 11. FEW-SHOT EXAMPLES

See `prompts/few_shot/` for complete examples of each mode.

## 12. EXECUTABLE SYSTEM PROMPT

See `prompts/system_prompt.md` for the full system prompt loaded into Claude.

## 13. FUTURE EXPANSION (v2)

- Multi-Agent Critic System (security, logic, architecture, style)
- Reinforcement Learning Logs
- Adaptive Reinforcement AI
- Hallucination Detection

## 14. MODE EXECUTION MATRIX

| Mode | Reflection | Echo | Lock | Critic | Compress | Multi-Pass | Reinforcement |
|------|-----------|------|------|--------|----------|-----------|---------------|
| basic | 0 | low | soft | no | no | no | low |
| reflection | 3 | medium | enabled | yes | optional | yes | medium |
| code | 2 | medium | aggressive | yes | no | yes | aggressive |
| architect | 2 | medium | enabled | yes | optional | yes | aggressive |
| brutal | 4+ | maximum | maximum | maximum | no | yes | maximum |
| focus | 1 | aggressive | maximum | optional | no | no | aggressive |
| teacher | 1 | low | soft | no | no | no | low |
| compress | 0 | none | disabled | no | maximum | no | none |

## 15. COMPLEXITY SCORE ENGINE

**score = constraint_weight + token_weight + ambiguity_weight + reasoning_weight + domain_weight**

| Component | Max | Thresholds |
|-----------|-----|-----------|
| Constraints | 25 | 0→0, 1-2→5, 3-5→10, 6-10→18, 10+→25 |
| Length | 20 | <100→2, 100-500→6, 500-1500→12, 1500-3000→16, 3000+→20 |
| Ambiguity | 20 | low→2, medium→8, high→15, critical→20 |
| Reasoning | 20 | none→0, light→5, medium→10, deep→20 |
| Domain | 15 | chat→0, writing→3, coding→7, architecture→10, cybersecurity→15 |

### Classifications
- 0-20: Simple → basic pipeline
- 21-50: Medium → standard pipeline
- 51-80: Complex → deep pipeline
- 81-100: Critical → maximum pipeline

## 16. USER DELIVERY LAYER

| Mode | Visibility |
|------|-----------|
| transparent | Optimized prompt only (default) |
| hybrid | Prompt + short optimization summary |
| verbose | Full analysis with all metadata |
