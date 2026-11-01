import copy
import pulp

# 1人前あたりの値（食品成分表をもとにした概算）。価格は本書用の架空の値
foods = {
    "rice":     {"label": "ごはん(150g)",      "price": 40, "kcal": 234, "protein": 3.8,  "fiber": 2.3, "calcium": 5,   "min": 0, "max": None},
    "natto":    {"label": "納豆(1パック)",     "price": 50, "kcal": 86,  "protein": 7.4,  "fiber": 3.0, "calcium": 41,  "min": 0, "max": None},
    "egg":      {"label": "卵(1個)",           "price": 30, "kcal": 71,  "protein": 6.1,  "fiber": 0.0, "calcium": 23,  "min": 0, "max": None},
    "milk":     {"label": "牛乳(200mL)",       "price": 50, "kcal": 126, "protein": 6.8,  "fiber": 0.0, "calcium": 227, "min": 0, "max": None},
    "banana":   {"label": "バナナ(1本)",       "price": 35, "kcal": 93,  "protein": 1.1,  "fiber": 1.1, "calcium": 6,   "min": 0, "max": None},
    "chicken":  {"label": "鶏むね肉(100g)",    "price": 90, "kcal": 105, "protein": 23.3, "fiber": 0.0, "calcium": 4,   "min": 0, "max": None},
    "broccoli": {"label": "ブロッコリー(80g)", "price": 60, "kcal": 30,  "protein": 4.3,  "fiber": 4.1, "calcium": 30,  "min": 0, "max": None},
}

# 栄養の条件：(下限, 上限)。None は条件なし
needs = {
    "kcal":    (700, 900),
    "protein": (30, None),
}


def solve_lunch(foods, needs, staple_ratio=None, step=None):
    prob = pulp.LpProblem("lunch", pulp.LpMinimize)

    if step is None:
        # 何人前食べるか（小数OK）
        eat = {
            f: prob.add_variable(f"eat_{f}", lowBound=d["min"], upBound=d["max"])
            for f, d in foods.items()
        }
    else:
        # step 人前を何単位食べるか（整数）。0.5 なら半人前ずつ
        units = {
            f: prob.add_variable(
                f"units_{f}",
                lowBound=round(d["min"] / step),
                upBound=None if d["max"] is None else round(d["max"] / step),
                cat="Integer",
            )
            for f, d in foods.items()
        }
        eat = {f: step * units[f] for f in foods}

    def total(key):
        return pulp.lpSum(foods[f][key] * eat[f] for f in foods)

    prob += total("price"), "total_price"

    for key, (low, high) in needs.items():
        if low is not None:
            prob += total(key) >= low, f"min_{key}"
        if high is not None:
            prob += total(key) <= high, f"max_{key}"

    if staple_ratio is not None:
        # ごはんのエネルギー ≦ 全体のエネルギー × staple_ratio
        prob += foods["rice"]["kcal"] * eat["rice"] <= staple_ratio * total("kcal"), "staple_ratio"

    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return {"status": stats.status_str}

    return {
        "status": stats.status_str,
        "price": pulp.value(prob.objective),
        "eat": {f: pulp.value(e) for f, e in eat.items()},
        "totals": {k: pulp.value(total(k)) for k in ["kcal", "protein", "fiber", "calcium"]},
        "rice_ratio": foods["rice"]["kcal"] * pulp.value(eat["rice"]) / pulp.value(total("kcal")),
    }


def show(title, result, foods):
    print(f"■ {title}: {result['status']}")
    if result["status"] != "Optimal":
        return
    menu = " / ".join(f"{foods[f]['label']} {x:.2f}" for f, x in result["eat"].items() if x > 1e-6)
    t = result["totals"]
    print(f"  {result['price']:.1f} 円  {menu}")
    print(f"  {t['kcal']:.0f} kcal / たんぱく質 {t['protein']:.1f} g / 食物繊維 {t['fiber']:.1f} g / "
          f"カルシウム {t['calcium']:.0f} mg / ごはんのエネルギー比 {result['rice_ratio']:.0%}")


if __name__ == "__main__":
    # ステップ1：エネルギーとたんぱく質だけ
    show("ステップ1", solve_lunch(foods, needs), foods)

    # ステップ2：食品ごとの上限を加える
    foods2 = copy.deepcopy(foods)
    foods2["rice"]["max"] = 2
    foods2["egg"]["max"] = 1
    foods2["milk"]["max"] = 1
    for f in foods2:
        if foods2[f]["max"] is None:
            foods2[f]["max"] = 2
    show("ステップ2", solve_lunch(foods2, needs), foods2)

    # ステップ3：食物繊維とカルシウムの条件を加える
    needs3 = {**needs, "fiber": (7, None), "calcium": (250, None)}
    show("ステップ3", solve_lunch(foods2, needs3), foods2)

    # ステップ4：ごはんのエネルギーを全体の50%以下にする
    show("ステップ4", solve_lunch(foods2, needs3, staple_ratio=0.5), foods2)

    # ステップ5：ブロッコリーを半人前以上、量は半人前単位にする
    foods5 = copy.deepcopy(foods2)
    foods5["broccoli"]["min"] = 0.5
    show("ステップ5(小数)", solve_lunch(foods5, needs3, staple_ratio=0.5), foods5)
    show("ステップ5(半人前単位)", solve_lunch(foods5, needs3, staple_ratio=0.5, step=0.5), foods5)
