import json

with open("data/benchmark_v3_results.json", encoding="utf-8") as f:
    v3 = json.load(f)

with open("data/benchmark_v2_subset_results.json", encoding="utf-8") as f:
    v2 = json.load(f)

v2_code = [r for r in v2["results"] if r["mode"] == "code"]
v2_raw = sum(sum(r["raw_critic"].values())/4.0 for r in v2_code) / len(v2_code)
v2_ppc = sum(sum(r["ppc_critic"].values())/4.0 for r in v2_code) / len(v2_code)
v2_wins = sum(1 for r in v2_code if sum(r["ppc_critic"].values()) > sum(r["raw_critic"].values()))

v3_code = [r for r in v3["results"] if r["mode"] == "code"]
v3_raw = sum(sum(r["raw_critic"].values())/4.0 for r in v3_code) / len(v3_code)
v3_ppc = sum(sum(r["ppc_critic"].values())/4.0 for r in v3_code) / len(v3_code)
v3_wins = sum(1 for r in v3_code if sum(r["ppc_critic"].values()) > sum(r["raw_critic"].values()))

print("=" * 68)
print("  CODE MODE: v2 (extreme) vs v3 (solvable + system channel)")
print("=" * 68)
print()
print(f"  v2:  RAW={v2_raw:.1f}  PPC={v2_ppc:.1f}  Delta={v2_ppc-v2_raw:+.2f}  Wins={v2_wins}/{len(v2_code)}")
print(f"  v3:  RAW={v3_raw:.1f}  PPC={v3_ppc:.1f}  Delta={v3_ppc-v3_raw:+.2f}  Wins={v3_wins}/{len(v3_code)}")
print()
print(f"  Improvement: { (v3_ppc-v3_raw) - (v2_ppc-v2_raw) :+.2f} delta points")
print()
print("  v3 per-prompt:")
for r in v3_code:
    raw_avg = sum(r["raw_critic"].values()) / 4.0
    ppc_avg = sum(r["ppc_critic"].values()) / 4.0
    delta = ppc_avg - raw_avg
    sign = "+" if delta > 0 else ""
    verdict = "WIN" if delta > 0 else ("TIE" if delta == 0 else "LOSS")
    name = r["id"].replace("code_v3_", "#").replace("0", "")
    print(f"    {name:<8}  RAW={raw_avg:.1f}  PPC={ppc_avg:.1f}  {sign}{delta:.1f}  {verdict}")
