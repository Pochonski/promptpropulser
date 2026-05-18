"""
Conflict Resolution Engine — Section 5

Priority hierarchy and resolution strategies
for conflicting user instructions.
"""

PRIORITY_HIERARCHY: list[str] = [
    "safety",
    "locked_constraints",
    "user_explicit_goals",
    "output_formatting",
    "style_preferences",
    "verbosity_preferences",
]

PRIORITY_RANK: dict[str, int] = {
    label: idx for idx, label in enumerate(PRIORITY_HIERARCHY)
}


RESOLUTION_RULES: list[dict] = [
    {
        "conflict": ("short_verbosity", "step_by_step"),
        "triggers": [
            (["corto", "breve", "r\u00e1pido", "resumen"],
             ["paso a paso", "detallado", "explica", "pasos"]),
        ],
        "resolution": "Prioritize step clarity. Reduce verbosity. Output short structured steps.",
        "winner": "step_by_step",
    },
    {
        "conflict": ("maximum_security", "maximum_speed"),
        "triggers": [
            (["seguridad", "seguro", "cr\u00edtico"],
             ["r\u00e1pido", "veloz", "performance", "optimiza"]),
        ],
        "resolution": "Security overrides performance. Apply caution. Note the tradeoff.",
        "winner": "maximum_security",
    },
    {
        "conflict": ("no_dependencies", "use_framework"),
        "triggers": [
            (["sin dependencias", "no uses librer\u00edas", "minimalista"],
             ["usa react", "usa django", "usa fastapi"]),
        ],
        "resolution": "Framework constraint wins. The user explicitly requested it. Note minimalism preference.",
        "winner": "use_framework",
    },
    {
        "conflict": ("exhaustive", "concise"),
        "triggers": [
            (["completo", "exhaustivo", "todo", "cada detalle"],
             ["corto", "breve", "conciso", "resumido"]),
        ],
        "resolution": "Provide structured summary with option to expand. Default to concise with signposts.",
        "winner": "hybrid",
    },
    {
        "conflict": ("keep_architecture", "refactor"),
        "triggers": [
            (["no cambies", "mant\u00e9n", "conserva", "no modifiques"],
             ["refactor", "mejora", "optimiza", "reescribe"]),
        ],
        "resolution": "Keep architecture constraint locks. Apply improvements only within existing structure.",
        "winner": "keep_architecture",
    },
    {
        "conflict": ("no_db", "use_orm"),
        "triggers": [
            (["sin base de datos", "no uses db", "sin sql"],
             ["usa sqlalchemy", "usa prisma", "orm"]),
        ],
        "resolution": "No database constraint is locked. Reject ORM usage. Suggest alternatives.",
        "winner": "no_db",
    },
]


def resolve_conflict(
    detected_a: str,
    detected_b: str,
) -> dict | None:
    for rule in RESOLUTION_RULES:
        conflict_pair = rule["conflict"]
        if detected_a in conflict_pair and detected_b in conflict_pair:
            return rule
    return None


def get_priority(label: str) -> int:
    return PRIORITY_RANK.get(label, 999)
