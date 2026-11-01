import pulp

prob = pulp.LpProblem("marche_plan", pulp.LpMaximize)
items = {
    "cookie": {"cost": 300, "profit": 200, "max": 10},
    "muffin": {"cost": 500, "profit": 350, "max": 8},
    "cake": {"cost": 800, "profit": 600, "max": 5},
}
x = {n: prob.add_variable(n, lowBound=0, upBound=i["max"], cat="Integer") for n, i in items.items()}
prob += pulp.lpSum(items[n]["profit"] * x[n] for n in items), "total_profit"
prob += pulp.lpSum(items[n]["cost"] * x[n] for n in items) <= 8500, "budget"

prob.writeLP("marche.lp")
prob.writeMPS("marche.mps")
print(open("marche.mps").read())

# MPS ファイルから問題を読み直して、別のソルバーで解く
variables, prob2 = pulp.LpProblem.fromMPS("marche.mps", sense=pulp.LpMaximize)
for name, solver in [("HiGHS", pulp.HiGHS(msg=False)), ("CBC", pulp.COIN_CMD(msg=False))]:
    stats = prob2.solve(solver)
    print(name, stats.status_str, pulp.value(prob2.objective), {k: v.value() for k, v in variables.items()})
