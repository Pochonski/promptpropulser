"""
Constraint Detection Engine — Section 3

Classifies constraints as HARD (locked) or SOFT using
pattern heuristics from config/heuristics.py.
"""

import re
from dataclasses import dataclass, field

from ppc.config.heuristics import (
    HARD_CONSTRAINT_TRIGGERS,
    SOFT_CONSTRAINT_TRIGGERS,
    CONSTRAINT_TYPE_LABELS,
    TECH_TRIGGERS,
    COMPRESSION_TRIGGERS,
    DEEP_ANALYSIS_TRIGGERS,
    SECURITY_BRUTAL_TRIGGERS,
    TEACHING_TRIGGERS,
    CODE_TRIGGERS,
    REASONING_DEPTH_TRIGGERS,
    TriggerPattern,
)
from ppc.schemas.output import DetectedConstraints


@dataclass
class ConstraintMatch:
    text: str
    is_hard: bool
    pattern: str
    confidence: float
    constraint_type: str = ""


def _match_triggers(
    prompt: str,
    patterns: list[TriggerPattern],
) -> list[ConstraintMatch]:
    prompt_lower = prompt.lower()
    matches: list[ConstraintMatch] = []

    for pattern in patterns:
        for kw in pattern.keywords:
            if kw.lower() in prompt_lower:
                context = _extract_constraint_context(prompt_lower, kw)
                if context:
                    matches.append(
                        ConstraintMatch(
                            text=context,
                            is_hard=True,  # set by caller
                            pattern=kw,
                            confidence=min(pattern.weight / 3.0, 1.0),
                        )
                    )
                    break

    return matches


def _split_into_clauses(text: str) -> list[str]:
    clauses = re.split(r"[,;]\s*|(?<=\s)y\s+|(?<=\s)e\s+", text)
    return [c.strip() for c in clauses if c.strip()]


def _extract_constraint_context(text: str, keyword: str) -> str:
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return ""
    sentences = re.split(r"[.!?\n]", text)
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            return sentence.strip()
    start = max(0, idx - 30)
    end = min(len(text), idx + len(keyword) + 80)
    return text[start:end].strip()


def _classify_constraint_type(constraint_text: str) -> str:
    text_lower = constraint_text.lower()
    for tech_kw in TECH_TRIGGERS:
        if tech_kw.lower() in text_lower:
            return "technological"
    if any(kw in text_lower for kw in ["formato", "format", "json", "xml", "markdown", "yaml"]):
        return "format"
    if any(kw in text_lower for kw in ["corto", "breve", "largo", "extenso",
                                         "palabras", "words", "caracteres", "characters"]):
        return "length"
    if any(kw in text_lower for kw in ["compatible", "compatibility", "python 3", "node",
                                         "versi\u00f3n", "version"]):
        return "compatibility"
    if any(kw in text_lower for kw in ["estilo", "style", "tono", "tone", "formal", "informal"]):
        return "style"
    if any(kw in text_lower for kw in ["seguridad", "security", "seguro", "vulnerab"]):
        return "security"
    if any(kw in text_lower for kw in ["arquitectura", "architecture", "estructura",
                                         "modular", "component"]):
        return "architecture"
    return "structural"


def _has_soft_trigger_in_clause(clause: str) -> bool:
    clause_lower = clause.lower()
    for pattern in SOFT_CONSTRAINT_TRIGGERS:
        if any(kw in clause_lower for kw in pattern.keywords):
            return True
    return False


def detect_constraints(prompt: str) -> DetectedConstraints:
    locked: list[str] = []
    soft: list[str] = []
    detected_types: set[str] = set()

    clauses = _split_into_clauses(prompt)

    for clause in clauses:
        if not clause.strip():
            continue

        is_soft = _has_soft_trigger_in_clause(clause)

        if not is_soft:
            hard_matches = _match_triggers(clause, HARD_CONSTRAINT_TRIGGERS)
            for match in hard_matches:
                constraint_text = match.text.strip()
                if constraint_text and constraint_text not in locked:
                    locked.append(constraint_text)
                    ctype = _classify_constraint_type(constraint_text)
                    detected_types.add(ctype)

        soft_matches = _match_triggers(clause, SOFT_CONSTRAINT_TRIGGERS)
        for match in soft_matches:
            constraint_text = match.text.strip()
            if (
                constraint_text
                and constraint_text not in locked
                and constraint_text not in soft
            ):
                soft.append(constraint_text)
                ctype = _classify_constraint_type(constraint_text)
                detected_types.add(ctype)

    if not locked and not soft:
        hard_matches = _match_triggers(prompt, HARD_CONSTRAINT_TRIGGERS)
        for match in hard_matches:
            constraint_text = match.text.strip()
            if constraint_text and constraint_text not in locked:
                locked.append(constraint_text)
                ctype = _classify_constraint_type(constraint_text)
                detected_types.add(ctype)

        soft_matches = _match_triggers(prompt, SOFT_CONSTRAINT_TRIGGERS)
        for match in soft_matches:
            constraint_text = match.text.strip()
            if (
                constraint_text
                and constraint_text not in locked
                and constraint_text not in soft
            ):
                soft.append(constraint_text)
                ctype = _classify_constraint_type(constraint_text)
                detected_types.add(ctype)

    return DetectedConstraints(
        locked=locked,
        soft=soft,
        detected_types=sorted(detected_types),
    )


def has_compression_trigger(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    for pattern in COMPRESSION_TRIGGERS:
        if any(kw in prompt_lower for kw in pattern.keywords):
            return True
    return False


def has_deep_analysis_trigger(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    for pattern in DEEP_ANALYSIS_TRIGGERS:
        if any(kw in prompt_lower for kw in pattern.keywords):
            return True
    return False


def has_security_trigger(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    for pattern in SECURITY_BRUTAL_TRIGGERS:
        if any(kw in prompt_lower for kw in pattern.keywords):
            return True
    return False


def has_teaching_trigger(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    for pattern in TEACHING_TRIGGERS:
        if any(kw in prompt_lower for kw in pattern.keywords):
            return True
    return False


def has_code_trigger(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    for pattern in CODE_TRIGGERS:
        if any(kw in prompt_lower for kw in pattern.keywords):
            return True
    return False


def count_reasoning_triggers(prompt: str) -> int:
    prompt_lower = prompt.lower()
    count = 0
    for pattern in REASONING_DEPTH_TRIGGERS:
        if any(kw in prompt_lower for kw in pattern.keywords):
            count += 1
    return count
