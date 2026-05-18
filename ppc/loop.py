"""
Self-Improvement Loop — pipeline + LLM + critic + optional retry.

Core of the PromptPropulserClaude runtime integration with Claude.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field

from ppc.schemas.input import InputSchema
from ppc.schemas.output import OutputSchema
from ppc.schemas.session_log import SessionLog, CriticScore

from ppc.engine.pipeline import run_pipeline
from ppc.reflection.critic import evaluate_response, CriticResult
from ppc.critic_llm import llm_evaluate_response

from ppc.integration.base import BaseLLMClient, LLMResponse
from ppc.session_store import save_log


@dataclass
class LoopResult:
    session_log: SessionLog
    final_response: str
    attempts: int
    passed_critic: bool
    all_critic_scores: list[CriticScore] = field(default_factory=list)


def _llm_response_to_text(response: LLMResponse | None) -> str:
    if response is None:
        return ""
    return response.text


def _get_critic(
    response: str,
    original_prompt: str,
    optimized_prompt: str,
    constraints,
    judge_client: BaseLLMClient | None = None,
) -> CriticResult:
    if judge_client is not None:
        return llm_evaluate_response(
            response, original_prompt, constraints, judge_client,
        )
    return evaluate_response(
        response, original_prompt, optimized_prompt, constraints,
    )


def run_once(
    input_schema: InputSchema,
    client: BaseLLMClient,
    system_prompt: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    judge_client: BaseLLMClient | None = None,
) -> LoopResult:
    output: OutputSchema = run_pipeline(input_schema)

    effective_system = system_prompt or ""
    if output.system_instructions:
        effective_system = (
            f"{output.system_instructions}\n\n{effective_system}"
            if effective_system
            else output.system_instructions
        )

    llm_response: LLMResponse | None = None
    response_text = ""

    try:
        llm_response = client.generate(
            prompt=output.optimized_prompt,
            system_prompt=effective_system or None,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        response_text = llm_response.text
    except Exception as e:
        response_text = f"[LLM ERROR: {e}]"

    critic: CriticResult = _get_critic(
        response=response_text,
        original_prompt=input_schema.prompt,
        optimized_prompt=output.optimized_prompt,
        constraints=output.constraints,
        judge_client=judge_client,
    )

    session_log = SessionLog(
        session_id=uuid.uuid4().hex[:12],
        original_prompt=input_schema.prompt,
        optimized_prompt_v1=output.optimized_prompt,
        llm_output_v1=response_text,
        critic_score=critic.score,
        detected_failures=critic.issues,
        optimized_prompt_v2="",
        timestamp=datetime.now().isoformat(),
        mode_used=input_schema.mode,
        complexity_at_start=output.analyzed_intent.complexity_score,
    )

    return LoopResult(
        session_log=session_log,
        final_response=response_text,
        attempts=1,
        passed_critic=not critic.needs_regeneration,
        all_critic_scores=[critic.score],
    )


def run_until_pass(
    input_schema: InputSchema,
    client: BaseLLMClient,
    system_prompt: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    max_retries: int = 3,
    judge_client: BaseLLMClient | None = None,
) -> LoopResult:
    first = run_once(
        input_schema, client, system_prompt, max_tokens, temperature,
        judge_client=judge_client,
    )
    if first.passed_critic or max_retries <= 1:
        return first

    all_scores = list(first.all_critic_scores)
    last_log = first.session_log
    final_response = first.final_response

    for attempt in range(2, max_retries + 1):
        input_schema.options.strict_constraints = True

        if last_log.critic_score.constraint_following <= 5:
            input_schema.mode = "focus"

        retry_output: OutputSchema = run_pipeline(input_schema)

        retry_system = system_prompt or ""
        if retry_output.system_instructions:
            retry_system = (
                f"{retry_output.system_instructions}\n\n{retry_system}"
                if retry_system
                else retry_output.system_instructions
            )

        try:
            llm_response = client.generate(
                prompt=retry_output.optimized_prompt,
                system_prompt=retry_system or None,
                max_tokens=max_tokens,
                temperature=min(0.3, temperature),
            )
            final_response = llm_response.text
        except Exception as e:
            final_response = f"[LLM ERROR on retry {attempt}: {e}]"
            break

        critic = _get_critic(
            response=final_response,
            original_prompt=input_schema.prompt,
            optimized_prompt=retry_output.optimized_prompt,
            constraints=retry_output.constraints,
            judge_client=judge_client,
        )

        all_scores.append(critic.score)

        last_log = SessionLog(
            session_id=first.session_log.session_id,
            original_prompt=input_schema.prompt,
            optimized_prompt_v1=first.session_log.optimized_prompt_v1,
            llm_output_v1=first.session_log.llm_output_v1,
            critic_score=first.session_log.critic_score,
            detected_failures=critic.issues,
            optimized_prompt_v2=retry_output.optimized_prompt,
            timestamp=datetime.now().isoformat(),
            mode_used=input_schema.mode,
            complexity_at_start=first.session_log.complexity_at_start,
        )

        if not critic.needs_regeneration:
            break

    return LoopResult(
        session_log=last_log,
        final_response=final_response,
        attempts=attempt,
        passed_critic=not critic.needs_regeneration if 'critic' in dir() else False,
        all_critic_scores=all_scores,
    )
