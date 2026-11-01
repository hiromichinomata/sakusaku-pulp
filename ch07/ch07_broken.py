import pulp

products = {
    "jam":      {"label": "ジャム", "profit": 450, "min": 10, "max": None},
    "syrup":    {"label": "シロップ", "profit": 400, "min": 0, "max": None},
    "umeboshi": {"label": "梅干し", "profit": 500, "min": 0, "max": 20},
}

resources = {
    "ume_g":    {"label": "梅(g)", "capacity": 18 * 1000,
                 "use": {"jam": 300, "syrup": 400, "umebosi": 500}},
    "sugar_g":  {"label": "砂糖(g)", "capacity": 10 * 1000,
                 "use": {"jam": 200, "syrup": 400}},
    "work_min": {"label": "作業(分)", "capacity": 12 * 60,
                 "use": {"jam": 20, "syrup": 10, "umeboshi": 15}},
    "jars":     {"label": "瓶(個)", "capacity": 5,
                 "use": {"jam": 1, "syrup": 1}},
}


def build_model(products, resources):
    prob = pulp.LpProblem("marche_broken", pulp.LpMaximize)
    make = {
        p: prob.add_variable(f"make_{p}", lowBound=info["min"], upBound=info["max"], cat="Integer")
        for p, info in products.items()
    }
    prob += pulp.lpSum(products[p]["profit"] * make[p] for p in products), "total_profit"
    for r, info in resources.items():
        used = pulp.lpSum(info["use"].get(p, 0) * make[p] for p in products)
        prob += used >= info["capacity"], f"cap_{r}"
    return prob, make


if __name__ == "__main__":
    prob, make = build_model(products, resources)
    stats = prob.solve(pulp.HiGHS(msg=False))
    print("状態:", stats.status_str)
    if stats.status_str == "Optimal":
        print(f"利益: {pulp.value(prob.objective):,.0f} 円")
        print({p: round(v.value()) for p, v in make.items()})
