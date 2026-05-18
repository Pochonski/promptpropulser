"""
LLM-as-Judge — Semantic response quality evaluator.

Replaces keyword-based heuristics with actual Claude evaluation.
Understands negation context, code quality, and proportional length.

Uses a separate, cheaper Claude model (haiku) for judging to minimize cost.
"""

import json
import re

from ppc.schemas.output import DetectedConstraints
from ppc.schemas.session_log import CriticScore
from ppc.reflection.critic import CriticResult
from ppc.integration.base import BaseLLMClient


JUDGE_SYSTEM_PROMPT = """You are an impartial response quality evaluator.
Your job is to score LLM outputs against user constraints.

CRITICAL RULES:
- "Without X", "SIN X", "no X" in the response = constraint RESPECTED.
- Only penalize if a constraint is ACTUALLY violated.
- Score proportionally: a simple question needs a short answer.
  A complex architecture question needs a thorough answer.
- Clarity = well-structured, easy to follow, properly formatted.
- Accuracy = factually correct, technically sound, no hallucinations.
- Efficiency = concise without losing quality. No filler.

Output ONLY valid JSON with no markdown, no explanation, no backticks."""


JUDGE_PROMPT_TEMPLATE = """ORIGINAL USER PROMPT:
{prompt}

LOCKED CONSTRAINTS (must be absolutely respected):
{constraints}

RESPONSE TO EVALUATE:
{response}

Score each dimension from 1 to 10 (1=worst, 10=best):

1. constraint_adherence: Does the response respect ALL locked constraints?
   Check negation context. "Without X", "SIN X", "no X" = RESPECTED COMPLIANCE.

2. clarity: Is the response well-structured, easy to follow, properly formatted?

3. accuracy: Is the response factually correct and technically sound?

4. efficiency: Is the response concise without losing quality? No filler?

Output ONLY this exact JSON structure:
{{"constraint_adherence": <1-10>, "clarity": <1-10>, "accuracy": <1-10>, "efficiency": <1-10>}}"""


def _build_judge_prompt(
    original_prompt: str,
    constraints: DetectedConstraints,
    response: str,
) -> str:
    constraints_text = "\n".join(
        f"  [{i}] {c.strip()}"
        for i, c in enumerate(constraints.locked, 1)
    ) if constraints.locked else "  (no locked constraints)"

    return JUDGE_PROMPT_TEMPLATE.format(
        prompt=original_prompt.strip(),
        constraints=constraints_text,
        response=response.strip()[:6000],
    )


def _parse_judge_response(text: str) -> dict | None:
    text = text.strip()

    json_match = re.search(r"\{[^}]+\}", text)
    if json_match:
        text = json_match.group(0)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        text_clean = text.replace("'", '"')
        try:
            data = json.loads(text_clean)
        except json.JSONDecodeError:
            return None

    required = {"constraint_adherence", "clarity", "accuracy", "efficiency"}
    if not required.issubset(set(data.keys())):
        return None

    for key in required:
        val = data[key]
        if isinstance(val, (int, float)):
            data[key] = max(1, min(10, int(val)))
        else:
            return None

    return data


def llm_evaluate_response(
    response: str,
    original_prompt: str,
    constraints: DetectedConstraints,
    judge_client: BaseLLMClient,
    judge_model: str = "claude-haiku-4-5-20251001",
) -> CriticResult:
    if not response.strip():
        return CriticResult(
            score=CriticScore(0, 0, 0, 0),
            issues=["Empty response."],
            recommendation="Regenerate. Response is empty.",
            needs_regeneration=True,
        )

    judge_prompt = _build_judge_prompt(original_prompt, constraints, response)

    original_model = judge_client.model
    judge_client.model = judge_model

    try:
        result = judge_client.generate(
            prompt=judge_prompt,
            system_prompt=JUDGE_SYSTEM_PROMPT,
            max_tokens=256,
            temperature=0.0,
        )
    except Exception as e:
        judge_client.model = original_model
        from ppc.reflection.critic import evaluate_response as keyword_eval
        result_kw = keyword_eval(response, original_prompt, original_prompt, constraints)
        result_kw.issues.append(f"[LLM Judge fallback: {e}]")
        return result_kw
    finally:
        judge_client.model = original_model

    scores = _parse_judge_response(result.text)

    if scores is None:
        from ppc.reflection.critic import evaluate_response as keyword_eval
        result_kw = keyword_eval(response, original_prompt, original_prompt, constraints)
        result_kw.issues.append("[LLM Judge: JSON parse failed, used keyword fallback]")
        return result_kw

    score = CriticScore(
        constraint_following=scores["constraint_adherence"],
        clarity=scores["clarity"],
        accuracy=scores["accuracy"],
        efficiency=scores["efficiency"],
    )

    needs_regeneration = score.constraint_following <= 3 or score.accuracy <= 3

    if needs_regeneration:
        recommendation = "CRITICAL: Regenerate response. Constraint or accuracy failure per LLM Judge."
    elif score.average() < 7:
        recommendation = f"LLM Judge score below 7. Review suggested."
    else:
        recommendation = "Response passed LLM Judge evaluation."

    return CriticResult(
        score=score,
        issues=[],
        recommendation=recommendation,
        needs_regeneration=needs_regeneration,
    )
