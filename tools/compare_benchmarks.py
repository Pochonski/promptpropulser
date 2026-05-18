"""Print keyword vs LLM judge comparison."""

import json

with open("data/benchmark_results.json", encoding="utf-8") as f:
    kw = json.load(f)

with open("data/benchmark_llm_judge_results.json", encoding="utf-8") as f:
    llm = json.load(f)

print("=" * 72)
print("  KEYWORD CRITIC vs LLM JUDGE — BENCHMARK COMPARISON")
print("=" * 72)

kw_overall = kw["overall"]
llm_overall = llm["overall"]

print(f"\n{'Metric':<28} {'Keyword':>10} {'LLM Judge':>10} {'Delta':>10}")
print("-" * 60)
metrics = [
    ("PPC Win Rate", "ppc_win_rate", "{:.1%}"),
    ("Constraint Delta", "constraint_delta", "{:+.2f}"),
    ("Accuracy Delta", "accuracy_delta", "{:+.2f}"),
    ("Clarity Delta", "clarity_delta", "{:+.2f}"),
    ("Efficiency Delta", "efficiency_delta", "{:+.2f}"),
]
for label, key, fmt in metrics:
    kw_val = kw_overall[key]
    llm_val = llm_overall[key]
    if "win" in key.lower() or "rate" in key.lower():
        print(f"{label:<28} {fmt.format(kw_val):>10} {fmt.format(llm_val):>10}")
    else:
        print(f"{label:<28} {fmt.format(kw_val):>10} {fmt.format(llm_val):>10}")

print(f"\n{'Mode':<14} {'KW RAW':>7} {'KW PPC':>7} {'KW Delta':>9} {'LLM RAW':>7} {'LLM PPC':>7} {'LLM Delta':>9} {'KW Wins':>7} {'LLM Wins':>7}")
print("-" * 80)
for mode in sorted(kw["mode_summary"].keys()):
    kws = kw["mode_summary"][mode]
    llms = llm["mode_summary"][mode]
    kw_delta = kws["ppc_avg"] - kws["raw_avg"]
    llm_delta = llms["ppc_avg"] - llms["raw_avg"]
    print(
        f"{mode:<14} {kws['raw_avg']:>6.1f} {kws['ppc_avg']:>6.1f} {kw_delta:>+8.2f} "
        f"{llms['raw_avg']:>7.1f} {llms['ppc_avg']:>7.1f} {llm_delta:>+8.2f} "
        f"{kws['ppc_wins']}/{kws['count']:>3}   {llms['ppc_wins']}/{llms['count']:>3}"
    )

print("\n--- KEY CHANGES ---")
for mode in sorted(kw["mode_summary"].keys()):
    kws = kw["mode_summary"][mode]
    llms = llm["mode_summary"][mode]
    kw_delta = kws["ppc_avg"] - kws["raw_avg"]
    llm_delta = llms["ppc_avg"] - llms["raw_avg"]
    if abs(llm_delta - kw_delta) >= 0.3:
        direction = "FLIPPED" if kw_delta * llm_delta < 0 else "IMPROVED"
        print(f"  {mode}: KW delta={kw_delta:+.2f} LLM delta={llm_delta:+.2f} — {direction}")
