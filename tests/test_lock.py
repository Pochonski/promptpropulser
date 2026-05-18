"""Tests for Constraint Lock System"""

import pytest
from ppc.schemas.output import DetectedConstraints
from ppc.transformers.lock import apply_constraint_lock


def test_lock_disabled_does_nothing():
    constraints = DetectedConstraints(locked=["No uses Docker"])
    result = apply_constraint_lock("Haz una API", constraints, "disabled")
    assert result == "Haz una API"


def test_lock_soft_only_adds_block():
    constraints = DetectedConstraints(locked=["No uses base de datos"])
    result = apply_constraint_lock("Haz una API", constraints, "soft_only")
    assert "LOCKED CONSTRAINTS" in result
    assert "No uses base de datos" in result


def test_lock_enabled_adds_reminder():
    constraints = DetectedConstraints(locked=["No uses Docker"])
    result = apply_constraint_lock("Haz una API", constraints, "enabled")
    assert "LOCKED CONSTRAINTS" in result
    assert "REMINDER" in result


def test_lock_aggressive_repeats():
    constraints = DetectedConstraints(locked=["No uses Docker"])
    result = apply_constraint_lock("Haz una API", constraints, "aggressive")
    assert "LOCKED CONSTRAINTS" in result
    assert "REPEATED REMINDER" in result


def test_lock_maximum_has_checklist():
    constraints = DetectedConstraints(locked=["No uses Docker", "No cambies el frontend"])
    result = apply_constraint_lock("Haz una API", constraints, "maximum")
    assert "CONSTRAINT INTEGRITY CHECK" in result
    assert "BEFORE RESPONDING" in result or "VERIFY" in result


def test_lock_preserves_original_prompt():
    constraints = DetectedConstraints(locked=["No uses Docker"])
    result = apply_constraint_lock("Haz una API en FastAPI", constraints, "enabled")
    assert "Haz una API en FastAPI" in result


def test_lock_with_soft_constraints():
    constraints = DetectedConstraints(
        locked=["No uses Docker"],
        soft=["Preferiblemente usa TypeScript"]
    )
    result = apply_constraint_lock("Haz una API", constraints, "soft_only")
    assert "PREFERRED GUIDELINES" in result


def test_no_constraints_no_changes():
    constraints = DetectedConstraints()
    result = apply_constraint_lock("Haz una API", constraints, "aggressive")
    assert result == "Haz una API"
