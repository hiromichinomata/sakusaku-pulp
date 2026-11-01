items = {
    "クッキー": {"cost": 300, "profit": 200, "max": 10},
    "マフィン": {"cost": 500, "profit": 350, "max": 8},
    "ケーキ": {"cost": 800, "profit": 600, "max": 5},
}
budget = 8500

# 1円あたりの利益が高い順に並べる
order = sorted(items, key=lambda n: items[n]["profit"] / items[n]["cost"], reverse=True)

remaining = budget
plan = {}
for name in order:
    info = items[name]
    count = min(info["max"], remaining // info["cost"])
    plan[name] = count
    remaining -= count * info["cost"]

profit = sum(items[n]["profit"] * k for n, k in plan.items())
print("効率順:", order)
print("仕入れ案:", plan)
print("利益:", profit, "円 / 残り予算:", remaining, "円")
