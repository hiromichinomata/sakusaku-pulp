import pulp

# 来年度の施策の候補（本書用の架空のデータ）。費用と効果は万円
candidates = {
    "web_ad":        {"label": "Web広告",          "cost": 120, "value": 180, "group": "promo"},
    "tv_cm":         {"label": "地方テレビCM",     "cost": 400, "value": 520, "group": "promo"},
    "sampling":      {"label": "店頭試食会",       "cost": 80,  "value": 110, "group": "promo"},
    "new_label":     {"label": "ラベル刷新",       "cost": 60,  "value": 70,  "group": "promo"},
    "hygiene":       {"label": "衛生設備の更新",   "cost": 250, "value": 150, "group": "equip"},
    "new_kettle":    {"label": "大型釜の導入",     "cost": 300, "value": 420, "group": "equip"},
    "solar":         {"label": "太陽光パネル",     "cost": 350, "value": 300, "group": "equip"},
    "training":      {"label": "品質研修",         "cost": 90,  "value": 140, "group": "people"},
    "hire_qc":       {"label": "品質管理者の採用", "cost": 200, "value": 230, "group": "people"},
    "inventory_sys": {"label": "在庫管理システム", "cost": 150, "value": 160, "group": "it"},
    "ec_site":       {"label": "通販サイト",       "cost": 180, "value": 260, "group": "it"},
    "pos_data":      {"label": "POSデータ分析",    "cost": 100, "value": 120, "group": "it"},
}
BUDGET = 1000


def solve_invest(rules):
    prob = pulp.LpProblem("invest", pulp.LpMaximize)
    pick = {k: prob.add_variable(f"pick_{k}", cat="Binary") for k in candidates}

    prob += pulp.lpSum(candidates[k]["value"] * pick[k] for k in candidates), "total_value"
    prob += pulp.lpSum(candidates[k]["cost"] * pick[k] for k in candidates) <= BUDGET, "budget"

    if "promo_max1" in rules:   # 広告・販促は1件まで（担当チームが1つ）
        prob += pulp.lpSum(pick[k] for k in candidates if candidates[k]["group"] == "promo") <= 1, "promo_max1"
    if "count_max4" in rules:   # 同時に進められるのは4件まで
        prob += pulp.lpSum(pick.values()) <= 4, "count_max4"
    if "must_hygiene" in rules:  # 衛生設備の更新は必須（法令対応）
        prob += pick["hygiene"] == 1, "must_hygiene"
    if "people_min1" in rules:  # 人材への投資を1件以上
        prob += pulp.lpSum(pick[k] for k in candidates if candidates[k]["group"] == "people") >= 1, "people_min1"

    stats = prob.solve(pulp.HiGHS(msg=False))
    picked = [k for k in candidates if pick[k].value() > 0.5]
    return {
        "status": stats.status_str,
        "value": pulp.value(prob.objective),
        "cost": sum(candidates[k]["cost"] for k in picked),
        "picked": picked,
    }


def greedy(budget):
    """効果 ÷ 費用 が高い順に、予算に収まるものを選ぶ"""
    order = sorted(candidates, key=lambda k: candidates[k]["value"] / candidates[k]["cost"], reverse=True)
    picked, rest = [], budget
    for k in order:
        if candidates[k]["cost"] <= rest:
            picked.append(k)
            rest -= candidates[k]["cost"]
    return {
        "status": "-",
        "value": sum(candidates[k]["value"] for k in picked),
        "cost": budget - rest,
        "picked": picked,
    }


def show(title, r):
    names = "・".join(candidates[k]["label"] for k in r["picked"])
    print(f"| {title} | {r['value']:,.0f} | {r['cost']:,} | {len(r['picked'])} | {names} |")


if __name__ == "__main__":
    print("| 条件 | 効果 | 費用 | 件数 | 選んだ施策 |")
    print("|------|-----:|-----:|----:|-----------|")
    show("効率順に選ぶ（参考）", greedy(BUDGET))
    rules = []
    for title, rule in [
        ("1: 予算だけ", None),
        ("2: ＋販促は1件まで", "promo_max1"),
        ("3: ＋4件まで", "count_max4"),
        ("4: ＋衛生設備は必須", "must_hygiene"),
        ("5: ＋人材を1件以上", "people_min1"),
    ]:
        if rule:
            rules.append(rule)
        show(title, solve_invest(rules))
