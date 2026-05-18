"""Tests for LLM-as-Judge critic"""

import pytest
from unittest.mock import MagicMock, patch

from ppc.schemas.output import DetectedConstraints
from ppc.schemas.session_log import CriticScore
from ppc.integration.base import LLMResponse
from ppc.critic_llm import (
    llm_evaluate_response,
    _build_judge_prompt,
    _parse_judge_response,
    JUDGE_SYSTEM_PROMPT,
    JUDGE_PROMPT_TEMPLATE,
)


@pytest.fixture
def mock_judge_client():
    client = MagicMock()
    client.model = "claude-haiku-4-5-20251001"

    def make_response(text):
        return LLMResponse(
            text=text,
            input_tokens=100,
            output_tokens=30,
            stop_reason="end_turn",
            model="claude-haiku-4-5-20251001",
        )

    client.generate.return_value = make_response(
        '{"constraint_adherence": 10, "clarity": 9, "accuracy": 10, "efficiency": 9}'
    )
    client.count_tokens.return_value = 10
    return client


def test_parse_judge_response_valid():
    text = '{"constraint_adherence": 9, "clarity": 8, "accuracy": 10, "efficiency": 7}'
    result = _parse_judge_response(text)
    assert result is not None
    assert result["constraint_adherence"] == 9
    assert result["clarity"] == 8
    assert result["accuracy"] == 10
    assert result["efficiency"] == 7


def test_parse_judge_response_clamped():
    text = '{"constraint_adherence": 15, "clarity": -1, "accuracy": 5, "efficiency": 0}'
    result = _parse_judge_response(text)
    assert result["constraint_adherence"] == 10
    assert result["clarity"] == 1
    assert result["efficiency"] == 1


def test_parse_judge_response_invalid():
    result = _parse_judge_response("not json at all")
    assert result is None


def test_parse_judge_response_missing_keys():
    result = _parse_judge_response('{"constraint_adherence": 5}')
    assert result is None


def test_parse_judge_response_json_in_text():
    text = 'Here is my evaluation: {"constraint_adherence": 8, "clarity": 7, "accuracy": 9, "efficiency": 8}'
    result = _parse_judge_response(text)
    assert result is not None
    assert result["constraint_adherence"] == 8


def test_build_judge_prompt():
    constraints = DetectedConstraints(locked=["No uses Docker", "Compatible con Python 3.12"])
    prompt = _build_judge_prompt(
        "Haz una API en FastAPI",
        constraints,
        "Aqui tienes la API en EC2 sin Docker",
    )
    assert "Haz una API en FastAPI" in prompt
    assert "No uses Docker" in prompt
    assert "Compatible con Python 3.12" in prompt
    assert "Aqui tienes la API" in prompt


def test_build_judge_prompt_no_constraints():
    constraints = DetectedConstraints()
    prompt = _build_judge_prompt(
        "Hola mundo",
        constraints,
        "Hola!",
    )
    assert "no locked constraints" in prompt.lower()


def test_llm_evaluate_empty_response(mock_judge_client):
    result = llm_evaluate_response(
        "", "Hola", DetectedConstraints(), mock_judge_client,
    )
    assert result.needs_regeneration is True
    assert result.score.constraint_following == 0


def test_llm_evaluate_good_response(mock_judge_client):
    constraints = DetectedConstraints(locked=["Usa FastAPI"])
    result = llm_evaluate_response(
        "Aqui tienes una API en FastAPI con endpoints REST bien documentados",
        "Haz una API en FastAPI",
        constraints,
        mock_judge_client,
    )
    assert result.score.constraint_following >= 5
    assert result.score.clarity >= 5
    assert result.needs_regeneration is False


def test_llm_evaluate_understands_negation(mock_judge_client):
    mock_judge_client.generate.return_value = LLMResponse(
        text='{"constraint_adherence": 10, "clarity": 9, "accuracy": 10, "efficiency": 10}',
        input_tokens=100,
        output_tokens=30,
        stop_reason="end_turn",
        model="haiku",
    )
    constraints = DetectedConstraints(locked=["No uses Docker"])
    result = llm_evaluate_response(
        "Desplegamos en EC2 con systemd, SIN Docker. No hay contenedores de ningun tipo.",
        "Despliega sin Docker",
        constraints,
        mock_judge_client,
    )
    assert result.score.constraint_following >= 8


def test_llm_evaluate_low_score_triggers_regeneration(mock_judge_client):
    mock_judge_client.generate.return_value = LLMResponse(
        text='{"constraint_adherence": 2, "clarity": 5, "accuracy": 5, "efficiency": 5}',
        input_tokens=100,
        output_tokens=30,
        stop_reason="end_turn",
        model="haiku",
    )
    constraints = DetectedConstraints(locked=["No uses base de datos"])
    result = llm_evaluate_response(
        "Usa SQLAlchemy con PostgreSQL",
        "Haz una API sin base de datos",
        constraints,
        mock_judge_client,
    )
    assert result.needs_regeneration is True


def test_llm_evaluate_fallback_on_bad_json(mock_judge_client):
    mock_judge_client.generate.return_value = LLMResponse(
        text="I think it's good",
        input_tokens=100,
        output_tokens=10,
        stop_reason="end_turn",
        model="haiku",
    )
    constraints = DetectedConstraints()
    result = llm_evaluate_response(
        "Some response here",
        "Original prompt",
        constraints,
        mock_judge_client,
    )
    assert result.score.constraint_following >= 0
    assert "JSON parse failed" in str(result.issues)


def test_llm_evaluate_model_restored_after_error(mock_judge_client):
    original_model = mock_judge_client.model
    mock_judge_client.generate.side_effect = Exception("API error")
    constraints = DetectedConstraints()
    result = llm_evaluate_response(
        "Some response",
        "Original prompt",
        constraints,
        mock_judge_client,
    )
    assert mock_judge_client.model == original_model
    assert "LLM Judge fallback" in str(result.issues)
