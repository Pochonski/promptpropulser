"""
LangChain Integration — PPC as a custom Chain / PromptTemplate.

Usage with LangChain:

    from ppc.integration.langchain import PPCPromptTemplate, PPCChain

    # Option 1: Standalone template
    template = PPCPromptTemplate(mode="code")
    optimized = template.format("Haz una API en FastAPI sin DB")

    # Option 2: Full chain (optimize + LLM)
    chain = PPCChain(mode="brutal", llm=ChatAnthropic(model="claude-sonnet-4-6"))
    result = chain.invoke({"input": "Audita este sistema JWT"})

Requires: langchain, langchain-anthropic
"""

from typing import Any

from ppc.schemas.input import InputSchema, InputOptions
from ppc.engine.pipeline import run_pipeline


class PPCPromptTemplate:
    """LangChain-compatible prompt template that runs PPC optimization."""

    def __init__(
        self,
        mode: str = "basic",
        reinforcement_level: str = "medium",
        reflection_depth: int = 0,
        compression: bool = False,
        token_budget: int = 4000,
    ):
        self.mode = mode
        self.reinforcement_level = reinforcement_level
        self.reflection_depth = reflection_depth
        self.compression = compression
        self.token_budget = token_budget

    def format(self, **kwargs: Any) -> str:
        prompt = kwargs.get("input") or kwargs.get("prompt") or str(kwargs)
        schema = InputSchema(
            mode=self.mode,
            prompt=prompt,
            options=InputOptions(
                reinforcement_level=self.reinforcement_level,
                reflection_depth=self.reflection_depth,
                compression=self.compression,
                strict_constraints=True,
                token_budget=self.token_budget,
            ),
        )
        output = run_pipeline(schema)
        return output.optimized_prompt

    def format_prompt(self, **kwargs: Any) -> str:
        return self.format(**kwargs)

    def invoke(self, input_data: dict[str, Any]) -> dict[str, Any]:
        prompt = input_data.get("input") or input_data.get("prompt") or str(input_data)
        optimized = self.format(input=prompt)
        return {"optimized_prompt": optimized, "input": prompt}


class PPCOptimizer:
    """Lightweight wrapper for LangChain pipeline integration."""

    def __init__(
        self,
        mode: str = "basic",
        reinforcement_level: str = "medium",
    ):
        self.mode = mode
        self.reinforcement_level = reinforcement_level

    def optimize(self, prompt: str) -> str:
        schema = InputSchema(
            mode=self.mode,
            prompt=prompt,
            options=InputOptions(
                reinforcement_level=self.reinforcement_level,
                strict_constraints=True,
            ),
        )
        output = run_pipeline(schema)
        return output.optimized_prompt

    def __call__(self, prompt: str) -> str:
        return self.optimize(prompt)
