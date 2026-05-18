"""
Benchmark Runner — raw vs PPC comparison across 24 prompts.

Computes composite metrics:
  - Constraint adherence delta
  - Accuracy delta
  - Conciseness (token reduction %)
  - Hallucination rate (accuracy score below threshold)
  - Overall quality improvement per mode
"""

import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

from ppc.schemas.input import InputSchema
from ppc.integration.anthropic import AnthropicClient
from ppc.integration.base import BaseLLMClient
from ppc.loop import run_once
from ppc.reflection.critic import evaluate_response
from ppc.critic_llm import llm_evaluate_response
from ppc.schemas.output import DetectedConstraints


BENCHMARK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "benchmark_prompts.json",
)

BENCHMARK_V2_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "benchmark_v2_prompts.json",
)


@dataclass
class PromptResult:
    id: str
    mode: str
    prompt: str
    raw_critic: dict = field(default_factory=dict)
    ppc_critic: dict = field(default_factory=dict)
    raw_response_tokens: int = 0
    ppc_response_tokens: int = 0
    ppc_prompt_tokens: int = 0
    raw_prompt_tokens: int = 0
    raw_error: str = ""
    ppc_error: str = ""
    ppc_mode_used: str = ""


@dataclass
class BenchmarkReport:
    results: list[PromptResult] = field(default_factory=list)
    mode_summary: dict[str, dict] = field(default_factory=dict)
    overall: dict = field(default_factory=dict)
    timestamp: str = ""

    def avg_constraint_delta(self) -> float:
        deltas = []
        for r in self.results:
            raw = r.raw_critic.get("constraint_following", 0)
            ppc = r.ppc_critic.get("constraint_following", 0)
            deltas.append(ppc - raw)
        return sum(deltas) / len(deltas) if deltas else 0.0

    def avg_accuracy_delta(self) -> float:
        deltas = []
        for r in self.results:
            raw = r.raw_critic.get("accuracy", 0)
            ppc = r.ppc_critic.get("accuracy", 0)
            deltas.append(ppc - raw)
        return sum(deltas) / len(deltas) if deltas else 0.0

    def avg_clarity_delta(self) -> float:
        deltas = []
        for r in self.results:
            raw = r.raw_critic.get("clarity", 0)
            ppc = r.ppc_critic.get("clarity", 0)
            deltas.append(ppc - raw)
        return sum(deltas) / len(deltas) if deltas else 0.0

    def avg_efficiency_delta(self) -> float:
        deltas = []
        for r in self.results:
            raw = r.raw_critic.get("efficiency", 0)
            ppc = r.ppc_critic.get("efficiency", 0)
            deltas.append(ppc - raw)
        return sum(deltas) / len(deltas) if deltas else 0.0

    def ppc_win_rate(self) -> float:
        wins = 0
        for r in self.results:
            raw_avg = (
                r.raw_critic.get("constraint_following", 0)
                + r.raw_critic.get("accuracy", 0)
                + r.raw_critic.get("clarity", 0)
                + r.raw_critic.get("efficiency", 0)
            ) / 4.0
            ppc_avg = (
                r.ppc_critic.get("constraint_following", 0)
                + r.ppc_critic.get("accuracy", 0)
                + r.ppc_critic.get("clarity", 0)
                + r.ppc_critic.get("efficiency", 0)
            ) / 4.0
            if ppc_avg > raw_avg:
                wins += 1
        return wins / len(self.results) if self.results else 0.0

    def improvement_summary(self) -> str:
        return (
            f"Benchmark Results ({len(self.results)} prompts):\n"
            f"  PPC Win Rate: {self.ppc_win_rate():.1%}\n"
            f"  Constraint Adherence Delta: {self.avg_constraint_delta():+.2f}\n"
            f"  Accuracy Delta:           {self.avg_accuracy_delta():+.2f}\n"
            f"  Clarity Delta:            {self.avg_clarity_delta():+.2f}\n"
            f"  Efficiency Delta:         {self.avg_efficiency_delta():+.2f}"
        )


def load_benchmark(path: str = BENCHMARK_PATH) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["prompts"]


