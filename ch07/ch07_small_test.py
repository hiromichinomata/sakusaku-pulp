import itertools
import pulp
from ch07_fixed import build_model

# 手で確かめられるくらい小さなデータ
small_products = {
    "a": {"label": "A", "profit": 3, "min": 0, "max": 4},
    "b": {"label": "B", "profit": 5, "min": 1, "max": 3},
}
small_resources = {
    "r1": {"label": "資源1", "capacity": 10, "use": {"a": 2, "b": 3}},
    "r2": {"label": "資源2", "capacity": 6, "use": {"a": 1, "b": 2}},
}


def brute_force(products, resources):
    names = list(products)
    ranges = [range(products[p]["min"], products[p]["max"] + 1) for p in names]
    best = None
    for counts in itertools.product(*ranges):
        x = dict(zip(names, counts))
        if all(sum(info["use"].get(p, 0) * x[p] for p in names) <= info["capacity"]
               for info in resources.values()):
            profit = sum(products[p]["profit"] * x[p] for p in names)
            if best is None or profit > best:
                best = profit
    return best


prob, make = build_model(small_products, small_resources)
stats = prob.solve(pulp.HiGHS(msg=False))
pulp_best = pulp.value(prob.objective)
bf_best = brute_force(small_products, small_resources)

print("PuLP:", stats.status_str, pulp_best)
print("全探索:", bf_best)
print("一致" if stats.status_str == "Optimal" and abs(pulp_best - bf_best) < 1e-6 else "不一致！")
