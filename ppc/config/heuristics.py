"""
Constraint Detection Heuristics — Section 3

Pattern-based triggers that classify user intent.
No logic. Pure pattern definitions consumed by analyzers/constraint.py.
"""

from dataclasses import dataclass, field


@dataclass
class TriggerPattern:
    keywords: list[str]
    weight: int = 1


# ----------------
# Hard Constraint Triggers → LOCKED CONSTRAINT
# ----------------

HARD_CONSTRAINT_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["no uses", "no usar", "no utilices"], weight=3),
    TriggerPattern(keywords=["sin usar", "sin utilizar"], weight=3),
    TriggerPattern(keywords=["evita", "evitar", "evite"], weight=2),
    TriggerPattern(keywords=["prohibido", "prohibida"], weight=3),
    TriggerPattern(keywords=["nunca", "jam\u00e1s"], weight=3),
    TriggerPattern(keywords=["obligatorio", "obligatoria", "obligatoriamente"], weight=3),
    TriggerPattern(keywords=["debe", "deben", "deber\u00e1"], weight=2),
    TriggerPattern(keywords=["solo usa", "solo usar", "solo utiliza", "\u00fanicamente"], weight=3),
    TriggerPattern(keywords=["mant\u00e9n", "mantener", "conserva"], weight=2),
    TriggerPattern(keywords=["no cambies", "no modifiques", "no alteres"], weight=3),
    TriggerPattern(keywords=["no agregues", "no a\u00f1adas", "no incluyas"], weight=2),
    TriggerPattern(keywords=["sin", "no"], weight=1),
    TriggerPattern(keywords=["requerido", "necesario", "imprescindible"], weight=2),
]

# ----------------
# Soft Constraint Triggers → SOFT CONSTRAINT
# ----------------

SOFT_CONSTRAINT_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["preferiblemente", "de preferencia"], weight=1),
    TriggerPattern(keywords=["idealmente", "lo ideal"], weight=1),
    TriggerPattern(keywords=["si puedes", "si es posible", "si se puede"], weight=1),
    TriggerPattern(keywords=["me gustar\u00eda", "quisiera", "desear\u00eda"], weight=1),
    TriggerPattern(keywords=["opcional", "opcionalmente"], weight=1),
    TriggerPattern(keywords=["recomendado", "sugerido"], weight=1),
    TriggerPattern(keywords=["a ser posible", "en lo posible"], weight=1),
]

# ----------------
# Compression Triggers → activate COMPRESS MODE
# ----------------

COMPRESSION_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["r\u00e1pido", "rapido", "veloz"], weight=1),
    TriggerPattern(keywords=["breve", "brevemente"], weight=1),
    TriggerPattern(keywords=["resumen", "resumir", "resumido"], weight=1),
    TriggerPattern(keywords=["corto", "corta", "acortar"], weight=1),
    TriggerPattern(keywords=["conciso", "concisi\u00f3n"], weight=1),
    TriggerPattern(keywords=["TLDR", "tldr", "tl;dr"], weight=1),
    TriggerPattern(keywords=["sintetiza", "sintetizar", "s\u00edntesis"], weight=1),
    TriggerPattern(keywords=["al grano", "directo"], weight=1),
    TriggerPattern(keywords=["sin rodeos"], weight=1),
]

# ----------------
# Deep Analysis Triggers → increase REFLECTION DEPTH
# ----------------

DEEP_ANALYSIS_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["analiza", "analizar", "an\u00e1lisis", "analisis"], weight=2),
    TriggerPattern(keywords=["profundo", "profundidad", "a fondo"], weight=2),
    TriggerPattern(keywords=["detallado", "detalle", "detalladamente"], weight=1),
    TriggerPattern(keywords=["arquitectura", "arquitect\u00f3nico"], weight=2),
    TriggerPattern(keywords=["investiga", "investigar", "investigaci\u00f3n"], weight=2),
    TriggerPattern(keywords=["debug", "debugging", "depurar", "depuraci\u00f3n"], weight=2),
    TriggerPattern(keywords=["reflection", "reflexi\u00f3n", "reflexionar"], weight=2),
    TriggerPattern(keywords=["eval\u00faa", "evaluar", "evaluaci\u00f3n"], weight=2),
    TriggerPattern(keywords=["compara", "comparar", "comparativa"], weight=1),
    TriggerPattern(keywords=["optimiza", "optimizar", "optimizaci\u00f3n"], weight=2),
]

