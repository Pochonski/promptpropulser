"""Tests for Semantic Echo Generator"""

import pytest
from ppc.schemas.output import DetectedConstraints
from ppc.transformers.echo import generate_echo, generate_echoes


def test_echo_negative_constraint():
    echo = generate_echo("No uses React")
    assert "React" in echo
    assert len(echo) > 10


def test_echo_positive_constraint():
    echo = generate_echo("Debe usar PostgreSQL")
    assert "PostgreSQL" in echo
    assert len(echo) > 10


def test_echo_variation():
    e1 = generate_echo("No uses Docker", variation=0)
    e2 = generate_echo("No uses Docker", variation=1)
    assert e1 != e2


def test_generate_echoes_none():
    constraints = DetectedConstraints(locked=["No uses React"])
    echoes = generate_echoes(constraints, "none")
    assert echoes == []


def test_generate_echoes_low():
    constraints = DetectedConstraints(locked=["No uses Docker", "No uses React"])
    echoes = generate_echoes(constraints, "low")
    assert len(echoes) > 0


def test_generate_echoes_aggressive():
    constraints = DetectedConstraints(locked=["No uses Docker"], soft=["Usa TypeScript"])
    echoes = generate_echoes(constraints, "aggressive")
    assert len(echoes) > 0


def test_generate_echoes_maximum():
    constraints = DetectedConstraints(
        locked=["No uses Docker", "No cambies el frontend"],
        soft=["Preferiblemente usa PostgreSQL"]
    )
    echoes = generate_echoes(constraints, "maximum")
    assert len(echoes) > 0


def test_echoes_no_duplicates():
    constraints = DetectedConstraints(locked=["No uses React"])
    echoes = generate_echoes(constraints, "maximum")
    assert len(echoes) == len(set(echoes))


def test_empty_constraints_no_echo():
    constraints = DetectedConstraints()
    echoes = generate_echoes(constraints, "aggressive")
    assert echoes == []
