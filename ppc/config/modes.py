"""
Mode Execution Matrix — Section 14

Defines exactly what engines activate per mode.
Each mode is a dict of engine flags + parameter overrides.
"""

from dataclasses import dataclass, field


@dataclass
class ModeConfig:
    key: str
    reflection_depth: int
    semantic_echo: str          # "none" | "low" | "medium" | "aggressive" | "maximum"
    constraint_lock: str        # "disabled" | "soft_only" | "enabled" | "aggressive" | "maximum"
    critic_engine: str          # "no" | "optional" | "yes" | "maximum"
    compression: str            # "no" | "optional" | "maximum"
    multi_pass_reasoning: bool
    reinforcement: str          # "none" | "low" | "medium" | "aggressive" | "maximum"
    constraint_channel: str = "inline"  # "inline" | "system"


MODE_MATRIX: dict[str, ModeConfig] = {
    "basic": ModeConfig(
        key="basic",
        reflection_depth=0,
        semantic_echo="low",
        constraint_lock="soft_only",
        critic_engine="no",
        compression="no",
        multi_pass_reasoning=False,
        reinforcement="low",
    ),
    "reflection": ModeConfig(
        key="reflection",
        reflection_depth=3,
        semantic_echo="medium",
        constraint_lock="enabled",
        critic_engine="yes",
        compression="optional",
        multi_pass_reasoning=True,
        reinforcement="medium",
    ),
    "code": ModeConfig(
        key="code",
        reflection_depth=2,
        semantic_echo="medium",
        constraint_lock="aggressive",
        critic_engine="yes",
        compression="no",
        multi_pass_reasoning=True,
        reinforcement="aggressive",
        constraint_channel="system",
    ),
    "architect": ModeConfig(
        key="architect",
        reflection_depth=2,
        semantic_echo="medium",
        constraint_lock="enabled",
        critic_engine="yes",
        compression="optional",
        multi_pass_reasoning=True,
        reinforcement="aggressive",
    ),
    "brutal": ModeConfig(
        key="brutal",
        reflection_depth=4,
        semantic_echo="maximum",
        constraint_lock="maximum",
        critic_engine="maximum",
        compression="no",
        multi_pass_reasoning=True,
        reinforcement="maximum",
    ),
    "focus": ModeConfig(
        key="focus",
        reflection_depth=1,
        semantic_echo="aggressive",
        constraint_lock="maximum",
        critic_engine="optional",
        compression="no",
        multi_pass_reasoning=False,
        reinforcement="aggressive",
        constraint_channel="system",
    ),
    "teacher": ModeConfig(
        key="teacher",
        reflection_depth=1,
        semantic_echo="low",
        constraint_lock="soft_only",
        critic_engine="no",
        compression="no",
        multi_pass_reasoning=False,
        reinforcement="low",
    ),
    "compress": ModeConfig(
        key="compress",
        reflection_depth=0,
        semantic_echo="none",
        constraint_lock="disabled",
        critic_engine="no",
        compression="maximum",
        multi_pass_reasoning=False,
        reinforcement="none",
    ),
}


MODE_BEHAVIORS: dict[str, str] = {
    "basic": (
        "Speed-first. No deep reflection. No multi-pass reasoning. "
        "Minimal token overhead. Ideal for simple queries and casual chat."
    ),
    "reflection": (
        "Maximize reasoning quality. Runs intent analysis, semantic "
        "reinforcement, reflection loop, and critic validation. "
        "Ideal for debugging, complex decisions, and analysis."
    ),
    "code": (
        "Programming-optimized. Activates syntax validation, edge-case "
        "detection, dependency analysis, and compatibility checking. "
        "Reflection focuses on bugs, imports, performance, and security."
    ),
    "architect": (
        "Complex system design. Uses modular decomposition, dependency "
        "mapping, scalability analysis, and infrastructure reasoning. "
        "Ideal for large-scale architecture design."
    ),
    "brutal": (
        "Hypercritical audit mode. Runs contradiction attack, failure "
        "simulation, exploit reasoning, and assumption destruction. "
        "The system MUST attempt to invalidate its own response. "
        "Ideal for security, critical architecture, and validation."
    ),
    "focus": (
        "Aggressive constraint retention. Maximizes repeated constraints, "
        "semantic emphasis, and locked restrictions. Reduces creativity. "
        "Ideal when constraint adherence is the top priority."
    ),
    "teacher": (
        "Pedagogical mode. Uses progressive explanation, adaptive "
        "complexity, analogy generation, and concept continuity validation. "
        "Ideal for explanations and tutorials."
    ),
    "compress": (
        "Token minimization. Deduplicates, compresses semantically, and "
        "reduces context while preserving intent, constraints, and quality. "
        "Ideal for long prompts that need to fit token limits."
    ),
}


def get_mode_config(mode: str) -> ModeConfig:
    if mode not in MODE_MATRIX:
        valid = ", ".join(sorted(MODE_MATRIX.keys()))
        raise ValueError(f"Unknown mode '{mode}'. Valid modes: {valid}")
    return MODE_MATRIX[mode]


def get_mode_behavior(mode: str) -> str:
    if mode not in MODE_BEHAVIORS:
        valid = ", ".join(sorted(MODE_BEHAVIORS.keys()))
        raise ValueError(f"Unknown mode '{mode}'. Valid modes: {valid}")
    return MODE_BEHAVIORS[mode]
