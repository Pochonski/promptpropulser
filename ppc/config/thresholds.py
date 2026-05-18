"""
Threshold Configuration — Seccion 6, 7, 15

All numeric thresholds and budget rules live here.
No logic. Pure declarative configuration.
"""

# ----------------
# Complexity Score (Section 15)
# ----------------

COMPLEXITY_THRESHOLDS: dict[str, tuple[int, int]] = {
    "simple":   (0, 20),
    "medium":   (21, 50),
    "complex":  (51, 80),
    "critical": (81, 100),
}

CONSTRAINT_WEIGHT_MAP: dict[str, int] = {
    "0":           0,
    "1-2":         5,
    "3-5":        10,
    "6-10":       18,
    "10+":        25,
}

PROMPT_LENGTH_WEIGHT_MAP: dict[str, int] = {
    "<100":        2,
    "100-500":     6,
    "500-1500":   12,
    "1500-3000":  16,
    "3000+":      20,
}

AMBIGUITY_WEIGHT_MAP: dict[str, int] = {
    "low":             2,
    "medium":          8,
    "high":           15,
    "critical":       20,
}

REASONING_WEIGHT_MAP: dict[str, int] = {
    "none":      0,
    "light":     5,
    "medium":   10,
    "deep":     20,
}

DOMAIN_WEIGHT_MAP: dict[str, int] = {
    "casual_chat":   0,
    "writing":       3,
    "coding":        7,
    "architecture": 10,
    "cybersecurity": 15,
}

COMPLEXITY_COMPONENT_MAX: dict[str, int] = {
    "constraint":   25,
    "prompt_length": 20,
    "ambiguity":    20,
    "reasoning":    20,
    "domain":       15,
}

# ----------------
# Token Budget (Section 7)
# ----------------

TOKEN_BUDGET_ALLOCATION: dict[str, dict[str, float]] = {
    "small":    {"tokens": (0, 300),   "optimization": 0.15, "generation": 0.85},
    "medium":   {"tokens": (301, 2000), "optimization": 0.25, "generation": 0.75},
    "large":    {"tokens": (2001, 999999), "optimization": 0.35, "generation": 0.65},
}

OPTIMIZATION_HARD_LIMIT_RATIO = 0.70

# ----------------
# Compression (Section 6)
# ----------------

COMPRESSION_AUTO_THRESHOLD_TOKENS = 2500

COMPRESSION_TARGET_RANGE: tuple[float, float] = (0.20, 0.40)

COMPRESSION_DUPLICATE_THRESHOLD = 2

# ----------------
# Reinforcement Defaults (Section 4)
# ----------------

REINFORCEMENT_LEVELS: dict[str, dict] = {
    "none": {
        "intro": 0, "middle": 0, "final": 0,
        "echo_count": 0, "lock_enabled": False,
    },
    "low": {
        "intro": 0, "middle": 0, "final": 2,
        "echo_count": 1, "lock_enabled": False,
    },
    "medium": {
        "intro": 1, "middle": 0, "final": 2,
        "echo_count": 1, "lock_enabled": True,
    },
    "aggressive": {
        "intro": 1, "middle": 1, "final": 2,
        "echo_count": 2, "lock_enabled": True,
    },
    "maximum": {
        "intro": 2, "middle": 1, "final": 3,
        "echo_count": 3, "lock_enabled": True,
    },
}

# ----------------
# Anti-Overengineering (Section 8)
# ----------------

ANTI_OE_SIMPLE_THRESHOLD_TOKENS = 100

ANTI_OE_MIN_CONSTRAINTS_FOR_ECHO = 2

# ----------------
# Reflection (Section 9)
# ----------------

REFLECTION_STAGES = [
    "intent_validation",
    "constraint_validation",
    "quality_analysis",
    "failure_simulation",
]
