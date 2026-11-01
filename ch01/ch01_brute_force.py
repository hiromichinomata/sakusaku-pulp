import itertools

items = {
    "クッキー": {"cost": 300, "profit": 200, "max": 10},
    "マフィン": {"cost": 500, "profit": 350, "max": 8},
    "ケーキ": {"cost": 800, "profit": 600, "max": 5},
}
budget = 8500

names = list(items)
ranges = [range(items[n]["max"] + 1) for n in names]  # 0〜上限個

best_profit = -1
best_plan = None
checked = 0
feasible = 0

for counts in itertools.product(*ranges):
    checked += 1
    cost = sum(items[n]["cost"] * k for n, k in zip(names, counts))
    if cost > budget:  # 予算オーバーは候補にしない
        continue
    feasible += 1
    profit = sum(items[n]["profit"] * k for n, k in zip(names, counts))
    if profit > best_profit:
        best_profit = profit
        best_plan = dict(zip(names, counts))
        best_cost = cost

print("調べた組み合わせ:", checked, "通り")
print("予算内の組み合わせ:", feasible, "通り")
print("最良の仕入れ案:", best_plan)
print("利益:", best_profit, "円 / 仕入れ額:", best_cost, "円")
