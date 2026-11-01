"""モデル：辞書を受け取り、PuLP の問題を作る（ファイルもソルバーも知らない）"""
import pulp


def unit_profit(d: dict, p: str, l: str) -> float:
    return d["products"][p]["price"] - d["products"][p]["material"] - d["line_time"][p, l] * d["lines"][l]["cost_per_h"]


def build_model(d: dict):
    products, lines, line_time = d["products"], d["lines"], d["line_time"]
    capacity, usage = d["capacity"], d["usage"]

    prob = pulp.LpProblem("factory", pulp.LpMaximize)
    make = {(p, l): prob.add_variable(f"make_{p}_{l}", lowBound=0, cat="Integer") for (p, l) in line_time}

    prob += pulp.lpSum(unit_profit(d, p, l) * make[p, l] for (p, l) in line_time), "total_profit"

    total = {p: pulp.lpSum(v for (q, l), v in make.items() if q == p) for p in products}
    for l in lines:
        prob += pulp.lpSum(line_time[p, m] * make[p, m] for (p, m) in line_time if m == l) \
            <= lines[l]["hours"], f"line_{l}"
    for r in capacity:
        prob += pulp.lpSum(usage.get((p, r), 0) * total[p] for p in products) <= capacity[r], f"res_{r}"
    for p in products:
        prob += total[p] <= products[p]["demand"], f"demand_{p}"
        prob += total[p] >= products[p]["min"], f"min_{p}"
    return prob, make
