import pulp
from ch07_fix1 import products, resources, build_model

# 資源の制約を1本ずつ外して解いてみる
for skip in resources:
    subset = {r: info for r, info in resources.items() if r != skip}
    prob, make = build_model(products, subset)
    stats = prob.solve(pulp.HiGHS(msg=False))
    print(f"{skip:<9} を外すと → {stats.status_str}")

# 変数の下限・上限をすべて外して解いてみる
relaxed = {p: {**info, "min": 0, "max": None} for p, info in products.items()}
prob, make = build_model(relaxed, resources)
stats = prob.solve(pulp.HiGHS(msg=False))
print(f"{'上下限':<9} を外すと → {stats.status_str}")
