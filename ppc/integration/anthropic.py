"""
Anthropic Claude Client — implements BaseLLMClient via anthropic SDK.
"""

import os
from dataclasses import dataclass

from ppc.integration.base import BaseLLMClient, LLMResponse


DEFAULT_MODEL = "claude-sonnet-4-6"


@dataclass
class AnthropicClient(BaseLLMClient):
    api_key: str = ""
    model: str = DEFAULT_MODEL
    base_url: str = ""
    _client: object = None

    def __post_init__(self):
        self.api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.base_url = self.base_url or os.environ.get("ANTHROPIC_BASE_URL", "")
        if not self.api_key:
            import warnings
            warnings.warn(
                "ANTHROPIC_API_KEY not set. Client will fail on generate() "
                "unless api_key is provided later."
            )

    def _get_client(self):
        if self._client is None:
            import anthropic
            kwargs = dict(api_key=self.api_key)
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = anthropic.Anthropic(**kwargs)
        return self._client

    @property
    def model_name(self) -> str:
        return self.model

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        client = self._get_client()

        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        if system_prompt:
            kwargs["system"] = system_prompt

        message = client.messages.create(**kwargs)

        return LLMResponse(
            text=message.content[0].text,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
            stop_reason=message.stop_reason,
            model=message.model,
        )

    def count_tokens(self, text: str) -> int:
        client = self._get_client()
        return client.messages.count_tokens(
            model=self.model,
            messages=[{"role": "user", "content": text}],
        ).input_tokens
