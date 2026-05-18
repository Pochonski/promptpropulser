"""
Pipeline Executor — assembles and runs the full optimization chain
based on the execution plan from the orchestrator.
"""

from ppc.schemas.input import InputSchema
from ppc.schemas.output import (
    OutputSchema,
    AnalyzedIntent,
    DetectedConstraints,
    AppliedReinforcement,
    ReflectionResult as OutputReflection,
    TokenUsage,
)

from ppc.engine.orchestrator import build_execution_plan, ExecutionPlan
from ppc.analyzers.intent import analyze_intent
from ppc.analyzers.constraint import detect_constraints
from ppc.analyzers.complexity import compute_complexity

from ppc.transformers.lock import apply_constraint_lock
from ppc.transformers.echo import generate_echoes
from ppc.transformers.reinforcement import (
    apply_reinforcement,
    determine_reinforcement_level,
    count_applied_patterns,
)
from ppc.transformers.compress import compress_prompt, estimate_tokens

from ppc.reflection.pipeline import run_reflection


def _estimate_tokens_local(text: str) -> int:
    return len(text.split())


def run_pipeline(input_schema: InputSchema) -> OutputSchema:
    input_schema.validate()

    prompt = input_schema.prompt.strip()
    input_tokens = _estimate_tokens_local(prompt)

    intent = analyze_intent(input_schema)
    constraints = detect_constraints(prompt)
    complexity = compute_complexity(prompt, input_tokens, intent, constraints)

    plan = build_execution_plan(input_schema)

    optimization_tokens = 0
    system_instructions = ""

    use_system_channel = plan.mode_config.constraint_channel == "system"

    if use_system_channel:
        lock_block = apply_constraint_lock(
            prompt,
            constraints,
            plan.effective_lock,
        )

        lock_only = lock_block[:lock_block.find("\n---\n")] if "\n---\n" in lock_block else lock_block
        if lock_only.startswith("LOCKED CONSTRAINTS"):
            system_instructions = lock_only

        if plan.effective_lock in ("aggressive", "maximum") and lock_block.rfind("REMINDER:") > 0:
            bottom_parts = lock_block[lock_block.rfind("\n\nRE"):] if "\n\nRE" in lock_block else ""
            bottom_parts = bottom_parts or lock_block[lock_block.rfind("\n\n==="):] if "\n\n===" in lock_block else ""
            if bottom_parts:
                system_instructions = system_instructions + bottom_parts

        locked_prompt = prompt
        optimization_tokens += _estimate_tokens_local(system_instructions)
    else:
        locked_prompt = apply_constraint_lock(
            prompt,
            constraints,
            plan.effective_lock,
        )

    echoes = generate_echoes(constraints, plan.effective_echo)
    echo_block = ""
    if echoes:
        if use_system_channel:
            system_instructions += "\n\n" + "\n".join(f"[ECHO] {e}" for e in echoes)
        else:
            echo_block = "\n".join(f"[ECHO] {e}" for e in echoes)
        optimization_tokens += _estimate_tokens_local(echo_block or system_instructions)

    reinforcement_level = determine_reinforcement_level(
        plan.mode_config,
        complexity.score,
        len(constraints.locked),
        input_schema.options.reinforcement_level
        if input_schema.options.reinforcement_level != "medium"
        else None,
    )

    optimized = apply_reinforcement(
        locked_prompt,
        intent,
        constraints,
        plan.mode_config,
        reinforcement_level,
        "" if use_system_channel else echo_block,
    )
    optimization_tokens += _estimate_tokens_local(optimized) - input_tokens

    if plan.effective_compression in ("maximum", "optional"):
        if plan.effective_compression == "maximum" or input_tokens > 2500:
            optimized = compress_prompt(optimized, intent.primary_goal, constraints.locked)

    final_tokens = _estimate_tokens_local(optimized)

    reflection_enabled = plan.effective_reflection_depth > 0
    reflection_result = None
    if reflection_enabled:
        reflection_result = run_reflection(
            intent,
            constraints,
            optimized,
            depth=plan.effective_reflection_depth,
        )

    applied_patterns = count_applied_patterns(reinforcement_level)
    if echoes:
        applied_patterns.append("semantic_echo")
    if use_system_channel:
        applied_patterns.append("system_channel")

    return OutputSchema(
        analyzed_intent=AnalyzedIntent(
            primary_goal=intent.primary_goal,
            secondary_goals=intent.secondary_goals,
            complexity_score=complexity.score,
        ),
        constraints=constraints,
        reinforcement=AppliedReinforcement(
            level=reinforcement_level,
            applied_patterns=applied_patterns,
        ),
        semantic_echoes=echoes,
        optimized_prompt=optimized,
        system_instructions=system_instructions.strip(),
        reflection=OutputReflection(
            enabled=reflection_enabled,
            stage_results=list(reflection_result.stage_results.values())
            if reflection_result
            else [],
            critic_notes=reflection_result.issues_found
            if reflection_result
            else [],
        ),
        token_usage=TokenUsage(
            input_tokens=input_tokens,
            optimization_tokens=max(0, optimization_tokens),
            final_prompt_tokens=final_tokens,
        ),
    )
