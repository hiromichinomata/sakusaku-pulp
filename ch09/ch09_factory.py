import pulp

# うめ食品の工場（本書用の架空のデータ）。数量の単位はケース、期間は1週間
products = {
    "jam":      {"label": "ジャム",       "price": 6000, "material": 2500,
                 "ume_kg": 6,  "sugar_kg": 4, "pack_h": 0.2, "demand": 120, "min": 30},
    "syrup":    {"label": "シロップ",     "price": 5000, "material": 2000,
                 "ume_kg": 5,  "sugar_kg": 5, "pack_h": 0.2, "demand": 100, "min": 0},
    "umeboshi": {"label": "梅干し",       "price": 8000, "material": 4200,
                 "ume_kg": 10, "sugar_kg": 0, "pack_h": 0.3, "demand": 60,  "min": 20},
    "dressing": {"label": "ドレッシング", "price": 4500, "material": 1500,
                 "ume_kg": 2,  "sugar_kg": 1, "pack_h": 0.1, "demand": 150, "min": 0},
}

lines = {
    "A": {"label": "ラインA(旧型)", "cost_per_h": 3000, "hours": 40},
    "B": {"label": "ラインB(新型)", "cost_per_h": 5000, "hours": 40},
}

# 1ケース作るのにかかる時間（時間）。梅干しはラインBでは作れない
line_time = {
    ("jam", "A"): 0.5, ("syrup", "A"): 0.3, ("umeboshi", "A"): 0.8, ("dressing", "A"): 0.4,
    ("jam", "B"): 0.3, ("syrup", "B"): 0.2,                          ("dressing", "B"): 0.25,
}

materials = {"ume_kg": 1500, "sugar_kg": 800}   # 週に使える原材料
pack_hours = 40                                 # 包装担当の作業時間（週）


def unit_profit(p, l):
    """1ケースあたりの利益 = 価格 - 原材料費 - ラインの稼働費"""
    return products[p]["price"] - products[p]["material"] - line_time[p, l] * lines[l]["cost_per_h"]


def build_model(use=("line", "material", "pack", "demand", "min")):
    prob = pulp.LpProblem("factory", pulp.LpMaximize)

    make = {(p, l): prob.add_variable(f"make_{p}_{l}", lowBound=0, cat="Integer") for (p, l) in line_time}

    prob += pulp.lpSum(unit_profit(p, l) * make[p, l] for (p, l) in line_time), "total_profit"

    # 商品ごとの合計（ラインA ＋ ラインB）
    total = {p: pulp.lpSum(make[p, l] for l in lines if (p, l) in line_time) for p in products}

    if "line" in use:
        for l in lines:
            prob += pulp.lpSum(line_time[p, l] * make[p, l] for p in products if (p, l) in line_time) \
                <= lines[l]["hours"], f"line_{l}"
    if "material" in use:
        for m, cap in materials.items():
            prob += pulp.lpSum(products[p][m] * total[p] for p in products) <= cap, f"mat_{m}"
    if "pack" in use:
        prob += pulp.lpSum(products[p]["pack_h"] * total[p] for p in products) <= pack_hours, "pack"
    if "demand" in use:
        for p in products:
            prob += total[p] <= products[p]["demand"], f"demand_{p}"
    if "min" in use:
        for p in products:
            if products[p]["min"] > 0:
                prob += total[p] >= products[p]["min"], f"min_{p}"

    return prob, make, total


def solve(use):
    prob, make, total = build_model(use)
    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return {"status": stats.status_str}
    line_used = {
        l: sum(line_time[p, l] * make[p, l].value() for p in products if (p, l) in line_time)
        for l in lines
    }
    return {
        "status": stats.status_str,
        "profit": pulp.value(prob.objective),
        "make": {k: round(v.value()) for k, v in make.items()},
        "total": {p: round(pulp.value(total[p])) for p in products},
        "line_used": line_used,
        "pack_used": sum(products[p]["pack_h"] * pulp.value(total[p]) for p in products),
        "mat_used": {m: sum(products[p][m] * pulp.value(total[p]) for p in products) for m in materials},
    }


if __name__ == "__main__":
    steps = [
        ("1: ライン＋原材料", ("line", "material")),
        ("2: ＋包装", ("line", "material", "pack")),
        ("3: ＋需要上限", ("line", "material", "pack", "demand")),
        ("4: ＋最低生産数", ("line", "material", "pack", "demand", "min")),
    ]
    print("| ステップ | 利益 | ジャム | シロップ | 梅干し | ドレッシング |")
    print("|---------|-----:|------:|--------:|------:|-----------:|")
    results = {}
    for title, use in steps:
        r = solve(use)
        results[title] = r
        t = r["total"]
        print(f"| {title} | {r['profit']:,.0f} | {t['jam']} | {t['syrup']} | {t['umeboshi']} | {t['dressing']} |")

    r = results["4: ＋最低生産数"]
    print()
    print("ステップ4の内訳")
    for l in lines:
        items = ", ".join(f"{products[p]['label']} {r['make'][p, l]}"
                          for p in products if (p, l) in line_time and r["make"][p, l] > 0)
        print(f"  {lines[l]['label']}: {items}（{r['line_used'][l]:.1f} / {lines[l]['hours']} 時間）")
    print(f"  包装: {r['pack_used']:.1f} / {pack_hours} 時間")
    for m, cap in materials.items():
        print(f"  {m}: {r['mat_used'][m]:,.0f} / {cap:,}")
