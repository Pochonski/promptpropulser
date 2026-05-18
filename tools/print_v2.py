"""Print v2 benchmark results."""
import json, sys

with open("data/benchmark_v2_results.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total prompts: {len(data['results'])}")
print(f"Timestamp: {data['timestamp']}")
print()

print(f"{'ID':<18} {'Mode':<11} {'RAW':>6} {'PPC':>6} {'Delta':>7}")
print("-" * 56)

for r in data["results"]:
    raw_avg = sum(r["raw_critic"].values()) / 4.0
    ppc_avg = sum(r["ppc_critic"].values()) / 4.0
    delta = ppc_avg - raw_avg
    sign = "+" if delta > 0 else ""
    print(f"{r['id']:<18} {r['mode']:<11} {raw_avg:>5.1f} {ppc_avg:>5.1f} {sign}{delta:>5.2f}")

print()
print("--- OVERALL ---")
o = data["overall"]
print(f"  PPC Win Rate:        {o['ppc_win_rate']:.1%}")
print(f"  Constraint Delta:    {o['constraint_delta']:+.2f}")
print(f"  Accuracy Delta:      {o['accuracy_delta']:+.2f}")
print(f"  Clarity Delta:       {o['clarity_delta']:+.2f}")
print(f"  Efficiency Delta:    {o['efficiency_delta']:+.2f}")

print()
print("--- BY MODE ---")
for mode, stats in sorted(data["mode_summary"].items()):
    delta = stats["ppc_avg"] - stats["raw_avg"]
    sign = "+" if delta > 0 else ""
    print(f"  {mode:<12} RAW={stats['raw_avg']:.1f} PPC={stats['ppc_avg']:.1f} Delta={sign}{delta:.1f} Wins={stats['ppc_wins']}/{stats['count']}")
