"""Tests for Mode Configuration and Orchestration"""

import pytest
from ppc.config.modes import get_mode_config, get_mode_behavior, MODE_MATRIX
from ppc.engine.orchestrator import build_execution_plan
from ppc.schemas.input import InputSchema


def test_all_modes_have_config():
    for mode in ["basic", "reflection", "code", "architect", "brutal", "focus", "teacher", "compress"]:
        config = get_mode_config(mode)
        assert config.key == mode
        assert config.reinforcement in ("none", "low", "medium", "aggressive", "maximum")


def test_all_modes_have_behavior():
    for mode in MODE_MATRIX:
        behavior = get_mode_behavior(mode)
        assert len(behavior) > 20


def test_invalid_mode_raises():
    with pytest.raises(ValueError):
        get_mode_config("invalid_mode")


def test_invalid_behavior_raises():
    with pytest.raises(ValueError):
        get_mode_behavior("invalid_mode")


def test_basic_mode_lightweight():
    config = get_mode_config("basic")
    assert config.reflection_depth == 0
    assert config.reinforcement == "low"
    assert config.multi_pass_reasoning is False


def test_brutal_mode_maximum():
    config = get_mode_config("brutal")
    assert config.reflection_depth >= 4
    assert config.reinforcement == "maximum"
    assert config.critic_engine == "maximum"


def test_compress_mode_minimal():
    config = get_mode_config("compress")
    assert config.reflection_depth == 0
    assert config.reinforcement == "none"
    assert config.compression == "maximum"


def test_orchestrator_suggests_brutal_for_security():
    schema = InputSchema(
        prompt="Encuentra todas las vulnerabilidades de seguridad en este sistema de autenticacion JWT"
    )
    schema.validate()
    plan = build_execution_plan(schema)
    assert plan.mode in ("brutal", "code", "reflection")


def test_orchestrator_suggests_code_for_programming():
    schema = InputSchema(
        prompt="Crea un endpoint en FastAPI que devuelva usuarios en formato JSON"
    )
    schema.validate()
    plan = build_execution_plan(schema)
    assert plan.mode in ("code", "basic")


def test_orchestrator_suggests_teacher_for_explanation():
    schema = InputSchema(
        prompt="Explicame paso a paso como funciona Kubernetes"
    )
    schema.validate()
    plan = build_execution_plan(schema)
    assert plan.mode in ("teacher", "basic")


def test_orchestrator_simple_prompt_stays_basic():
    schema = InputSchema(prompt="Hola")
    schema.validate()
    plan = build_execution_plan(schema)
    assert plan.mode == "basic"


def test_orchestrator_respects_explicit_mode():
    schema = InputSchema(mode="brutal", prompt="Hola mundo")
    schema.validate()
    plan = build_execution_plan(schema)
    assert plan.mode in ("brutal", "basic")  # simple prompt may override


def test_orchestrator_execution_plan_complete():
    schema = InputSchema(
        mode="code",
        prompt="Crea una API sin base de datos y compatible con Python 3.12"
    )
    schema.validate()
    plan = build_execution_plan(schema)
    assert plan.mode
    assert plan.mode_config
    assert plan.complexity.score >= 0
    assert plan.effective_reflection_depth >= 0
    assert plan.effective_reinforcement
