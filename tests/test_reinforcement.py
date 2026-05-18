"""Tests for Attention Reinforcement Engine"""

import pytest
from ppc.analyzers.intent import analyze_intent
from ppc.schemas.input import InputSchema
from ppc.schemas.output import DetectedConstraints
from ppc.config.modes import get_mode_config
from ppc.transformers.reinforcement import (
    apply_reinforcement,
    determine_reinforcement_level,
    count_applied_patterns,
)


def build_fixtures(prompt):
    schema = InputSchema(prompt=prompt)
    from ppc.analyzers.intent import analyze_intent
    from ppc.analyzers.constraint import detect_constraints
    return analyze_intent(schema), detect_constraints(prompt)


def test_reinforcement_adds_intro():
    intent, constraints = build_fixtures("Crea una API REST")
    mode = get_mode_config("reflection")
    result = apply_reinforcement(
        "Crea una API REST", intent, constraints, mode, "aggressive", ""
    )
    assert "PRIMARY TASK" in result


def test_reinforcement_adds_priority():
    intent, constraints = build_fixtures(
        "Haz una API sin base de datos compatible con Python 3.12"
    )
    mode = get_mode_config("focus")
    result = apply_reinforcement(
        "Haz una API sin base de datos compatible con Python 3.12",
        intent, constraints, mode, "aggressive", ""
    )
    assert "ABSOLUTE PRIORITY" in result or "PRIMARY TASK" in result


def test_maximum_adds_checklist():
    intent, constraints = build_fixtures("No uses Docker ni modifiques el frontend")
    mode = get_mode_config("brutal")
    result = apply_reinforcement(
        "No uses Docker ni modifiques el frontend",
        intent, constraints, mode, "maximum", ""
    )
    assert "PRE-RESPONSE VALIDATION" in result or "VERIFY" in result


def test_low_reinforcement_lightweight():
    intent, constraints = build_fixtures("Hola como estas")
    mode = get_mode_config("basic")
    result = apply_reinforcement(
        "Hola como estas", intent, constraints, mode, "low", ""
    )
    assert result.strip().startswith("Hola") or "PRIMARY TASK" in result


def test_determine_reinforcement_none():
    mode = get_mode_config("compress")
    level = determine_reinforcement_level(mode, 5, 0)
    assert level == "none"


def test_determine_reinforcement_maximum():
    mode = get_mode_config("brutal")
    level = determine_reinforcement_level(mode, 90, 10)
    assert level == "maximum"


def test_determine_reinforcement_aggressive_high_complexity():
    mode = get_mode_config("code")
    level = determine_reinforcement_level(mode, 75, 7)
    assert level in ("aggressive", "maximum")


def test_count_applied_patterns_max():
    patterns = count_applied_patterns("maximum")
    assert "intro_reinforcement" in patterns
    assert "anti_hallucination_check" in patterns


def test_count_applied_patterns_low():
    patterns = count_applied_patterns("low")
    assert "final_reinforcement" in patterns
    assert "anti_hallucination_check" not in patterns
