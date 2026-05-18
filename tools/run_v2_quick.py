"""Quick benchmark: 12 hardest v2 prompts"""
import json, time
from ppc.integration.anthropic import AnthropicClient
from ppc.benchmark import run_benchmark, save_report, format_report_text, PromptResult, BenchmarkReport, DetectedConstraints
from ppc.critic_llm import llm_evaluate_response
from ppc.loop import run_once
from ppc.schemas.input import InputSchema

BENCHMARK_SUBSET = [
    "reflection_02", "code_01", "code_02", "code_03",
    "architect_01", "brutal_01", "brutal_03",
    "focus_01", "focus_03", "teacher_01", "teacher_03",
    "compress_01",
]

with open("data/benchmark_v2_prompts.json", encoding="utf-8") as f:
    all_prompts = json.load(f)["prompts"]

prompts = [p for p in all_prompts if p["id"] in BENCHMARK_SUBSET]

client = AnthropicClient()
judge_client = AnthropicClient()

results = []
for i, item in enumerate(prompts):
    pid = item["id"]
    mode = item["mode"]
    prompt_text = item["prompt"]
    print(f"[{i+1}/{len(prompts)}] {pid} ({mode})", end=" ", flush=True)

    result = PromptResult(id=pid, mode=mode, prompt=prompt_text, raw_prompt_tokens=len(prompt_text.split()))

    try:
        raw_resp = client.generate(prompt=prompt_text, max_tokens=1500, temperature=0.7)
        raw_critic = llm_evaluate_response(raw_resp.text, prompt_text, DetectedConstraints(), judge_client)
        result.raw_critic = {
            "constraint_following": raw_critic.score.constraint_following,
            "accuracy": raw_critic.score.accuracy,
            "clarity": raw_critic.score.clarity,
            "efficiency": raw_critic.score.efficiency,
        }
        result.raw_response_tokens = raw_resp.output_tokens
    except Exception as e:
        result.raw_error = str(e)
        result.raw_critic = {"constraint_following": 0, "accuracy": 0, "clarity": 0, "efficiency": 0}

    time.sleep(0.3)

    try:
        schema = InputSchema(mode=mode, prompt=prompt_text)
        loop_result = run_once(schema, client, max_tokens=1500, judge_client=judge_client)
        ppc_score = loop_result.session_log.critic_score
        result.ppc_critic = {
            "constraint_following": ppc_score.constraint_following,
            "accuracy": ppc_score.accuracy,
            "clarity": ppc_score.clarity,
            "efficiency": ppc_score.efficiency,
        }
        result.ppc_response_tokens = len(loop_result.final_response.split())
        result.ppc_prompt_tokens = len(loop_result.session_log.optimized_prompt_v1.split())
    except Exception as e:
        result.ppc_error = str(e)
        result.ppc_critic = {"constraint_following": 0, "accuracy": 0, "clarity": 0, "efficiency": 0}

    raw_avg = sum(result.raw_critic.values()) / 4.0
    ppc_avg = sum(result.ppc_critic.values()) / 4.0
    delta = ppc_avg - raw_avg
    sign = "+" if delta > 0 else ""
    print(f"RAW={raw_avg:.1f} PPC={ppc_avg:.1f} Delta={sign}{delta:.1f}")
    results.append(result)

from datetime import datetime
mode_summary = {}
for mode in sorted(set(r.mode for r in results)):
    mode_results = [r for r in results if r.mode == mode]
    mode_summary[mode] = {
        "count": len(mode_results),
        "raw_avg": sum(sum(r.raw_critic.values())/4.0 for r in mode_results) / len(mode_results),
        "ppc_avg": sum(sum(r.ppc_critic.values())/4.0 for r in mode_results) / len(mode_results),
        "ppc_wins": sum(1 for r in mode_results if sum(r.ppc_critic.values()) > sum(r.raw_critic.values())),
    }

report = BenchmarkReport(results=results, mode_summary=mode_summary, overall={
    "total_prompts": len(results),
    "ppc_win_rate": sum(1 for r in results if sum(r.ppc_critic.values()) > sum(r.raw_critic.values())) / len(results),
    "constraint_delta": sum(r.ppc_critic["constraint_following"] - r.raw_critic["constraint_following"] for r in results) / len(results),
    "accuracy_delta": sum(r.ppc_critic["accuracy"] - r.raw_critic["accuracy"] for r in results) / len(results),
    "clarity_delta": sum(r.ppc_critic["clarity"] - r.raw_critic["clarity"] for r in results) / len(results),
    "efficiency_delta": sum(r.ppc_critic["efficiency"] - r.raw_critic["efficiency"] for r in results) / len(results),
}, timestamp=datetime.now().isoformat())

save_report(report, "data/benchmark_v2_subset_results.json")
print()
print(format_report_text(report))
