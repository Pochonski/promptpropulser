"""Tests for Self-Improvement Loop"""

import pytest
from unittest.mock import MagicMock, patch

from ppc.schemas.input import InputSchema
from ppc.integration.base import LLMResponse
from ppc.loop import run_once, run_until_pass


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.model_name = "claude-mock"

    def make_response(text, tokens=50):
        return LLMResponse(
            text=text,
            input_tokens=tokens,
            output_tokens=len(text.split()),
            stop_reason="end_turn",
            model="claude-mock",
        )

    client.generate.return_value = make_response("def hello(): return 'world'")
    client.count_tokens.return_value = 10
    return client


def test_run_once_basic(mock_client):
    schema = InputSchema(prompt="Crea una funcion de saludo en Python")
    result = run_once(schema, mock_client)

    assert result.attempts == 1
    assert result.final_response
    assert result.session_log.original_prompt == "Crea una funcion de saludo en Python"
    assert result.session_log.llm_output_v1
    assert result.all_critic_scores


def test_run_once_with_system_prompt(mock_client):
    schema = InputSchema(prompt="Hola")
    result = run_once(schema, mock_client, system_prompt="Eres util")
    assert result.final_response


def test_run_once_session_log_has_scores(mock_client):
    schema = InputSchema(prompt="Haz una API sin base de datos")
    result = run_once(schema, mock_client)

    cs = result.session_log.critic_score
    assert 0 <= cs.constraint_following <= 10
    assert 0 <= cs.clarity <= 10
    assert 0 <= cs.accuracy <= 10
    assert 0 <= cs.efficiency <= 10


def test_run_once_passes_for_good_response(mock_client):
    mock_client.generate.return_value = LLMResponse(
        text="Aqui tienes una API en FastAPI pura, sin ORM ni base de datos. "
             "Usa almacenamiento en memoria con diccionarios Python.",
        input_tokens=20,
        output_tokens=25,
        stop_reason="end_turn",
        model="claude-mock",
    )
    schema = InputSchema(prompt="Haz una API sin base de datos")
    result = run_once(schema, mock_client)
    assert isinstance(result.passed_critic, bool)


def test_run_until_pass_single_attempt(mock_client):
    mock_client.generate.return_value = LLMResponse(
        text="Aqui tienes el codigo solicitado en Python puro.",
        input_tokens=10,
        output_tokens=8,
        stop_reason="end_turn",
        model="claude-mock",
    )
    schema = InputSchema(prompt="Escribe codigo Python simple")
    result = run_until_pass(schema, mock_client, max_retries=3)

    assert result.attempts >= 1
    assert result.final_response
    assert len(result.all_critic_scores) >= 1


def test_run_until_pass_llm_error_handled(mock_client):
    mock_client.generate.side_effect = Exception("API connection error")
    schema = InputSchema(prompt="Test prompt")
    result = run_until_pass(schema, mock_client, max_retries=2)

    assert "[LLM ERROR" in result.final_response


def test_loop_result_attributes(mock_client):
    schema = InputSchema(mode="code", prompt="Crea una funcion Python")
    result = run_once(schema, mock_client)

    assert hasattr(result, "session_log")
    assert hasattr(result, "final_response")
    assert hasattr(result, "attempts")
    assert hasattr(result, "passed_critic")
    assert hasattr(result, "all_critic_scores")


def test_session_log_session_id_unique(mock_client):
    schema1 = InputSchema(prompt="Prompt A")
    r1 = run_once(schema1, mock_client)

    schema2 = InputSchema(prompt="Prompt B")
    r2 = run_once(schema2, mock_client)

    assert r1.session_log.session_id != r2.session_log.session_id


@pytest.fixture
def mock_judge_client():
    client = MagicMock()
    client.model = "claude-haiku-4-5-20251001"
    client.model_name = "claude-haiku-mock"

    def make_response(text):
        return LLMResponse(
            text=text,
            input_tokens=50,
            output_tokens=20,
            stop_reason="end_turn",
            model="claude-haiku-mock",
        )

    client.generate.return_value = make_response(
        '{"constraint_adherence": 9, "clarity": 8, "accuracy": 10, "efficiency": 9}'
    )
    client.count_tokens.return_value = 10
    return client


def test_run_once_with_judge(mock_client, mock_judge_client):
    schema = InputSchema(prompt="Crea una funcion Python")
    result = run_once(schema, mock_client, judge_client=mock_judge_client)

    assert result.attempts == 1
    assert result.final_response
    assert result.all_critic_scores


def test_run_until_pass_with_judge(mock_client, mock_judge_client):
    mock_client.generate.return_value = LLMResponse(
        text="Codigo Python correcto y bien documentado",
        input_tokens=5,
        output_tokens=5,
        stop_reason="end_turn",
        model="claude-mock",
    )
    schema = InputSchema(prompt="Escribe codigo simple")
    result = run_until_pass(schema, mock_client, max_retries=2, judge_client=mock_judge_client)

    assert result.final_response
    assert len(result.all_critic_scores) >= 1


def test_judge_scores_different_from_keyword(mock_client, mock_judge_client):
    mock_client.generate.return_value = LLMResponse(
        text="def hello(): return 'Hola'",
        input_tokens=5,
        output_tokens=5,
        stop_reason="end_turn",
        model="mock",
    )
    schema = InputSchema(prompt="Haz una funcion en Python")

    result_kw = run_once(schema, mock_client)
    result_judge = run_once(schema, mock_client, judge_client=mock_judge_client)

    assert result_kw.all_critic_scores
    assert result_judge.all_critic_scores
