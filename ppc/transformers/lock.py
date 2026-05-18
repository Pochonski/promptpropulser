"""
Constraint Lock System — Section 4

Converts critical constraints into an immutable locked block
pinned at top and bottom of the prompt to prevent model
from forgetting mid-generation.
"""

from ppc.schemas.output import DetectedConstraints


def _build_lock_block(constraints: list[str]) -> str:
    if not constraints:
        return ""

    lines = [
        "LOCKED CONSTRAINTS (NON-NEGOTIABLE):",
    ]
    for i, constraint in enumerate(constraints, 1):
        clean = constraint.strip().rstrip(".").rstrip(" ")
        lines.append(f"  [{i}] {clean}.")

    lines.append("")
    lines.append(
        "THE ABOVE CONSTRAINTS ARE MANDATORY. "
        "DO NOT VIOLATE, RELAX, OR IGNORE THEM UNDER ANY CIRCUMSTANCE."
    )

    return "\n".join(lines)


def _build_soft_note(constraints: list[str]) -> str:
    if not constraints:
        return ""

    lines = ["PREFERRED GUIDELINES (FOLLOW WHEN POSSIBLE):"]
    for i, constraint in enumerate(constraints, 1):
        clean = constraint.strip().rstrip(".").rstrip(" ")
        lines.append(f"  ({i}) {clean}.")

    return "\n".join(lines)


def apply_constraint_lock(
    prompt: str,
    constraints: DetectedConstraints,
    lock_intensity: str,
) -> str:
    """
    lock_intensity: "disabled" | "soft_only" | "enabled" | "aggressive" | "maximum"
    """
    if lock_intensity == "disabled":
        return prompt

    top_block = ""
    bottom_block = ""

    if lock_intensity == "soft_only":
        if constraints.locked:
            top_block = _build_lock_block(constraints.locked)
        if constraints.soft:
            soft_note = _build_soft_note(constraints.soft)
            top_block = f"{top_block}\n\n{soft_note}" if top_block else soft_note

    elif lock_intensity == "enabled":
        if constraints.locked:
            top_block = _build_lock_block(constraints.locked)
            bottom_block = f"\n\nREMINDER: {len(constraints.locked)} locked constraint(s) remain in effect."

    elif lock_intensity == "aggressive":
        if constraints.locked:
            top_block = _build_lock_block(constraints.locked)
            bottom_block = (
                f"\n\nREPEATED REMINDER:\n{_build_lock_block(constraints.locked)}"
            )

    elif lock_intensity == "maximum":
        if constraints.locked:
            lock_block = _build_lock_block(constraints.locked)
            top_block = lock_block
            bottom_block = (
                f"\n\n=== CONSTRAINT INTEGRITY CHECK ===\n"
                f"BEFORE RESPONDING, VERIFY:\n"
                + "\n".join(
                    f"  [ ] Did I respect: {c.strip()[:120]}"
                    for c in constraints.locked
                )
                + f"\n\n{lock_block}"
            )

    result = prompt
    if top_block:
        result = f"{top_block}\n\n---\n\n{result}"
    if bottom_block:
        result = f"{result}{bottom_block}"

    return result
