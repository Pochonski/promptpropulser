"""Tests for Intent Analyzer"""

import pytest
from ppc.schemas.input import InputSchema
from ppc.analyzers.intent import analyze_intent


def test_detect_create_goal():
    schema = InputSchema(prompt="Crea una API REST con FastAPI")
    result = analyze_intent(schema)
    assert result.primary_goal == "create"


def test_detect_explain_goal():
    schema = InputSchema(prompt="Explicame como funciona el garbage collector")
    result = analyze_intent(schema)
    assert result.primary_goal == "explain"


def test_detect_fix_goal():
    schema = InputSchema(prompt="Arregla este bug en el codigo")
    result = analyze_intent(schema)
    assert result.primary_goal == "fix"


def test_detect_analyze_goal():
    schema = InputSchema(prompt="Analiza la seguridad de este sistema")
    result = analyze_intent(schema)
    assert result.primary_goal == "analyze"


def test_detect_design_goal():
    schema = InputSchema(prompt="Disena una arquitectura de microservicios")
    result = analyze_intent(schema)
    assert result.primary_goal == "design"


def test_code_related():
    schema = InputSchema(prompt="Haz una funcion en Python")
    result = analyze_intent(schema)
    assert result.is_code_related is True


def test_security_related():
    schema = InputSchema(prompt="Audita la seguridad del JWT")
    result = analyze_intent(schema)
    assert result.is_security_related is True


def test_teaching_related():
    schema = InputSchema(prompt="Explicame paso a paso como usar Docker")
    result = analyze_intent(schema)
    assert result.is_teaching_related is True


def test_domain_coding():
    schema = InputSchema(prompt="Crea un endpoint en FastAPI con Python")
    result = analyze_intent(schema)
    assert result.domain == "coding"


def test_domain_casual():
    schema = InputSchema(prompt="Hola, como estas?")
    result = analyze_intent(schema)
    assert result.domain == "casual_chat"