# ----------------
# Security / Brutal Mode Triggers
# ----------------

SECURITY_BRUTAL_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["seguridad", "seguro", "inseguro"], weight=2),
    TriggerPattern(keywords=["vulnerabilidad", "vulnerable"], weight=3),
    TriggerPattern(keywords=["hack", "hackear", "hackeo"], weight=2),
    TriggerPattern(keywords=["exploit", "explotar", "explotaci\u00f3n"], weight=3),
    TriggerPattern(keywords=["riesgo", "riesgoso", "arriesgado"], weight=2),
    TriggerPattern(keywords=["cr\u00edtico", "critico", "cr\u00edtica", "critica"], weight=2),
    TriggerPattern(keywords=["auditor\u00eda", "auditoria", "auditar"], weight=3),
    TriggerPattern(keywords=["ataque", "atacante", "adversario"], weight=2),
    TriggerPattern(keywords=["amenaza", "peligro"], weight=2),
    TriggerPattern(keywords=["pentest", "penetration test", "pen testing"], weight=3),
]

# ----------------
# Teaching Triggers → activate TEACHER MODE
# ----------------

TEACHING_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["expl\u00edcame", "explicame", "explica", "explicar"], weight=1),
    TriggerPattern(keywords=["aprende", "aprender", "aprendizaje"], weight=1),
    TriggerPattern(keywords=["paso a paso", "paso por paso"], weight=1),
    TriggerPattern(keywords=["ELI5", "eli5", "explain like"], weight=1),
    TriggerPattern(keywords=["ense\u00f1a", "ens\u00e9\u00f1ame", "ense\u00f1ame", "enseniar"], weight=1),
    TriggerPattern(keywords=["tutorial", "gu\u00eda", "guia"], weight=1),
    TriggerPattern(keywords=["principiante", "b\u00e1sico", "basico"], weight=1),
    TriggerPattern(keywords=["entiende", "entender", "comprender"], weight=1),
]

# ----------------
# Reasoning Depth Triggers
# ----------------

REASONING_DEPTH_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["analiza", "analizar"], weight=1),
    TriggerPattern(keywords=["design", "dise\u00f1a", "dise\u00f1ar", "dise\u00f1o"], weight=2),
    TriggerPattern(keywords=["architect", "arquitectura"], weight=2),
    TriggerPattern(keywords=["optimiza", "optimizar"], weight=1),
    TriggerPattern(keywords=["debug", "depurar"], weight=1),
    TriggerPattern(keywords=["eval\u00faa", "evaluar"], weight=1),
    TriggerPattern(keywords=["compara", "comparar"], weight=1),
    TriggerPattern(keywords=["investiga", "investigar", "research"], weight=1),
]

# ----------------
# Code-Specific Triggers
# ----------------

CODE_TRIGGERS: list[TriggerPattern] = [
    TriggerPattern(keywords=["c\u00f3digo", "codigo", "code"], weight=2),
    TriggerPattern(keywords=["programa", "programar", "programaci\u00f3n"], weight=2),
    TriggerPattern(keywords=["API", "endpoint"], weight=1),
    TriggerPattern(keywords=["funci\u00f3n", "funcion", "function"], weight=1),
    TriggerPattern(keywords=["clase", "class", "m\u00f3dulo", "modulo"], weight=1),
    TriggerPattern(keywords=["bug", "error", "fix", "arreglar"], weight=1),
    TriggerPattern(keywords=["refactor", "refactorizar"], weight=1),
    TriggerPattern(keywords=["test", "testing", "pruebas"], weight=1),
    TriggerPattern(keywords=["import", "dependencia", "dependency"], weight=1),
    TriggerPattern(keywords=["FastAPI", "Django", "Flask"], weight=1),
    TriggerPattern(keywords=["Python", "JavaScript", "TypeScript", "Rust", "Go"], weight=1),
]

# ----------------
# Constraint Type Labels
# ----------------

CONSTRAINT_TYPE_LABELS: list[str] = [
    "technological",
    "structural",
    "format",
    "length",
    "compatibility",
    "style",
    "security",
    "architecture",
]

TECH_TRIGGERS: list[str] = [
    "docker", "react", "vue", "angular", "postgresql", "mysql", "mongodb",
    "redis", "graphql", "rest", "grpc", "aws", "azure", "gcp", "kubernetes",
    "python", "javascript", "typescript", "rust", "go", "java", "c#",
    "fastapi", "django", "flask", "node", "express", "next.js", "nuxt",
]
