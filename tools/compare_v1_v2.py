"""Compare v1 and v2 benchmark results."""
import json

with open("data/benchmark_results.json", encoding="utf-8") as f:
    v1 = json.load(f)

with open("data/benchmark_llm_judge_results.json", encoding="utf-8") as f:
    v1_llm = json.load(f)

with open("data/benchmark_v2_subset_results.json", encoding="utf-8") as f:
    v2 = json.load(f)

print("=" * 72)
print("  BENCHMARK v1 vs v2 — COMPARISON")
print("=" * 72)

print("\n--- OVERALL COMPARISON ---")
print(f"{'Metric':<28} {'v1 Keyword':>10} {'v1 LLM':>10} {'v2 LLM':>10}")
print("-" * 60)
metrics = [
    ("PPC Win Rate", "ppc_win_rate", "{:.1%}"),
    ("Constraint Delta", "constraint_delta", "{:+.2f}"),
    ("Accuracy Delta", "accuracy_delta", "{:+.2f}"),
    ("Clarity Delta", "clarity_delta", "{:+.2f}"),
    ("Efficiency Delta", "efficiency_delta", "{:+.2f}"),
]
for label, key, fmt in metrics:
    v1_val = v1["overall"][key]
    v1_llm_val = v1_llm["overall"][key]
    v2_val = v2["overall"][key]
    print(f"{label:<28} {fmt.format(v1_val):>10} {fmt.format(v1_llm_val):>10} {fmt.format(v2_val):>10}")

print("\n--- MODE COMPARISON (LLM Judge only) ---")
print(f"{'Mode':<14} {'v1 RAW':>7} {'v1 PPC':>7} {'v1 Delta':>9} {'v2 RAW':>7} {'v2 PPC':>7} {'v2 Delta':>9}")
print("-" * 68)
for mode in sorted(set(list(v1_llm["mode_summary"].keys()) + list(v2["mode_summary"].keys()))):
    v1s = v1_llm["mode_summary"].get(mode)
    v2s = v2["mode_summary"].get(mode)
    v1_str_a = f"{v1s['raw_avg']:>6.1f} {v1s['ppc_avg']:>6.1f} {(v1s['ppc_avg']-v1s['raw_avg']):>+8.2f}" if v1s else "       N/A"
    v2_str_a = f"{v2s['raw_avg']:>6.1f} {v2s['ppc_avg']:>6.1f} {(v2s['ppc_avg']-v2s['raw_avg']):>+8.2f}" if v2s else "       N/A"
    print(f"{mode:<14} {v1_str_a}    {v2_str_a}")

print("\n--- KEY INSIGHT ---")
print("v1: PPC wins on simple/medium prompts (41.7%)")
print("v2: PPC wins on architecture/compression/teaching (+0.2 to +0.8)")
print("v2: PPC LOSES on complex code generation (-3.6 avg, -5.2 worst)")
print()
print("ROOT CAUSE: Code generation needs full token budget.")
print("PPC overhead (constraint lock + echo) competes directly")
print("with Claude's code output capacity on complex tasks.")
print()
print("FIX: Code mode should add constraints as system-level")
print("instructions, NOT inline lock blocks that consume output tokens.")
