import pulp

# 4週間の生産と在庫の計画（本書用の架空のデータ）。3週目にお中元の注文が集中する
weeks = [1, 2, 3, 4]
products = {
    "jam":   {"label": "ジャム",   "profit": 2000, "hours": 0.5},
    "syrup": {"label": "シロップ", "profit": 2100, "hours": 0.3},
}
demand = {
    ("jam", 1): 40, ("jam", 2): 50, ("jam", 3): 120, ("jam", 4): 60,
    ("syrup", 1): 60, ("syrup", 2): 60, ("syrup", 3): 100, ("syrup", 4): 50,
}
LINE_HOURS = 50   # 1週間に使えるラインの時間
HOLD = 150        # 1ケースを1週間在庫として持つ費用（円）


def solve_weeks(allow_stock):
    prob = pulp.LpProblem("weeks", pulp.LpMaximize)
    make = {(p, w): prob.add_variable(f"make_{p}_{w}", lowBound=0, cat="Integer") for p in products for w in weeks}
    sell = {(p, w): prob.add_variable(f"sell_{p}_{w}", lowBound=0, upBound=demand[p, w]) for p in products for w in weeks}
    stock = {(p, w): prob.add_variable(f"stock_{p}_{w}", lowBound=0) for p in products for w in weeks}

    prob += (pulp.lpSum(products[p]["profit"] * sell[p, w] for p in products for w in weeks)
             - pulp.lpSum(HOLD * stock[p, w] for p in products for w in weeks)), "profit"

    for p in products:
        for w in weeks:
            before = stock[p, w - 1] if w > 1 else 0   # 1週目の前の在庫は 0
            # 先週の在庫 ＋ 今週作った量 − 今週売った量 ＝ 今週末の在庫
            prob += before + make[p, w] - sell[p, w] == stock[p, w], f"balance_{p}_{w}"
            if not allow_stock:
                prob += stock[p, w] == 0, f"no_stock_{p}_{w}"
    for w in weeks:
        prob += pulp.lpSum(products[p]["hours"] * make[p, w] for p in products) <= LINE_HOURS, f"line_{w}"

    stats = prob.solve(pulp.HiGHS(msg=False))
    return stats, prob, make, sell, stock


def show(title, allow_stock):
    stats, prob, make, sell, stock = solve_weeks(allow_stock)
    print(f"■ {title}: {stats.status_str}  利益 {pulp.value(prob.objective):,.0f} 円")
    print("| 商品 | 項目 | 1週 | 2週 | 3週 | 4週 |")
    print("|------|------|----:|----:|----:|----:|")
    for p in products:
        for label, var in [("需要", None), ("生産", make), ("販売", sell), ("在庫", stock)]:
            vals = [demand[p, w] if var is None else round(var[p, w].value()) for w in weeks]
            print(f"| {products[p]['label']} | {label} | " + " | ".join(str(v) for v in vals) + " |")
    used = [sum(products[p]["hours"] * make[p, w].value() for p in products) for w in weeks]
    print("ライン: " + " / ".join(f"{u:.1f}" for u in used) + f"（各週 {LINE_HOURS} 時間まで）")


if __name__ == "__main__":
    show("在庫を持たない", allow_stock=False)
    show("在庫を持ってよい", allow_stock=True)
