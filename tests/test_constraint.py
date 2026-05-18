"""Tests for Constraint Detection Engine"""

import pytest
from ppc.analyzers.constraint import (
    detect_constraints,
    has_compression_trigger,
    has_deep_analysis_trigger,
    has_security_trigger,
    has_teaching_trigger,
    has_code_trigger,
)


def test_detect_hard_constraint_no_uses():
    result = detect_constraints("Haz una API pero no uses base de datos")
    assert len(result.locked) >= 1


def test_detect_hard_constraint_obligatorio():
    result = detect_constraints("Es obligatorio usar Python 3.12")
    assert len(result.locked) >= 1


def test_detect_hard_constraint_manten():
    result = detect_constraints("Manten la arquitectura actual sin cambios")
    assert len(result.locked) >= 1


def test_detect_hard_constraint_no_cambies():
    result = detect_constraints("No cambies el frontend bajo ninguna circunstancia")
    assert len(result.locked) >= 1


def test_detect_hard_constraint_solo_usa():
    result = detect_constraints("Solo usa PostgreSQL como base de datos")
    assert len(result.locked) >= 1


def test_detect_soft_constraint_preferiblemente():
    result = detect_constraints("Preferiblemente usa TypeScript pero no es obligatorio")
    assert len(result.soft) >= 1


def test_detect_soft_constraint_si_puedes():
    result = detect_constraints("Si puedes, agrega tests unitarios")
    assert len(result.soft) >= 1


def test_no_false_positive():
    result = detect_constraints("Cual es la capital de Francia?")
    assert len(result.locked) == 0


def test_multiple_constraints():
    result = detect_constraints(
        "No uses Docker, no cambies el frontend, y debe ser compatible con Python 3.12"
    )
    assert len(result.locked) >= 2


def test_constraint_types_detected():
    result = detect_constraints(
        "No uses Docker y debe ser compatible con Python 3.12"
    )
    assert len(result.detected_types) >= 1


def test_compression_trigger():
    assert has_compression_trigger("Dame un resumen rapido y breve") is True


def test_deep_analysis_trigger():
    assert has_deep_analysis_trigger("Analiza profundamente este codigo") is True


def test_security_trigger():
    assert has_security_trigger("Encuentra vulnerabilidades en este sistema") is True


def test_teaching_trigger():
    assert has_teaching_trigger("Explicame paso a paso como funciona React") is True


def test_code_trigger():
    assert has_code_trigger("Crea un API endpoint en FastAPI") is True
