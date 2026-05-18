"""
Reflection Pipeline — Section 9

Four-stage self-evaluation engine:
  1. Intent Validation
  2. Constraint Validation
  3. Quality Analysis
  4. Failure Simulation
"""

from dataclasses import dataclass, field

from ppc.schemas.output import DetectedConstraints
from ppc.analyzers.intent import IntentResult


@dataclass
class ReflectionResult:
    stage_results: dict[str, str]
    passed: bool
    issues_found: list[str]
    suggestions: list[str]


def _validate_intent(
    original_intent: IntentResult,
    optimized_prompt: str,
) -> tuple[bool, str]:
    primary = original_intent.primary_goal
    if primary and primary != "general_query":
        if primary.replace("_", " ").lower() not in optimized_prompt.lower():
            return (
                False,
                f"Primary intent '{primary}' may have been lost in optimization. "
                f"Reinforce the core task.",
            )
    return True, "Intent preserved."


def _validate_constraints(
    constraints: DetectedConstraints,
    optimized_prompt: str,
) -> tuple[bool, list[str]]:
    issues = []
    for locked in constraints.locked:
        key_terms = locked.lower().split()
        key_words = [w for w in key_terms if len(w) > 3]
        if key_words and not any(kw in optimized_prompt.lower() for kw in key_words[:2]):
            issues.append(f"Locked constraint may be missing: '{locked[:80]}'")
    return len(issues) == 0, issues


def _analyze_quality(optimized_prompt: str) -> list[str]:
    notes = []
    tokens = len(optimized_prompt.split())

    if tokens < 10:
        notes.append("Prompt is very short. Ensure critical instructions are preserved.")
    if tokens > 3000:
        notes.append("Prompt is large. Consider compression for efficiency.")

    repetitions: dict[str, int] = {}
    for line in optimized_prompt.split("\n"):
        stripped = line.strip().lower()
        if len(stripped) > 10:
            repetitions[stripped] = repetitions.get(stripped, 0) + 1
    over_repeated = [k for k, v in repetitions.items() if v > 3]
    if over_repeated:
        notes.append(f"Found {len(over_repeated)} over-repeated lines. Consider trimming.")

    if not notes:
        notes.append("Quality check passed.")
    return notes


def _simulate_failure(constraints: DetectedConstraints) -> list[str]:
    scenarios = []
    if constraints.locked:
        scenarios.append(
            "What if a locked constraint is violated? "
            "Would the output still be valid?"
        )
    if len(constraints.locked) > 3:
        scenarios.append(
            "Multiple constraints increase failure surface. "
            "Check for constraint conflicts."
        )
    if not scenarios:
        scenarios.append("No obvious failure scenarios detected.")
    return scenarios


def run_reflection(
    intent: IntentResult,
    constraints: DetectedConstraints,
    optimized_prompt: str,
    depth: int,
) -> ReflectionResult:
    stage_results: dict[str, str] = {}
    all_issues: list[str] = []
    suggestions: list[str] = []

    if depth >= 1:
        ok, msg = _validate_intent(intent, optimized_prompt)
        stage_results["intent_validation"] = msg
        if not ok:
            all_issues.append(msg)

    if depth >= 2:
        ok, issues = _validate_constraints(constraints, optimized_prompt)
        stage_results["constraint_validation"] = (
            "Passed" if ok else f"Issues: {len(issues)}"
        )
        all_issues.extend(issues)

    if depth >= 3:
        notes = _analyze_quality(optimized_prompt)
        stage_results["quality_analysis"] = "; ".join(notes)
        suggestions.extend(notes)

    if depth >= 4:
        scenarios = _simulate_failure(constraints)
        stage_results["failure_simulation"] = "; ".join(scenarios)
        suggestions.extend(scenarios)

    return ReflectionResult(
        stage_results=stage_results,
        passed=len(all_issues) == 0,
        issues_found=all_issues,
        suggestions=suggestions,
    )
