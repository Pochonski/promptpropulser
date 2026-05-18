"""
Semantic Echo Generator — Section 4

Reformulates constraints semantically instead of repeating
verbatim. Increases contextual activation without redundancy.
"""

import random

from ppc.schemas.output import DetectedConstraints


ECHO_TEMPLATES: list[str] = [
    "Do not include or use {constraint} in any way.",
    "The solution must avoid {constraint} entirely.",
    "Ensure no dependency on {constraint}.",
    "Any use of {constraint} is prohibited.",
    "The answer must be free of {constraint}.",
    "Steer clear of {constraint} in the response.",
    "Under no circumstances should {constraint} appear.",
    "Exclude {constraint} from the final output.",
    "The response must not rely on {constraint}.",
    "Avoid frameworks, libraries, or tools related to {constraint}.",
]


POSITIVE_ECHO_TEMPLATES: list[str] = [
    "The solution must use {constraint}.",
    "Ensure compatibility with {constraint}.",
    "The response must incorporate {constraint}.",
    "Build the solution around {constraint}.",
    "Make {constraint} a core requirement.",
    "The answer should be built with {constraint}.",
    "Prioritize {constraint} in the implementation.",
    "Anchor the solution on {constraint}.",
    "Use {constraint} as the foundational technology.",
    "The output must adhere to {constraint}.",
]


NEGATIVE_PATTERNS: list[str] = [
    "no uses", "no usar", "no utilices", "sin usar", "sin utilizar",
    "evita", "evitar", "evite", "prohibido", "prohibida",
    "nunca", "jam\u00e1s", "no cambies", "no modifiques", "no alteres",
    "no agregues", "no a\u00f1adas", "no incluyas", "sin", "no",
]


def _is_negative_constraint(text: str) -> bool:
    text_lower = text.lower()
    return any(pat in text_lower for pat in NEGATIVE_PATTERNS)


def _extract_subject(constraint: str) -> str:
    subjects = []
    constraint_lower = constraint.lower()
    for pat in NEGATIVE_PATTERNS:
        idx = constraint_lower.find(pat)
        if idx >= 0:
            remainder = constraint[idx + len(pat):].strip()
            if remainder:
                subjects.append(remainder)
    if not subjects:
        subjects.append(constraint)
    return subjects[0] if subjects else constraint


def generate_echo(constraint: str, variation: int = 0) -> str:
    is_negative = _is_negative_constraint(constraint)
    subject = _extract_subject(constraint)

    if is_negative:
        templates = ECHO_TEMPLATES
    else:
        templates = POSITIVE_ECHO_TEMPLATES

    idx = variation % len(templates)
    return templates[idx].format(constraint=subject)


def generate_echoes(
    constraints: DetectedConstraints,
    echo_intensity: str,
) -> list[str]:
    """
    echo_intensity: "none" | "low" | "medium" | "aggressive" | "maximum"
    """
    if echo_intensity == "none":
        return []

    targets = constraints.locked.copy()
    if echo_intensity in ("medium", "aggressive", "maximum"):
        targets += constraints.soft

    if not targets:
        return []

    count_map = {
        "low": 1,
        "medium": 1,
        "aggressive": 2,
        "maximum": 3,
    }
    echo_count = count_map.get(echo_intensity, 1)

    echoes: list[str] = []
    for i, constraint in enumerate(targets):
        for v in range(echo_count):
            echo = generate_echo(constraint, variation=i + v)
            if echo not in echoes:
                echoes.append(echo)

    return echoes
