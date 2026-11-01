import pulp

# ---- データ（モデル表をそのまま辞書にする） ----
products = {
    "jam":      {"label": "ジャム", "profit": 450, "min": 10, "max": None},
    "syrup":    {"label": "シロップ", "profit": 400, "min": 0, "max": None},
    "umeboshi": {"label": "梅干し", "profit": 500, "min": 0, "max": 20},
}

resources = {
    "ume_g":    {"label": "梅(g)", "capacity": 18 * 1000,
                 "use": {"jam": 300, "syrup": 400, "umeboshi": 500}},
    "sugar_g":  {"label": "砂糖(g)", "capacity": 10 * 1000,
                 "use": {"jam": 200, "syrup": 400}},
    "work_min": {"label": "作業(分)", "capacity": 12 * 60,
                 "use": {"jam": 20, "syrup": 10, "umeboshi": 15}},
    "jars":     {"label": "瓶(個)", "capacity": 50,
                 "use": {"jam": 1, "syrup": 1}},
}


# ---- モデル（データが変わっても書き換えない） ----
def build_model(products, resources):
    prob = pulp.LpProblem("marche_data", pulp.LpMaximize)

    make = {
        p: prob.add_variable(f"make_{p}", lowBound=info["min"], upBound=info["max"], cat="Integer")
        for p, info in products.items()
    }

    prob += pulp.lpSum(products[p]["profit"] * make[p] for p in products), "total_profit"

    used = {}
    for r, info in resources.items():
        used[r] = pulp.lpSum(info["use"].get(p, 0) * make[p] for p in products)
        prob += used[r] <= info["capacity"], f"cap_{r}"

    return prob, make, used


def report(prob, stats, make, used, products, resources):
    print("状態:", stats.status_str)
    print(f"利益: {pulp.value(prob.objective):,.0f} 円")
    for p, info in products.items():
        print(f"  {info['label']}: {make[p].value():.0f}")
    for r, info in resources.items():
        print(f"  {info['label']}: {pulp.value(used[r]):,.0f} / {info['capacity']:,}")


if __name__ == "__main__":
    prob, make, used = build_model(products, resources)
    stats = prob.solve(pulp.HiGHS(msg=False))
    report(prob, stats, make, used, products, resources)