def run_benchmark(
    client: AnthropicClient,
    system_prompt: str | None = None,
    max_tokens: int = 2048,
    verbose: bool = False,
    judge_client: BaseLLMClient | None = None,
    benchmark_path: str = BENCHMARK_PATH,
) -> BenchmarkReport:
    prompts = load_benchmark(benchmark_path)
    results: list[PromptResult] = []

    print(f"Running benchmark: {len(prompts)} prompts across {len(set(p['mode'] for p in prompts))} modes")
    print("=" * 60)

    for i, item in enumerate(prompts):
        pid = item["id"]
        mode = item["mode"]
        prompt_text = item["prompt"]

        if verbose:
            print(f"\n[{i+1}/{len(prompts)}] {pid} ({mode})")

        result = PromptResult(
            id=pid,
            mode=mode,
            prompt=prompt_text,
            raw_prompt_tokens=len(prompt_text.split()),
        )

        # --- RAW ---
        try:
            raw_response = client.generate(
                prompt=prompt_text,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            if judge_client is not None:
                raw_critic = llm_evaluate_response(
                    raw_response.text, prompt_text, DetectedConstraints(), judge_client,
                )
            else:
                raw_critic = evaluate_response(
                    raw_response.text, prompt_text, prompt_text,
                    DetectedConstraints(),
                )
            result.raw_critic = {
                "constraint_following": raw_critic.score.constraint_following,
                "accuracy": raw_critic.score.accuracy,
                "clarity": raw_critic.score.clarity,
                "efficiency": raw_critic.score.efficiency,
            }
            result.raw_response_tokens = raw_response.output_tokens
        except Exception as e:
            result.raw_error = str(e)
            result.raw_critic = {
                "constraint_following": 0, "accuracy": 0,
                "clarity": 0, "efficiency": 0,
            }

        time.sleep(0.3)

        # --- PPC ---
        try:
            schema = InputSchema(mode=mode, prompt=prompt_text)
            loop_result = run_once(
                schema, client,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                judge_client=judge_client,
            )
            ppc_score = loop_result.session_log.critic_score
            result.ppc_critic = {
                "constraint_following": ppc_score.constraint_following,
                "accuracy": ppc_score.accuracy,
                "clarity": ppc_score.clarity,
                "efficiency": ppc_score.efficiency,
            }
            result.ppc_response_tokens = len(loop_result.final_response.split())
            result.ppc_prompt_tokens = len(
                loop_result.session_log.optimized_prompt_v1.split()
            )
            result.ppc_mode_used = loop_result.session_log.mode_used
        except Exception as e:
            result.ppc_error = str(e)
            result.ppc_critic = {
                "constraint_following": 0, "accuracy": 0,
                "clarity": 0, "efficiency": 0,
            }

        if verbose:
            raw_avg = sum(result.raw_critic.values()) / 4.0
            ppc_avg = sum(result.ppc_critic.values()) / 4.0
            delta = ppc_avg - raw_avg
            sign = "+" if delta > 0 else ""
            print(f"  RAW avg: {raw_avg:.1f} | PPC avg: {ppc_avg:.1f} | Delta: {sign}{delta:.1f}")

        results.append(result)

    mode_summary: dict[str, dict] = {}
    for mode in sorted(set(r.mode for r in results)):
        mode_results = [r for r in results if r.mode == mode]
        mode_summary[mode] = {
            "count": len(mode_results),
            "raw_avg": sum(
                sum(r.raw_critic.values()) / 4.0 for r in mode_results
            ) / len(mode_results),
            "ppc_avg": sum(
                sum(r.ppc_critic.values()) / 4.0 for r in mode_results
            ) / len(mode_results),
            "ppc_wins": sum(
                1 for r in mode_results
                if sum(r.ppc_critic.values()) > sum(r.raw_critic.values())
            ),
        }

    report = BenchmarkReport(
        results=results,
        mode_summary=mode_summary,
        overall={
            "total_prompts": len(results),
            "ppc_win_rate": 0.0,
            "constraint_delta": 0.0,
            "accuracy_delta": 0.0,
            "clarity_delta": 0.0,
            "efficiency_delta": 0.0,
        },
        timestamp=datetime.now().isoformat(),
    )
    report.overall["ppc_win_rate"] = report.ppc_win_rate()
    report.overall["constraint_delta"] = report.avg_constraint_delta()
    report.overall["accuracy_delta"] = report.avg_accuracy_delta()
    report.overall["clarity_delta"] = report.avg_clarity_delta()
    report.overall["efficiency_delta"] = report.avg_efficiency_delta()

    return report


def save_report(report: BenchmarkReport, path: str) -> str:
    report_data = {
        "timestamp": report.timestamp,
        "overall": report.overall,
        "mode_summary": report.mode_summary,
        "results": [
            {
                "id": r.id,
                "mode": r.mode,
                "raw_critic": r.raw_critic,
                "ppc_critic": r.ppc_critic,
                "raw_response_tokens": r.raw_response_tokens,
                "ppc_response_tokens": r.ppc_response_tokens,
                "ppc_prompt_tokens": r.ppc_prompt_tokens,
                "ppc_mode_used": r.ppc_mode_used,
                "raw_error": r.raw_error,
                "ppc_error": r.ppc_error,
            }
            for r in report.results
        ],
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    return path


def format_report_text(report: BenchmarkReport) -> str:
    lines = [
        "=" * 60,
        "  PPC BENCHMARK REPORT",
        "=" * 60,
        f"Timestamp: {report.timestamp}",
        f"Prompts: {report.overall['total_prompts']}",
        "",
        "--- OVERALL ---",
        f"PPC Win Rate:        {report.ppc_win_rate():.1%}",
        f"Constraint Delta:    {report.avg_constraint_delta():+.2f}",
        f"Accuracy Delta:      {report.avg_accuracy_delta():+.2f}",
        f"Clarity Delta:       {report.avg_clarity_delta():+.2f}",
        f"Efficiency Delta:    {report.avg_efficiency_delta():+.2f}",
        "",
        "--- BY MODE ---",
    ]
    for mode, stats in sorted(report.mode_summary.items()):
        delta = stats["ppc_avg"] - stats["raw_avg"]
        sign = "+" if delta > 0 else ""
        lines.append(
            f"  {mode:<12}  RAW={stats['raw_avg']:.1f}  PPC={stats['ppc_avg']:.1f}  "
            f"Delta={sign}{delta:.1f}  Wins={stats['ppc_wins']}/{stats['count']}"
        )

    return "\n".join(lines)
