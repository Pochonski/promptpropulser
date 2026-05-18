"""Tests for Full Pipeline Execution"""

import pytest
from ppc.schemas.input import InputSchema, InputOptions
from ppc.engine.pipeline import run_pipeline


def test_pipeline_basic():
    schema = InputSchema(prompt="Hola mundo")
    schema.validate()
    output = run_pipeline(schema)
    assert output.optimized_prompt
    assert output.analyzed_intent.primary_goal != ""
    assert output.token_usage.input_tokens > 0


def test_pipeline_code_mode():
    schema = InputSchema(
        mode="code",
        prompt="Crea una API en FastAPI sin base de datos compatible con Python 3.12",
    )
    schema.validate()
    output = run_pipeline(schema)
    assert output.optimized_prompt
    assert len(output.constraints.locked) >= 1


def test_pipeline_brutal_mode():
    schema = InputSchema(
        mode="brutal",
        prompt="Audita la seguridad de este sistema JWT y encuentra todas las vulnerabilidades",
    )
    schema.validate()
    output = run_pipeline(schema)
    assert output.optimized_prompt


def test_pipeline_reflection_mode():
    schema = InputSchema(
        mode="reflection",
        prompt="Analiza si esta arquitectura de microservicios tiene cuellos de botella",
    )
    schema.validate()
    output = run_pipeline(schema)
    assert output.reflection.enabled is True


def test_pipeline_compress_mode():
    schema = InputSchema(
        mode="compress",
        prompt=(
            "Necesito que me ayudes a crear un sistema y me gustaria que "
            "fuera muy completo con muchas funcionalidades " * 20
        ),
    )
    schema.validate()
    output = run_pipeline(schema)
    assert output.optimized_prompt


def test_pipeline_output_schema_complete():
    schema = InputSchema(mode="code", prompt="Haz una funcion en Python sin usar librerias externas")
    schema.validate()
    output = run_pipeline(schema)

    assert output.analyzed_intent.primary_goal
    assert isinstance(output.constraints.locked, list)
    assert isinstance(output.reinforcement.applied_patterns, list)
    assert isinstance(output.optimized_prompt, str)
    assert output.token_usage.final_prompt_tokens > 0


def test_pipeline_output_to_dict():
    schema = InputSchema(prompt="Hola")
    schema.validate()
    output = run_pipeline(schema)
    d = output.to_dict()
    assert "optimized_prompt" in d
    assert "analyzed_intent" in d
    assert "token_usage" in d


def test_pipeline_token_counting():
    schema = InputSchema(prompt="Hola mundo, como estas?")
    schema.validate()
    output = run_pipeline(schema)
    assert output.token_usage.input_tokens > 0
    assert output.token_usage.final_prompt_tokens > 0


def test_pipeline_invalid_mode_raises():
    schema = InputSchema(mode="invalid", prompt="test")
    with pytest.raises(ValueError):
        schema.validate()
