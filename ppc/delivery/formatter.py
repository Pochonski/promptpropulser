"""
Delivery Layer — Section 16

Formats final output for the user in one of three modes:
  - transparent: optimized prompt only
  - hybrid: prompt + short summary
  - verbose: full analysis with all internal data
"""

import json
from dataclasses import dataclass

from ppc.schemas.output import OutputSchema, AnalyzedIntent, DetectedConstraints
from ppc.schemas.input import DeliveryMode


@dataclass
class UserOutput:
    optimized_prompt: str
    summary: str
    metadata: dict


def _build_summary(output: OutputSchema) -> str:
    lines = []
    intent = output.analyzed_intent
    constraints = output.constraints
    reinforcement = output.reinforcement

    if intent.primary_goal:
        lines.append(f"Goal: {intent.primary_goal.replace('_', ' ')}")
    if constraints.locked:
        lines.append(f"Locked constraints: {len(constraints.locked)}")
    if constraints.soft:
        lines.append(f"Soft preferences: {len(constraints.soft)}")
    if reinforcement.applied_patterns:
        lines.append(f"Reinforcement: {', '.join(reinforcement.applied_patterns)}")
    if output.semantic_echoes:
        lines.append(f"Echoes applied: {len(output.semantic_echoes)}")
    if output.reflection.enabled:
        lines.append("Reflection: enabled")
    tokens = output.token_usage
    if tokens.final_prompt_tokens > 0:
        lines.append(
            f"Tokens: {tokens.input_tokens} in -> "
            f"{tokens.final_prompt_tokens} out "
            f"({tokens.optimization_tokens} optimization)"
        )

    return " | ".join(lines) if lines else "No optimizations applied."


def _build_verbose_metadata(output: OutputSchema) -> dict:
    return {
        "analyzed_intent": {
            "primary_goal": output.analyzed_intent.primary_goal,
            "secondary_goals": output.analyzed_intent.secondary_goals,
            "complexity_score": output.analyzed_intent.complexity_score,
        },
        "constraints": {
            "locked": output.constraints.locked,
            "soft": output.constraints.soft,
            "detected_types": output.constraints.detected_types,
        },
        "reinforcement": {
            "level": output.reinforcement.level,
            "applied_patterns": output.reinforcement.applied_patterns,
        },
        "semantic_echoes": output.semantic_echoes,
        "reflection": {
            "enabled": output.reflection.enabled,
            "stage_results": output.reflection.stage_results,
            "critic_notes": output.reflection.critic_notes,
        },
        "token_usage": {
            "input_tokens": output.token_usage.input_tokens,
            "optimization_tokens": output.token_usage.optimization_tokens,
            "final_prompt_tokens": output.token_usage.final_prompt_tokens,
        },
    }


def format_output(
    output: OutputSchema,
    delivery_mode: DeliveryMode = "transparent",
) -> UserOutput:
    if delivery_mode == "transparent":
        return UserOutput(
            optimized_prompt=output.optimized_prompt,
            summary="",
            metadata={},
        )

    elif delivery_mode == "hybrid":
        summary = _build_summary(output)
        return UserOutput(
            optimized_prompt=output.optimized_prompt,
            summary=summary,
            metadata={},
        )

    elif delivery_mode == "verbose":
        summary = _build_summary(output)
        metadata = _build_verbose_metadata(output)
        return UserOutput(
            optimized_prompt=output.optimized_prompt,
            summary=summary,
            metadata=metadata,
        )

    return UserOutput(
        optimized_prompt=output.optimized_prompt,
        summary="",
        metadata={},
    )
