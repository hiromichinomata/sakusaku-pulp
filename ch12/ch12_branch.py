import math
import pulp

items = {
    "cookie": {"cost": 300, "profit": 200, "max": 10},
    "muffin": {"cost": 500, "profit": 350, "max": 8},
    "cake":   {"cost": 800, "profit": 600, "max": 5},
}
budget = 8500


def solve_relaxed(bounds):
    """整数の条件を外して（連続変数で）解く。bounds は {商品: (下限, 上限)}"""
    prob = pulp.LpProblem("relaxed", pulp.LpMaximize)
    x = {n: prob.add_variable(n, lowBound=bounds[n][0], upBound=bounds[n][1]) for n in items}
    prob += pulp.lpSum(items[n]["profit"] * x[n] for n in items)
    prob += pulp.lpSum(items[n]["cost"] * x[n] for n in items) <= budget
    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return None, None
    return pulp.value(prob.objective), {n: x[n].value() for n in items}


best = {"profit": -1, "plan": None}
count = 0


def branch(bounds, depth):
    global count
    count += 1
    profit, x = solve_relaxed(bounds)
    indent = "  " * depth
    if profit is None:
        print(f"{indent}#{count} 解なし → 打ち切り")
        return
    plan = ", ".join(f"{n}={v:g}" for n, v in x.items())
    if profit <= best["profit"] + 1e-9:
        print(f"{indent}#{count} 上限 {profit:.1f} ≦ 暫定 {best['profit']} → 打ち切り")
        return
    frac = [n for n, v in x.items() if abs(v - round(v)) > 1e-6]
    if not frac:
        print(f"{indent}#{count} 整数解 {profit:.0f} ({plan}) → 暫定解を更新")
        best["profit"], best["plan"] = profit, x
        return
    n = frac[0]
    v = x[n]
    print(f"{indent}#{count} 上限 {profit:.1f} ({plan}) → {n} で分ける")
    low, high = bounds[n]
    branch({**bounds, n: (low, math.floor(v))}, depth + 1)   # n ≦ 切り捨て
    branch({**bounds, n: (math.ceil(v), high)}, depth + 1)   # n ≧ 切り上げ


branch({n: (0, items[n]["max"]) for n in items}, 0)
print()
print(f"最適解: {best['profit']:.0f} 円 {best['plan']} / 調べた問題の数: {count}")
