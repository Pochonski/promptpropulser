"""
Anti-Overengineering Guardrails — Section 8

Prevents the system from applying heavyweight pipelines
to trivial prompts. Guard clauses evaluated before
pipeline execution.
"""

from ppc.config.thresholds import ANTI_OE_SIMPLE_THRESHOLD_TOKENS, ANTI_OE_MIN_CONSTRAINTS_FOR_ECHO


def should_disable_deep_reflection(prompt_tokens: int) -> bool:
    return prompt_tokens < ANTI_OE_SIMPLE_THRESHOLD_TOKENS


def should_disable_brutal_mode(prompt_tokens: int) -> bool:
    return prompt_tokens < ANTI_OE_SIMPLE_THRESHOLD_TOKENS


def should_disable_multi_pass(prompt_tokens: int) -> bool:
    return prompt_tokens < ANTI_OE_SIMPLE_THRESHOLD_TOKENS


def should_disable_semantic_echo(constraint_count: int) -> bool:
    return constraint_count <= ANTI_OE_MIN_CONSTRAINTS_FOR_ECHO - 1


def should_use_maximum_reinforcement(mode: str, complexity: int, constraint_count: int) -> bool:
    if mode in ("basic", "teacher", "compress"):
        return False
    if complexity >= 81:
        return True
    if constraint_count >= 10:
        return True
    return mode == "brutal"


def is_simple_prompt(prompt_tokens: int, constraint_count: int) -> bool:
    return prompt_tokens < ANTI_OE_SIMPLE_THRESHOLD_TOKENS and constraint_count < 2


GUARDRAILS = [
    {
        "rule": 1,
        "condition": "input_tokens < 100",
        "action": "disable: deep_reflection, brutal_mode, multi_pass_reasoning",
        "func": lambda tokens: should_disable_deep_reflection(tokens),
    },
    {
        "rule": 2,
        "condition": "simple_prompt",
        "action": "use simple pipeline only",
        "func": lambda tokens, constraints: is_simple_prompt(tokens, constraints),
    },
    {
        "rule": 3,
        "condition": "casual mode + maximum reinforcement",
        "action": "never use maximum reinforcement for casual conversation",
        "func": lambda mode, level: not (mode in ("basic", "teacher") and level == "maximum"),
    },
    {
        "rule": 4,
        "condition": "constraints <= 1",
        "action": "do not add semantic echoes",
        "func": lambda count: should_disable_semantic_echo(count),
    },
]
