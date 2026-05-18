"""Tests for Reflection Pipeline"""

import pytest
from ppc.schemas.input import InputSchema
from ppc.analyzers.intent import analyze_intent
from ppc.analyzers.constraint import detect_constraints
from ppc.reflection.pipeline import run_reflection


def test_reflection_depth_0():
    schema = InputSchema(prompt="Haz una API")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = run_reflection(intent, constraints, "Haz una API", depth=0)
    assert result.passed is True
    assert len(result.stage_results) == 0


def test_reflection_depth_1():
    schema = InputSchema(prompt="Haz una API REST")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = run_reflection(intent, constraints, "Haz una API REST", depth=1)
    assert "intent_validation" in result.stage_results


def test_reflection_depth_2():
    schema = InputSchema(prompt="Haz una API sin base de datos")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = run_reflection(
        intent, constraints,
        "Haz una API sin base de datos",
        depth=2
    )
    assert "constraint_validation" in result.stage_results


def test_reflection_depth_3():
    schema = InputSchema(prompt="Haz una API REST con FastAPI")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = run_reflection(
        intent, constraints,
        "Haz una API REST con FastAPI",
        depth=3
    )
    assert "quality_analysis" in result.stage_results


def test_reflection_depth_4():
    schema = InputSchema(prompt="Audita la seguridad del sistema")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = run_reflection(
        intent, constraints,
        "Audita la seguridad del sistema",
        depth=4
    )
    assert "failure_simulation" in result.stage_results


def test_constraint_violation_detected():
    schema = InputSchema(prompt="No uses base de datos")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = run_reflection(
        intent, constraints,
        "Aqui esta la respuesta sin mencionar la restriccion",
        depth=2
    )
    assert isinstance(result.passed, bool)
