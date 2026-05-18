"""Tests for Critic Engine"""

import pytest
from ppc.schemas.output import DetectedConstraints
from ppc.reflection.critic import evaluate_response


def test_empty_response_fails():
    constraints = DetectedConstraints()
    result = evaluate_response("", "Hola", "Hola", constraints)
    assert result.needs_regeneration is True


def test_good_response_passes():
    constraints = DetectedConstraints(locked=["Usa FastAPI"])
    result = evaluate_response(
        "Aqui tienes una API en FastAPI con endpoints REST",
        "Haz una API en FastAPI",
        "Haz una API en FastAPI",
        constraints,
    )
    assert result.score.constraint_following >= 5


def test_constraint_violation_lowers_score():
    constraints = DetectedConstraints(locked=["No uses base de datos"])
    result = evaluate_response(
        "Usa SQLAlchemy para conectar a PostgreSQL",
        "Haz una API sin base de datos",
        "Haz una API sin base de datos",
        constraints,
    )
    assert result.score.constraint_following <= 8


def test_long_response_flags_efficiency():
    constraints = DetectedConstraints()
    long_text = "palabra " * 2001
    result = evaluate_response(
        long_text, "Cuentame algo", "Cuentame algo", constraints
    )
    assert result.score.efficiency <= 8


def test_critic_score_total():
    from ppc.schemas.session_log import CriticScore
    score = CriticScore(8, 7, 9, 6)
    assert score.total() == 30
    assert score.average() == 7.5


def test_critic_is_critical_failure():
    from ppc.schemas.session_log import CriticScore
    assert CriticScore(constraint_following=2, clarity=8, accuracy=8, efficiency=8).is_critical_failure() is True
    assert CriticScore(constraint_following=8, clarity=8, accuracy=8, efficiency=8).is_critical_failure() is False
