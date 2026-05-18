"""
Post-Response Critic Engine — Section 9, 10

Evaluates generated responses against:
  - constraint adherence
  - clarity
  - accuracy
  - efficiency

Also performs failure analysis and outputs a scored critique.
"""

from dataclasses import dataclass, field

from ppc.schemas.output import DetectedConstraints
from ppc.schemas.session_log import CriticScore


@dataclass
class CriticResult:
    score: CriticScore
    issues: list[str]
    recommendation: str
    needs_regeneration: bool


SEMANTIC_VIOLATION_MAP: dict[str, list[str]] = {
    "base de datos": [
        "sqlalchemy", "sqlite", "postgresql", "postgres", "mysql", "mariadb",
        "mongodb", "redis", "orm", "prisma", "django orm", "database", "db",
        "create table", "insert into", "select ", "migraci",
    ],
    "docker": ["docker", "dockerfile", "docker-compose", "container"],
    "react": ["react", "jsx", "next.js", "nextjs", "componentdidmount", "usestate", "useeffect"],
    "orm": ["sqlalchemy", "prisma", "django orm", "typeorm", "sequelize", "eloquent"],
    "frontend": ["react", "vue", "angular", "svelte", "frontend", "css", "html"],
    "librerias externas": ["pip install", "npm install", "yarn add", "import "],
}


def _check_constraint_adherence(
    response: str,
    constraints: DetectedConstraints,
) -> tuple[int, list[str]]:
    score = 10
    issues: list[str] = []
    response_lower = response.lower()

    for c in constraints.locked:
        c_lower = c.lower()
        negative_patterns = [
            "no uses", "no usar", "sin", "evita", "prohibido",
            "nunca", "no cambies", "no agregues",
        ]
        for pat in negative_patterns:
            if pat in c_lower:
                subject = c_lower.split(pat, 1)[-1].strip()
                if subject and subject in response_lower:
                    score -= 2
                    issues.append(
                        f"Possible violation: included '{subject}' "
                        f"despite constraint '{c[:60]}'"
                    )
                else:
                    expanded = SEMANTIC_VIOLATION_MAP.get(subject, [])
                    for kw in expanded:
                        if kw in response_lower:
                            score -= 2
                            issues.append(
                                f"Possible violation: '{kw}' detected in response "
                                f"violates constraint '{c[:60]}'"
                            )
                            break
                break

    for c in constraints.locked:
        c_lower = c.lower()
        positive_patterns = ["debe", "obligatorio", "requerido", "usa", "usar"]
        for pat in positive_patterns:
            if pat in c_lower:
                subject = c_lower.split(pat, 1)[-1].strip()
                if subject and subject not in response_lower:
                    score -= 1
                    issues.append(
                        f"Missing required element: '{subject}' "
                        f"from constraint '{c[:60]}'"
                    )
                break

    return max(1, score), issues


def _check_clarity(response: str) -> tuple[int, list[str]]:
    score = 10
    issues: list[str] = []
    tokens = response.split()

    if len(tokens) < 5 and len(response) > 0:
        score -= 3
        issues.append("Response may be too short to be useful.")

    sentences = response.replace("!", ".").replace("?", ".").split(".")
    long_sentences = [s for s in sentences if len(s.split()) > 60]
    if long_sentences:
        score -= len(long_sentences)
        issues.append(f"Found {len(long_sentences)} very long sentences. Consider breaking them up.")

    return max(1, score), issues


def _check_accuracy(response: str, prompt: str) -> tuple[int, list[str]]:
    score = 10
    issues: list[str] = []
    response_lower = response.lower()
    prompt_lower = prompt.lower()

    hallucination_markers = [
        "as an ai", "as a language model", "i cannot", "i'm unable",
        "i don't have", "i am not able", "lo siento", "no puedo",
        "como ia", "como modelo de lenguaje",
    ]
    for marker in hallucination_markers:
        if marker in response_lower:
            score -= 1
            issues.append("Response contains refusal/disclaimer phrasing.")

    if "?" in prompt and "?" not in response_lower and len(response) > 0:
        pass

    return max(1, score), issues


def _check_efficiency(response: str) -> tuple[int, list[str]]:
    score = 10
    issues: list[str] = []
    tokens = len(response.split())

    if tokens > 2000:
        score -= 3
        issues.append("Response is very large. Consider summarizing.")
    elif tokens > 1000:
        score -= 1
        issues.append("Response is moderately large.")

    filler_phrases = [
        "en conclusi\u00f3n", "en resumen", "para finalizar",
        "cabe destacar", "es importante mencionar", "vale la pena se\u00f1alar",
    ]
    filler_count = sum(1 for fp in filler_phrases if fp in response.lower())
    if filler_count > 3:
        score -= 1
        issues.append("Excessive filler/closing phrases.")

    return max(1, score), issues


def evaluate_response(
    response: str,
    original_prompt: str,
    optimized_prompt: str,
    constraints: DetectedConstraints,
) -> CriticResult:
    if not response.strip():
        return CriticResult(
            score=CriticScore(0, 0, 0, 0),
            issues=["Empty response."],
            recommendation="Regenerate. Response is empty.",
            needs_regeneration=True,
        )

    c_score, c_issues = _check_constraint_adherence(response, constraints)
    a_score, a_issues = _check_accuracy(response, original_prompt)
    q_score, q_issues = _check_clarity(response)
    e_score, e_issues = _check_efficiency(response)

    score = CriticScore(
        constraint_following=max(1, c_score),
        clarity=max(1, q_score),
        accuracy=max(1, a_score),
        efficiency=max(1, e_score),
    )

    all_issues = c_issues + q_issues + a_issues + e_issues

    needs_regeneration = score.constraint_following <= 3 or score.accuracy <= 3

    if needs_regeneration:
        recommendation = "CRITICAL: Regenerate response. Constraint or accuracy failure detected."
    elif all_issues:
        recommendation = f"Minor issues found ({len(all_issues)}). Review suggested."
    else:
        recommendation = "Response passed all critic checks."

    return CriticResult(
        score=score,
        issues=all_issues,
        recommendation=recommendation,
        needs_regeneration=needs_regeneration,
    )
