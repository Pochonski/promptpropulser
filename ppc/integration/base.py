"""
Base LLM Client — abstract interface.

Implementations: AnthropicClient, OpenAI (future), Gemini (future).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""
    model: str = ""


class BaseLLMClient(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        ...

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...
