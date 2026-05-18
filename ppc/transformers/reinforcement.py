"""
Attention Reinforcement Engine (ARE) — Sections 1, 4

Redistributes critical information within the prompt
to increase attentional weight via:
  - repetition reinforcement
  - edge emphasis (primacy + recency)
  - priority stacking
  - semantic weighting
"""

from ppc.analyzers.intent import IntentResult
from ppc.schemas.output import DetectedConstraints
from ppc.config.thresholds import REINFORCEMENT_LEVELS
from ppc.config.modes import ModeConfig


def _build_intro_block(
    intent: IntentResult,
    constraints: DetectedConstraints,
) -> str:
    lines = []
    if intent.primary_goal:
        goal_label = intent.primary_goal.upper().replace("_", " ")
        lines.append(f"PRIMARY TASK: {goal_label}.")
    for i, goal in enumerate(intent.secondary_goals[:3]):
        lines.append(f"SECONDARY TASK {i+1}: {goal.replace('_', ' ')}.")
    return "\n".join(lines)


def _build_priority_block(constraints: DetectedConstraints) -> str:
    if not constraints.locked:
        return ""
    lines = ["ABSOLUTE PRIORITY:"]
    for c in constraints.locked[:5]:
        clean = c.strip().rstrip(".").rstrip(" ")
        lines.append(f"  - {clean}")
    return "\n".join(lines)


def _build_reminder_block(constraints: DetectedConstraints, repetition: int) -> str:
    if not constraints.locked or repetition <= 0:
        return ""

    reminders = []
    for _ in range(repetition):
        for c in constraints.locked[:3]:
            clean = c.strip().rstrip(".").rstrip(" ")
            reminders.append(f"REMINDER: {clean}.")

    if len(reminders) > 6:
        reminders = reminders[:6]
    return "\n".join(reminders)


def _build_middle_reinforcement(constraints: DetectedConstraints) -> str:
    if not constraints.locked:
        return ""
    items = [f"  [ ] {c.strip()[:100]}" for c in constraints.locked[:5]]
    return "MID-RESPONSE CHECKPOINT:\n" + "\n".join(items)


def _build_validation_checklist(constraints: DetectedConstraints) -> str:
    if not constraints.locked:
        return ""
    checks = [f"  [ ] Verified: {c.strip()[:120]}" for c in constraints.locked]
    return "PRE-RESPONSE VALIDATION:\n" + "\n".join(checks)


def _build_antialucination_block(constraints: DetectedConstraints) -> str:
    if not constraints.locked:
        return ""
    lines = [
        "ANTI-HALLUCINATION CHECK:",
        "Before outputting the final response, confirm:",
    ]
    for c in constraints.locked[:5]:
        lines.append(f"  - No part of the response violates: {c.strip()[:120]}")
    return "\n".join(lines)


def apply_reinforcement(
    prompt: str,
    intent: IntentResult,
    constraints: DetectedConstraints,
    mode_config: ModeConfig,
    reinforcement_level: str,
    echo_block: str,
) -> str:
    levels = REINFORCEMENT_LEVELS.get(
        reinforcement_level,
        REINFORCEMENT_LEVELS["medium"],
    )

    intro_count = levels.get("intro", 0)
    middle_count = levels.get("middle", 0)
    final_count = levels.get("final", 0)

    parts: list[str] = []

    if intro_count >= 1:
        intro = _build_intro_block(intent, constraints)
        if intro:
            parts.append(intro)
        priority = _build_priority_block(constraints)
        if priority and intro_count >= 2:
            parts.append(priority)

    parts.append(prompt)

    if echo_block:
        parts.append(echo_block)

    if middle_count >= 1:
        middle = _build_middle_reinforcement(constraints)
        if middle:
            parts.append(middle)

    if final_count >= 1:
        reminder = _build_reminder_block(constraints, final_count)
        if reminder:
            parts.append(reminder)

    if reinforcement_level in ("aggressive", "maximum"):
        checklist = _build_validation_checklist(constraints)
        if checklist:
            parts.append(checklist)

    if reinforcement_level == "maximum":
        antihallucination = _build_antialucination_block(constraints)
        if antihallucination:
            parts.append(antihallucination)

    return "\n\n".join(parts)


def determine_reinforcement_level(
    mode_config: ModeConfig,
    complexity_score: int,
    constraint_count: int,
    user_override: str | None = None,
) -> str:
    if user_override and user_override in REINFORCEMENT_LEVELS:
        return user_override

    if mode_config.key in ("compress",):
        return "none"
    if mode_config.key in ("basic", "teacher"):
        return "low"
    if mode_config.key == "brutal":
        return "maximum"
    if complexity_score >= 81:
        return "maximum"
    if complexity_score >= 51:
        return "aggressive"
    if constraint_count >= 6:
        return "aggressive"
    if constraint_count >= 3:
        return "medium"

    return mode_config.reinforcement


def count_applied_patterns(level: str) -> list[str]:
    levels = REINFORCEMENT_LEVELS.get(level, REINFORCEMENT_LEVELS["medium"])
    patterns = []
    if levels.get("intro", 0) > 0:
        patterns.append("intro_reinforcement")
    if levels.get("middle", 0) > 0:
        patterns.append("middle_reinforcement")
    if levels.get("final", 0) > 0:
        patterns.append("final_reinforcement")
    if levels.get("echo_count", 0) > 0:
        patterns.append("semantic_echo")
    if levels.get("lock_enabled", False):
        patterns.append("constraint_lock")
    if level == "maximum":
        patterns.append("anti_hallucination_check")
        patterns.append("validation_checklist")
    return patterns
