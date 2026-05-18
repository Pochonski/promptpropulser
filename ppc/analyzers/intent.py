"""Intent Analyzer — detects primary goal, secondary goals, and classifies intent."""

import re
from dataclasses import dataclass, field

from ppc.schemas.input import InputSchema


@dataclass
class IntentResult:
    primary_goal: str = ""
    secondary_goals: list[str] = field(default_factory=list)
    domain: str = "casual_chat"
    is_code_related: bool = False
    is_security_related: bool = False
    is_teaching_related: bool = False
    requires_deep_analysis: bool = False
    requires_compression: bool = False
    raw_prompt: str = ""


GOAL_PATTERNS: list[tuple[str, list[str]]] = [
    ("create", ["crea", "crear", "haz", "hacer", "genera", "generar", "construye",
                "construir", "escribe", "escribir", "desarrolla", "desarrollar",
                "implementa", "implementar", "build", "create", "make", "generate"]),
    ("fix", ["arregla", "arreglar", "corrige", "corregir", "repara", "reparar",
             "fix", "solve", "resuelve", "resolver"]),
    ("explain", ["explica", "explicar", "expl\u00edcame", "describe", "describir",
                 "explain", "describe", "tell me about", "what is"]),
    ("analyze", ["analiza", "analizar", "eval\u00faa", "evaluar", "revisa", "revisar",
                 "analyze", "evaluate", "review", "audit", "audita"]),
    ("optimize", ["optimiza", "optimizar", "mejora", "mejorar", "refactoriza",
                  "optimize", "improve", "refactor"]),
    ("design", ["dise\u00f1a", "dise\u00f1ar", "arquitectura", "planifica", "planificar",
                "design", "architect", "plan"]),
    ("compare", ["compara", "comparar", "diferencia", "compare", "diff"]),
    ("convert", ["convierte", "convertir", "transforma", "transformar",
                 "convert", "transform", "migrate", "migra"]),
    ("research", ["investiga", "investigar", "busca", "buscar", "research", "find"]),
    ("summarize", ["resume", "resumir", "resumen", "sintetiza", "summarize", "tldr"]),
]

DOMAIN_INDICATORS: dict[str, list[str]] = {
    "coding": [
        "c\u00f3digo", "code", "programa", "funci\u00f3n", "function", "clase",
        "class", "api", "endpoint", "bug", "error", "import", "script",
        "fastapi", "django", "flask", "react", "vue", "python", "javascript",
        "typescript", "rust", "go", "java", "sql", "database", "frontend",
        "backend", "npm", "pip", "docker", "git",
    ],
    "architecture": [
        "arquitectura", "architecture", "sistema", "system", "dise\u00f1o",
        "design", "infraestructura", "infrastructure", "microservicios",
        "microservices", "escalable", "scalable", "modular", "componentes",
        "components", "patr\u00f3n", "pattern", "distribuido", "distributed",
    ],
    "cybersecurity": [
        "seguridad", "security", "vulnerabilidad", "vulnerability", "hack",
        "exploit", "ataque", "attack", "pentest", "auditor\u00eda", "audit",
        "cifrado", "encryption", "autenticaci\u00f3n", "authentication",
        "jwt", "oauth", "token",
    ],
    "writing": [
        "escribe", "write", "redacta", "art\u00edculo", "article", "blog",
        "ensayo", "essay", "documento", "document", "correo", "email",
        "carta", "letter",
    ],
}


def _detect_primary_goal(prompt: str) -> str:
    prompt_lower = prompt.lower()
    matched = []
    for goal, patterns in GOAL_PATTERNS:
        score = sum(1 for p in patterns if p in prompt_lower)
        if score > 0:
            matched.append((goal, score))
    matched.sort(key=lambda x: x[1], reverse=True)
    if matched:
        return matched[0][0]
    return "general_query"


def _detect_secondary_goals(prompt: str) -> list[str]:
    prompt_lower = prompt.lower()
    found = []
    for goal, patterns in GOAL_PATTERNS:
        if any(p in prompt_lower for p in patterns):
            found.append(goal)
    if len(found) > 1:
        return found[1:]
    return []


def _detect_domain(prompt: str) -> str:
    prompt_lower = prompt.lower()
    scores = {}
    for domain, indicators in DOMAIN_INDICATORS.items():
        score = sum(1 for ind in indicators if ind in prompt_lower)
        if score > 0:
            scores[domain] = score
    if not scores:
        return "casual_chat"
    return max(scores, key=scores.get)


def analyze_intent(input_schema: InputSchema) -> IntentResult:
    prompt = input_schema.prompt.strip()
    prompt_lower = prompt.lower()

    primary = _detect_primary_goal(prompt)
    secondary = _detect_secondary_goals(prompt)
    domain = _detect_domain(prompt)

    code_keywords = [
        "c\u00f3digo", "code", "programa", "api", "funci\u00f3n",
        "function", "clase", "class", "bug", "error", "import",
        "endpoint", "fastapi", "django", "flask", "script",
        "python", "javascript", "typescript",
    ]
    is_code_related = any(kw in prompt_lower for kw in code_keywords)

    security_keywords = [
        "seguridad", "security", "vulnerab", "hack", "exploit",
        "ataque", "auditor", "cifrado", "encryption", "jwt",
        "oauth", "token forgery",
    ]
    is_security_related = any(kw in prompt_lower for kw in security_keywords)

    teaching_keywords = [
        "expl\u00edcame", "explica", "aprende", "paso a paso",
        "tutorial", "ense\u00f1a", "eli5", "principiante",
    ]
    is_teaching_related = any(kw in prompt_lower for kw in teaching_keywords)

    deep_analysis_keywords = [
        "analiza", "profundo", "detallado", "investiga",
        "debug", "reflection", "eval\u00faa", "compara",
        "optimiza", "arquitectura",
    ]
    requires_deep_analysis = any(kw in prompt_lower for kw in deep_analysis_keywords)

    compression_keywords = [
        "r\u00e1pido", "breve", "resumen", "corto", "conciso",
        "tldr", "sintetiza", "al grano", "sin rodeos",
    ]
    requires_compression = any(kw in prompt_lower for kw in compression_keywords)

    return IntentResult(
        primary_goal=primary,
        secondary_goals=secondary,
        domain=domain,
        is_code_related=is_code_related,
        is_security_related=is_security_related,
        is_teaching_related=is_teaching_related,
        requires_deep_analysis=requires_deep_analysis,
        requires_compression=requires_compression,
        raw_prompt=prompt,
    )
