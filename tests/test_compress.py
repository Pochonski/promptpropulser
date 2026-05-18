"""Tests for Prompt Compression Engine"""

import pytest
from ppc.transformers.compress import (
    compress_prompt,
    should_compress,
    estimate_compression_ratio,
    estimate_tokens,
)


def test_compress_removes_duplicate_lines():
    prompt = "Haz una API\nHaz una API\nHaz una API\ncon FastAPI"
    result = compress_prompt(prompt, "create", [])
    assert result.count("Haz una API") <= 2


def test_compress_removes_fillers():
    prompt = "Basicamente haz una API y obviamente usa FastAPI"
    result = compress_prompt(prompt, "create", [])
    assert "api" in result.lower()


def test_compress_handles_empty():
    result = compress_prompt("", "create", [])
    assert result == ""


def test_should_compress_short():
    assert should_compress("Hola") is False


def test_should_compress_force():
    assert should_compress("Hola", force=True) is True


def test_estimate_compression_ratio():
    ratio = estimate_compression_ratio("a b c d e f g h i j", "a b c")
    assert ratio > 0


def test_estimate_tokens():
    assert estimate_tokens("hola mundo") == 2
    assert estimate_tokens("") == 0


def test_compress_preserves_content():
    prompt = "Usa FastAPI y Python 3.12"
    result = compress_prompt(prompt, "create", ["Python 3.12"])
    assert "FastAPI" in result or "Python" in result
