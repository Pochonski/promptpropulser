"""PromptPropulserClaude CLI — /ppc <mode> <prompt>

Modes: basic | reflection | code | architect | brutal | focus | teacher | compress

Flags:
  --run               Optimize + send to Claude + LLM Judge evaluation
  --ab                A/B test: raw prompt vs PPC-optimized
  --retry             Auto-retry with critic re-optimization on failure
  --no-judge          Use keyword critic instead of LLM Judge (faster, no API cost)
  --judge-model M     Judge model (default: claude-haiku-4-5-20251001)
  --api-key KEY       Anthropic API key (or set ANTHROPIC_API_KEY env var)
  --base-url URL      Custom API base URL (for proxies). Also ANTHROPIC_BASE_URL env.
  --model MODEL       Claude model (default: claude-sonnet-4-6)
  --system-prompt     Path to .md system prompt file
  --save-session      Save SessionLog to sessions/ directory
  --verbose           Full analysis output
  --hybrid            Optimized prompt + short summary
  --json              JSON output
  --reinforcement     none | low | medium | aggressive | maximum
  --reflection-depth  0-5
  --compress          Force compression on
  --token-budget      Token budget (default: 4000)
"""

import argparse
import json
import os
import sys

from ppc.schemas.input import InputSchema, InputOptions
from ppc.engine.pipeline import run_pipeline
from ppc.delivery.formatter import format_output

from ppc.integration.anthropic import AnthropicClient, DEFAULT_MODEL
from ppc.loop import run_once, run_until_pass


def _read_system_prompt(path: str | None) -> str | None:
    if not path:
        return None
    if not os.path.isfile(path):
        print(f"Warning: system prompt file not found: {path}", file=sys.stderr)
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _build_input(args) -> InputSchema:
    return InputSchema(
        mode=args.mode,
        prompt=args.prompt,
        options=InputOptions(
            reinforcement_level=args.reinforcement,
            reflection_depth=args.reflection_depth,
            compression=args.compress,
            strict_constraints=True,
            token_budget=args.token_budget,
        ),
    )


