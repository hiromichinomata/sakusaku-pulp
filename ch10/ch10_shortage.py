import pulp
from ch10_transport import supply, demand, cost, labels, solve_transport

# 京都店の注文が 150 → 230 ケースに増えた
demand2 = {**demand, "kyoto": 230}
print("在庫の合計:", sum(supply.values()), "/ 注文の合計:", sum(demand2.values()))

stats, prob, ship = solve_transport(supply, demand2, cost)
print("欠品を考えないモデル:", stats.status_str)

# 欠品（届けられない量）を変数にして、1ケースあたり 2,000 円の罰金を付ける
PENALTY = 2000

prob = pulp.LpProblem("transport_shortage", pulp.LpMinimize)
ship = {(w, s): prob.add_variable(f"ship_{w}_{s}", lowBound=0) for (w, s) in cost}
short = {s: prob.add_variable(f"short_{s}", lowBound=0) for s in demand2}

prob += (pulp.lpSum(cost[k] * ship[k] for k in cost)
         + pulp.lpSum(PENALTY * short[s] for s in demand2)), "total_cost"

for w in supply:
    prob += pulp.lpSum(ship[w, s] for s in demand2 if (w, s) in cost) <= supply[w], f"supply_{w}"
for s in demand2:
    prob += pulp.lpSum(ship[w, s] for w in supply if (w, s) in cost) + short[s] == demand2[s], f"demand_{s}"

stats = prob.solve(pulp.HiGHS(msg=False))
print("欠品を許すモデル:", stats.status_str)
transport = sum(cost[k] * ship[k].value() for k in cost)
print(f"輸送費: {transport:,.0f} 円 / 欠品の罰金: {PENALTY * sum(v.value() for v in short.values()):,.0f} 円")
for s in demand2:
    if short[s].value() > 1e-6:
        print(f"  {labels[s]}: {short[s].value():.0f} ケース欠品")
