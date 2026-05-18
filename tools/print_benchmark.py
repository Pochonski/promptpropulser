"""Print detailed benchmark results."""
import json
import sys

with open("data/benchmark_results.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total prompts: {len(data['results'])}")
print(f"Timestamp: {data['timestamp']}")
print()

print(f"{'ID':<22} {'Mode':<12} {'RAW':>6} {'PPC':>6} {'Delta':>7} {'Err'}")
print("-" * 60)

for r in data["results"]:
    raw_avg = sum(r["raw_critic"].values()) / 4.0
    ppc_avg = sum(r["ppc_critic"].values()) / 4.0
    delta = ppc_avg - raw_avg
    sign = "+" if delta > 0 else ""
    errs = []
    if r.get("raw_error"):
        errs.append("RAW_ERR")
    if r.get("ppc_error"):
        errs.append("PPC_ERR")
    err_str = ",".join(errs) if errs else ""
    print(f"{r['id']:<22} {r['mode']:<12} {raw_avg:>5.1f} {ppc_avg:>5.1f} {sign}{delta:>5.2f}  {err_str}")

print()
print("--- MODE SUMMARY ---")
for mode, stats in sorted(data["mode_summary"].items()):
    delta = stats["ppc_avg"] - stats["raw_avg"]
    sign = "+" if delta > 0 else ""
    print(f"  {mode:<12} RAW={stats['raw_avg']:.2f} PPC={stats['ppc_avg']:.2f} Delta={sign}{delta:.2f} Wins={stats['ppc_wins']}/{stats['count']}")

print()
print("--- OVERALL ---")
o = data["overall"]
print(f"  PPC Win Rate:        {o['ppc_win_rate']:.1%}")
print(f"  Constraint Delta:    {o['constraint_delta']:+.2f}")
print(f"  Accuracy Delta:      {o['accuracy_delta']:+.2f}")
print(f"  Clarity Delta:       {o['clarity_delta']:+.2f}")
print(f"  Efficiency Delta:    {o['efficiency_delta']:+.2f}")
