"""
Orchestrator — selects mode, configures engine flags,
reconciles user input with auto-detected signals.
"""

from dataclasses import dataclass

from ppc.schemas.input import InputSchema
from ppc.config.modes import ModeConfig, get_mode_config, MODE_MATRIX
from ppc.config.guardrails import (
    should_disable_deep_reflection,
    should_disable_multi_pass,
    should_disable_semantic_echo,
    is_simple_prompt,
)
from ppc.analyzers.intent import analyze_intent, IntentResult
from ppc.analyzers.constraint import (
    detect_constraints,
    has_compression_trigger,
    has_deep_analysis_trigger,
    has_security_trigger,
    has_teaching_trigger,
    has_code_trigger,
)
from ppc.analyzers.complexity import compute_complexity, ComplexityResult
from ppc.schemas.output import DetectedConstraints


@dataclass
class ExecutionPlan:
    mode: str
    mode_config: ModeConfig
    complexity: ComplexityResult
    effective_reflection_depth: int
    effective_reinforcement: str
    effective_echo: str
    effective_lock: str
    effective_compression: str
    override_mode: str | None


def _suggest_mode_from_prompt(
    prompt: str,
    intent: IntentResult,
    constraints: DetectedConstraints,
) -> str | None:
    if has_security_trigger(prompt):
        return "brutal"
    if has_code_trigger(prompt) or intent.is_code_related:
        if intent.primary_goal in ("design", "architect"):
            return "architect"
        return "code"
    if has_teaching_trigger(prompt) or intent.is_teaching_related:
        return "teacher"
    if has_compression_trigger(prompt) or intent.requires_compression:
        return "compress"
    if has_deep_analysis_trigger(prompt) or intent.requires_deep_analysis:
        return "reflection"
    if len(constraints.locked) >= 3:
        return "focus"
    return None


def build_execution_plan(input_schema: InputSchema) -> ExecutionPlan:
    prompt = input_schema.prompt
    token_estimate = input_schema.prompt_token_estimate()

    intent = analyze_intent(input_schema)
    constraints = detect_constraints(prompt)
    complexity = compute_complexity(prompt, token_estimate, intent, constraints)

    user_mode = input_schema.mode
    suggested_mode = _suggest_mode_from_prompt(prompt, intent, constraints)
    effective_mode = user_mode if user_mode != "basic" or not suggested_mode else suggested_mode
    final_mode = suggested_mode or effective_mode or user_mode

    is_simple = is_simple_prompt(token_estimate, len(constraints.locked))
    has_high_signal = (
        intent.is_security_related
        or intent.requires_deep_analysis
        or len(constraints.locked) >= 2
        or prompt.split().__len__() >= 8
    )
    if is_simple and not has_high_signal:
        final_mode = "basic"

    mode_config = get_mode_config(final_mode)

    effective_reflection_depth = mode_config.reflection_depth
    if should_disable_deep_reflection(token_estimate) and not has_high_signal:
        effective_reflection_depth = 0

    effective_reinforcement = mode_config.reinforcement
    effective_echo = mode_config.semantic_echo
    effective_lock = mode_config.constraint_lock
    effective_compression = mode_config.compression

    if should_disable_semantic_echo(len(constraints.locked) + len(constraints.soft)):
        effective_echo = "none"

    if input_schema.options.compression:
        effective_compression = "maximum"

    if final_mode == "brutal":
        effective_reflection_depth = max(effective_reflection_depth, 4)
        effective_reinforcement = "maximum"

    return ExecutionPlan(
        mode=final_mode,
        mode_config=mode_config,
        complexity=complexity,
        effective_reflection_depth=effective_reflection_depth,
        effective_reinforcement=effective_reinforcement,
        effective_echo=effective_echo,
        effective_lock=effective_lock,
        effective_compression=effective_compression,
        override_mode=suggested_mode,
    )
