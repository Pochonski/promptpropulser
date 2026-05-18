"""Tests for Anthropic Integration"""

import pytest
from unittest.mock import MagicMock, patch

from ppc.integration.base import LLMResponse
from ppc.integration.anthropic import AnthropicClient, DEFAULT_MODEL


def _make_mock_client():
    mock_client = MagicMock()

    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = "Hello from Claude"
    mock_message.usage.input_tokens = 50
    mock_message.usage.output_tokens = 100
    mock_message.stop_reason = "end_turn"
    mock_message.model = "claude-sonnet-4-20250514"

    mock_token_result = MagicMock()
    mock_token_result.input_tokens = 25

    mock_client.messages.create.return_value = mock_message
    mock_client.messages.count_tokens.return_value = mock_token_result
    return mock_client


@pytest.fixture
def mock_client():
    mock = _make_mock_client()
    with patch.object(AnthropicClient, "_get_client", return_value=mock):
        yield mock


def test_client_creation(mock_client):
    client = AnthropicClient(api_key="sk-test-key")
    assert client.model == DEFAULT_MODEL
    assert client.api_key == "sk-test-key"


def test_generate_response(mock_client):
    client = AnthropicClient(api_key="sk-test-key")
    response = client.generate("Hello Claude")

    assert response.text == "Hello from Claude"
    assert response.input_tokens == 50
    assert response.output_tokens == 100
    assert response.stop_reason == "end_turn"


def test_generate_with_system_prompt(mock_client):
    client = AnthropicClient(api_key="sk-test-key")
    response = client.generate(
        "Hello",
        system_prompt="You are a helpful assistant",
    )

    assert response.text == "Hello from Claude"


def test_generate_with_temperature(mock_client):
    client = AnthropicClient(api_key="sk-test-key")
    response = client.generate("Hello", temperature=0.3)
    assert response.text


def test_count_tokens(mock_client):
    client = AnthropicClient(api_key="sk-test-key")
    tokens = client.count_tokens("Hello world")
    assert tokens == 25


def test_model_name():
    client = AnthropicClient(api_key="sk-test-key", model="claude-opus-4-20250514")
    assert client.model_name == "claude-opus-4-20250514"


def test_env_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-env-key")
    client = AnthropicClient()
    assert client.api_key == "sk-env-key"


def test_missing_api_key_warns():
    with pytest.warns(UserWarning):
        AnthropicClient(api_key="")
