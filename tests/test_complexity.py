"""Tests for Complexity Score Engine"""

import pytest
from ppc.schemas.input import InputSchema
from ppc.analyzers.intent import analyze_intent
from ppc.analyzers.constraint import detect_constraints
from ppc.analyzers.complexity import compute_complexity, get_classification


def test_simple_prompt():
    schema = InputSchema(prompt="Hola")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = compute_complexity(schema.prompt, 1, intent, constraints)
    assert result.classification == "simple"
    assert result.score <= 20


def test_medium_complexity():
    schema = InputSchema(prompt="Crea una API en FastAPI sin base de datos")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = compute_complexity(schema.prompt, 12, intent, constraints)
    assert result.classification in ("simple", "medium")


def test_complex_security_prompt():
    schema = InputSchema(
        prompt="Analiza la seguridad del sistema JWT, encuentra vulnerabilidades, "
               "revisa el cifrado, y audita los permisos. No uses herramientas externas."
    )
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = compute_complexity(schema.prompt, 30, intent, constraints)
    assert result.score > 0


def test_components_present():
    schema = InputSchema(prompt="Disena una arquitectura de microservicios escalable")
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = compute_complexity(schema.prompt, 10, intent, constraints)
    assert "constraint_weight" in result.components
    assert "prompt_length_weight" in result.components
    assert "ambiguity_weight" in result.components
    assert "reasoning_weight" in result.components
    assert "domain_weight" in result.components


def test_classification_simple():
    assert get_classification(10) == "simple"
    assert get_classification(20) == "simple"


def test_classification_medium():
    assert get_classification(35) == "medium"
    assert get_classification(50) == "medium"


def test_classification_complex():
    assert get_classification(65) == "complex"
    assert get_classification(80) == "complex"


def test_classification_critical():
    assert get_classification(90) == "critical"
    assert get_classification(100) == "critical"


def test_security_domain_weights_high():
    schema = InputSchema(
        prompt="Audita la seguridad del sistema JWT con refresh tokens y encuentra "
               "todas las vulnerabilidades posibles"
    )
    intent = analyze_intent(schema)
    constraints = detect_constraints(schema.prompt)
    result = compute_complexity(schema.prompt, 20, intent, constraints)
    assert result.components["domain_weight"] >= 10