def _print_optimized(output, args):
    delivery_mode = (
        "verbose" if args.verbose
        else ("hybrid" if args.hybrid else "transparent")
    )
    user_output = format_output(output, delivery_mode=delivery_mode)

    if args.json_out:
        payload = {
            "optimized_prompt": user_output.optimized_prompt,
            "summary": user_output.summary,
            "metadata": output.to_dict() if args.verbose else {},
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if delivery_mode == "transparent":
            print(user_output.optimized_prompt)
        else:
            if user_output.summary:
                print(f"--- SUMMARY ---\n{user_output.summary}\n")
            print("--- OPTIMIZED PROMPT ---")
            print(user_output.optimized_prompt)
            if user_output.metadata and delivery_mode == "verbose":
                print("\n--- METADATA ---")
                print(json.dumps(user_output.metadata, indent=2, ensure_ascii=False))


def _print_critic_scores(scores):
    for i, s in enumerate(scores, 1):
        print(
            f"  Attempt {i}: "
            f"constraint={s.constraint_following} "
            f"clarity={s.clarity} "
            f"accuracy={s.accuracy} "
            f"efficiency={s.efficiency} "
            f"| avg={s.average():.1f}"
        )


def cmd_run(args):
    client = AnthropicClient(api_key=args.api_key, model=args.model, base_url=args.base_url)
    judge_client = AnthropicClient(api_key=args.api_key, model=args.judge_model, base_url=args.base_url) if not args.no_judge else None
    system_prompt = _read_system_prompt(args.system_prompt)
    input_schema = _build_input(args)

    result = run_once(
        input_schema,
        client,
        system_prompt=system_prompt,
        max_tokens=args.token_budget,
        judge_client=judge_client,
    )

    print("=" * 60)
    print("  CLAUDE RESPONSE")
    print("=" * 60)
    print(result.final_response)

    print("\n" + "=" * 60)
    print("  CRITIC EVALUATION")
    print("=" * 60)
    _print_critic_scores(result.all_critic_scores)

    if result.session_log.detected_failures:
        print("\nIssues found:")
        for issue in result.session_log.detected_failures:
            print(f"  - {issue}")

    print(f"\nStatus: {'PASSED' if result.passed_critic else 'NEEDS REVIEW'}")

    if args.save_session:
        from ppc.session_store import save_log
        path = save_log(result.session_log)
        print(f"Session saved: {path}")


def cmd_ab(args):
    client = AnthropicClient(api_key=args.api_key, model=args.model, base_url=args.base_url)
    judge_client = AnthropicClient(api_key=args.api_key, model=args.judge_model, base_url=args.base_url) if not args.no_judge else None
    system_prompt = _read_system_prompt(args.system_prompt)

    print("=" * 60)
    print("  A/B TEST: RAW vs PPC-OPTIMIZED")
    print("=" * 60)

    raw_schema = InputSchema(mode=args.mode, prompt=args.prompt)
    raw_output = run_pipeline(raw_schema)
    raw_prompt = raw_schema.prompt

    print("\n--- TEST A: RAW PROMPT ---")
    print(f"Prompt: {raw_prompt[:200]}{'...' if len(raw_prompt) > 200 else ''}")

    try:
        raw_response = client.generate(
            prompt=raw_prompt,
            system_prompt=system_prompt,
            max_tokens=args.token_budget,
        )
        print(f"\nResponse ({raw_response.output_tokens} tokens):")
        print(raw_response.text[:500])
        if len(raw_response.text) > 500:
            print("...")
    except Exception as e:
        print(f"\nLLM Error: {e}")
        raw_response = None

    print("\n--- TEST B: PPC-OPTIMIZED ---")
    opt_schema = _build_input(args)
    opt_result = run_once(
        opt_schema, client,
        system_prompt=system_prompt,
        max_tokens=args.token_budget,
        judge_client=judge_client,
    )
    print(f"Optimized prompt ({opt_result.session_log.optimized_prompt_v1.split().__len__()} tokens)")
    print(f"\nResponse:")
    print(opt_result.final_response[:500])
    if len(opt_result.final_response) > 500:
        print("...")

    print("\n--- CRITIC COMPARISON ---")
    print(f"{'Metric':<20} {'RAW':>8} {'PPC':>8}")
    print("-" * 38)
    if raw_response:
        from ppc.reflection.critic import evaluate_response
        from ppc.schemas.output import DetectedConstraints
        raw_critic = evaluate_response(
            raw_response.text, args.prompt, raw_prompt, DetectedConstraints(),
        )
        ppc_critic_result = opt_result.session_log.critic_score
        for metric in ["constraint_following", "clarity", "accuracy", "efficiency"]:
            raw_val = getattr(raw_critic.score, metric, 0)
            ppc_val = getattr(ppc_critic_result, metric, 0)
            delta = ppc_val - raw_val
            sign = "+" if delta > 0 else ""
            print(f"{metric:<20} {raw_val:>8} {f'{sign}{ppc_val}':>8}")
        print(f"{'avg':<20} {raw_critic.score.average():>8.1f} {ppc_critic_result.average():>8.1f}")

    if args.save_session:
        from ppc.session_store import save_log
        path = save_log(opt_result.session_log)
        print(f"\nSession saved: {path}")


def cmd_retry(args):
    client = AnthropicClient(api_key=args.api_key, model=args.model, base_url=args.base_url)
    judge_client = AnthropicClient(api_key=args.api_key, model=args.judge_model, base_url=args.base_url) if not args.no_judge else None
    system_prompt = _read_system_prompt(args.system_prompt)
    input_schema = _build_input(args)

    print("=" * 60)
    print("  SELF-IMPROVEMENT LOOP (max 3 retries)")
    print("=" * 60)

    result = run_until_pass(
        input_schema, client,
        system_prompt=system_prompt,
        max_tokens=args.token_budget,
        max_retries=3,
        judge_client=judge_client,
    )

    print(f"\nAttempts: {result.attempts}")

    print("\n--- CRITIC SCORES ---")
    _print_critic_scores(result.all_critic_scores)

    print("\n" + "=" * 60)
    print("  FINAL RESPONSE")
    print("=" * 60)
    print(result.final_response)

    if result.session_log.detected_failures:
        print("\nRemaining issues:")
        for issue in result.session_log.detected_failures:
            print(f"  - {issue}")

    print(f"\nStatus: {'PASSED' if result.passed_critic else 'FAILED AFTER RETRIES'}")

    if args.save_session:
        from ppc.session_store import save_log
        path = save_log(result.session_log)
        print(f"Session saved: {path}")


def main():
    parser = argparse.ArgumentParser(
        prog="ppc",
        description="PromptPropulserClaude — Contextual cognition orchestration for LLMs",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="basic",
        choices=["basic", "reflection", "code", "architect", "brutal", "focus", "teacher", "compress"],
        help="Execution mode (default: basic)",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="",
        help="The prompt to optimize. Use quotes for multi-word prompts.",
    )
    parser.add_argument(
        "--reinforcement",
        default="medium",
        choices=["none", "low", "medium", "aggressive", "maximum"],
        help="Reinforcement intensity (default: medium)",
    )
    parser.add_argument(
        "--reflection-depth",
        type=int,
        default=0,
        choices=range(0, 6),
        help="Reflection depth 0-5 (default: 0, auto-detected per mode)",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Force compression on",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output with full analysis",
    )
    parser.add_argument(
        "--hybrid",
        action="store_true",
        help="Show optimized prompt + short summary",
    )
    parser.add_argument(
        "--json",
        dest="json_out",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--token-budget",
        type=int,
        default=4000,
        help="Token budget (default: 4000)",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Optimize + send to Claude + show response + critic",
    )
    parser.add_argument(
        "--ab",
        action="store_true",
        help="A/B test: raw prompt vs PPC-optimized with critic scores",
    )
    parser.add_argument(
        "--retry",
        action="store_true",
        help="Self-improvement loop with auto-regeneration on critic failure",
    )
    parser.add_argument(
        "--api-key",
        default="",
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="Custom API base URL (for proxies like OpenCode Go). "
             "Can also set ANTHROPIC_BASE_URL env var.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Claude model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--system-prompt",
        default="",
        help="Path to .md system prompt file to send to Claude",
    )
    parser.add_argument(
        "--save-session",
        dest="save_session",
        action="store_true",
        help="Save SessionLog to sessions/ directory",
    )
    parser.add_argument(
        "--no-judge",
        dest="no_judge",
        action="store_true",
        help="Use fast keyword critic instead of LLM Judge.",
    )
    parser.add_argument(
        "--judge-model",
        default="claude-haiku-4-5-20251001",
        help="Model for LLM Judge (default: claude-haiku-4-5-20251001)",
    )

    args = parser.parse_args()

    if not args.prompt:
        if not sys.stdin.isatty():
            args.prompt = sys.stdin.read().strip()
        if not args.prompt:
            parser.print_help()
            print("\nError: prompt is required.")
            sys.exit(1)

    if args.api_key:
        os.environ.setdefault("ANTHROPIC_API_KEY", args.api_key)

    try:
        if args.retry:
            cmd_retry(args)
        elif args.ab:
            cmd_ab(args)
        elif args.run:
            cmd_run(args)
        else:
            input_schema = _build_input(args)
            output = run_pipeline(input_schema)
            _print_optimized(output, args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        if "anthropic" in str(e).lower():
            print("Error: anthropic SDK not installed. Run: pip install anthropic", file=sys.stderr)
        else:
            print(f"Import error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
