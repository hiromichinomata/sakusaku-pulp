import pulp
from ch10_transport import demand, cost as out_cost, labels

# 工場の生産能力（ケース）と、工場→倉庫の輸送費（円/ケース）
factories = {"f_wakayama": 450, "f_nagoya": 350}
in_cost = {
    ("f_wakayama", "osaka"): 150, ("f_wakayama", "wakayama"): 50, ("f_wakayama", "nagoya"): 500,
    ("f_nagoya", "osaka"): 400, ("f_nagoya", "wakayama"): 600, ("f_nagoya", "nagoya"): 50,
}
# 倉庫が1週間に扱える量（ケース）
handling = {"osaka": 300, "wakayama": 200, "nagoya": 250}
labels = {**labels, "f_wakayama": "和歌山工場", "f_nagoya": "名古屋工場"}

prob = pulp.LpProblem("two_stage", pulp.LpMinimize)

inbound = {k: prob.add_variable(f"in_{k[0]}_{k[1]}", lowBound=0) for k in in_cost}
outbound = {k: prob.add_variable(f"out_{k[0]}_{k[1]}", lowBound=0) for k in out_cost}

prob += (pulp.lpSum(in_cost[k] * inbound[k] for k in in_cost)
         + pulp.lpSum(out_cost[k] * outbound[k] for k in out_cost)), "total_cost"

for f, cap in factories.items():
    prob += pulp.lpSum(inbound[f, w] for w in handling if (f, w) in in_cost) <= cap, f"factory_{f}"

for w, cap in handling.items():
    flow_in = pulp.lpSum(inbound[f, w] for f in factories if (f, w) in in_cost)
    flow_out = pulp.lpSum(outbound[w, s] for s in demand if (w, s) in out_cost)
    prob += flow_in == flow_out, f"balance_{w}"      # 入った分だけ出ていく
    prob += flow_in <= cap, f"handling_{w}"          # 倉庫の取扱量の上限

for s, d in demand.items():
    prob += pulp.lpSum(outbound[w, s] for w in handling if (w, s) in out_cost) == d, f"demand_{s}"

stats = prob.solve(pulp.HiGHS(msg=False))
print("状態:", stats.status_str)
in_total = sum(in_cost[k] * inbound[k].value() for k in in_cost)
out_total = sum(out_cost[k] * outbound[k].value() for k in out_cost)
print(f"輸送費: {in_total + out_total:,.0f} 円（工場→倉庫 {in_total:,.0f} 円 / 倉庫→店舗 {out_total:,.0f} 円）")
print("工場→倉庫:")
for (f, w), v in inbound.items():
    if v.value() > 1e-6:
        print(f"  {labels[f]} → {labels[w]}: {v.value():.0f}")
print("倉庫→店舗:")
for (w, s), v in outbound.items():
    if v.value() > 1e-6:
        print(f"  {labels[w]} → {labels[s]}: {v.value():.0f}")
