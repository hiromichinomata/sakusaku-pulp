import pulp

items = {
    "cookie": {"cost": 300, "profit": 200, "max": 10},
    "muffin": {"cost": 500, "profit": 350, "max": 8},
    "cake": {"cost": 800, "profit": 600, "max": 5},
}
budget = 8500

prob = pulp.LpProblem("marche_plan", pulp.LpMaximize)

x = {
    name: prob.add_variable(name, lowBound=0, upBound=info["max"], cat="Integer")
    for name, info in items.items()
}

prob += pulp.lpSum(items[n]["profit"] * x[n] for n in items), "total_profit"
prob += pulp.lpSum(items[n]["cost"] * x[n] for n in items) <= budget, "budget"

stats = prob.solve(pulp.HiGHS(msg=False))

print("状態:", stats.status_str)
print("利益:", pulp.value(prob.objective))
for name in items:
    print(name, x[name].value())
