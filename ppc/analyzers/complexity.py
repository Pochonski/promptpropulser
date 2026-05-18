"""
Complexity Score Engine — Section 15

Computes a 0-100 complexity score from five weighted components:
constraint_count, prompt_length, ambiguity, reasoning_depth, domain_complexity.
"""

import math
from dataclasses import dataclass

from ppc.analyzers.intent import IntentResult
from ppc.analyzers.constraint import (
    DetectedConstraints,
    count_reasoning_triggers,
)
from ppc.config.thresholds import (
    COMPLEXITY_THRESHOLDS,
    CONSTRAINT_WEIGHT_MAP,
    PROMPT_LENGTH_WEIGHT_MAP,
    AMBIGUITY_WEIGHT_MAP,
    REASONING_WEIGHT_MAP,
    DOMAIN_WEIGHT_MAP,
    COMPLEXITY_COMPONENT_MAX,
)


@dataclass
class ComplexityResult:
    score: int
    classification: str
    components: dict[str, int]


def _constraint_weight(constraints: DetectedConstraints) -> int:
    total = len(constraints.locked) + len(constraints.soft)
    if total == 0:
        return 0
    if total <= 2:
        return 5
    if total <= 5:
        return 10
    if total <= 10:
        return 18
    return min(25, 18 + (total - 10))


def _prompt_length_weight(token_count: int) -> int:
    if token_count < 100:
        return 2
    if token_count <= 500:
        return 6
    if token_count <= 1500:
        return 12
    if token_count <= 3000:
        return 16
    return 20


def _ambiguity_weight(prompt: str) -> tuple[int, str]:
    prompt_lower = prompt.lower()

    indicators = 0
    vague_refs = [
        "eso", "esto", "aquello", "esa cosa", "lo mismo",
        "como antes", "igual que", "similar a",
    ]
    indicators += sum(1 for ref in vague_refs if ref in prompt_lower)

    missing_output = (
        "?" not in prompt
        and not any(kw in prompt_lower for kw in [
            "quiero que", "necesito que", "resultado", "output",
            "respuesta", "quiero", "necesito",
        ])
    )
    if missing_output:
        indicators += 2

    conflicting = sum(
        1
        for pair in [
            ("corto", "detallado"),
            ("r\u00e1pido", "profundo"),
            ("simple", "complejo"),
            ("todo", "resumen"),
        ]
        if pair[0] in prompt_lower and pair[1] in prompt_lower
    )
    indicators += conflicting * 2

    if "solo" in prompt_lower and "pero" in prompt_lower:
        indicators += 1

    if indicators <= 1:
        return (2, "low")
    if indicators <= 4:
        return (8, "medium")
    if indicators <= 7:
        return (15, "high")
    return (20, "critical")


def _reasoning_weight(intent: IntentResult) -> tuple[int, str]:
    trigger_count = count_reasoning_triggers(intent.raw_prompt)
    if intent.requires_deep_analysis:
        trigger_count += 3
    if intent.is_security_related:
        trigger_count += 2
    if intent.primary_goal in ("analyze", "design"):
        trigger_count += 2
    if trigger_count == 0:
        return (0, "none")
    if trigger_count <= 3:
        return (5, "light")
    if trigger_count <= 6:
        return (10, "medium")
    return (20, "deep")


def _domain_weight(domain: str) -> int:
    return DOMAIN_WEIGHT_MAP.get(domain, 0)


def compute_complexity(
    prompt: str,
    token_count: int,
    intent: IntentResult,
    constraints: DetectedConstraints,
) -> ComplexityResult:
    c_weight = _constraint_weight(constraints)
    p_weight = _prompt_length_weight(token_count)
    a_weight, a_level = _ambiguity_weight(prompt)
    r_weight, r_level = _reasoning_weight(intent)
    d_weight = _domain_weight(intent.domain)

    raw_score = c_weight + p_weight + a_weight + r_weight + d_weight
    normalized = min(100, raw_score)

    classification = "simple"
    for label, (low, high) in COMPLEXITY_THRESHOLDS.items():
        if low <= normalized <= high:
            classification = label
            break

    return ComplexityResult(
        score=normalized,
        classification=classification,
        components={
            "constraint_weight": c_weight,
            "prompt_length_weight": p_weight,
            "ambiguity_weight": a_weight,
            "reasoning_weight": r_weight,
            "domain_weight": d_weight,
        },
    )


def get_classification(score: int) -> str:
    for label, (low, high) in COMPLEXITY_THRESHOLDS.items():
        if low <= score <= high:
            return label
    return "simple"
