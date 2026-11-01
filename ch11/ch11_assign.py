import pulp

# 作業員と時給（円）。本書用の架空のデータ
workers = {
    "sato":      {"label": "佐藤",   "wage": 2000},
    "suzuki":    {"label": "鈴木",   "wage": 1500},
    "takahashi": {"label": "高橋",   "wage": 1200},
    "tanaka":    {"label": "田中",   "wage": 1200},
    "ito":       {"label": "伊藤",   "wage": 1000},
}
tasks = {
    "inspect": "原料検品", "jam_prep": "ジャム仕込み", "bottling": "瓶詰め", "labeling": "ラベル貼り",
    "boxing": "箱詰め", "forklift": "フォークリフト", "cleaning": "機械清掃", "inventory": "在庫記録",
}

# その人がその作業をすると何時間かかるか。None はできない（資格・免許がない）
hours_table = {
    #             検品  仕込み 瓶詰め ラベル 箱詰め リフト 清掃  在庫
    "sato":      [1.5,  3.0,   2.0,   1.0,   1.5,   1.0,   2.0,  1.0],
    "suzuki":    [2.0,  3.5,   2.5,   1.5,   2.0,   1.5,   2.0,  1.5],
    "takahashi": [2.5,  None,  3.0,   1.5,   2.0,   None,  2.5,  2.0],
    "tanaka":    [2.5,  4.5,   3.0,   2.0,   2.5,   2.0,   3.0,  2.0],
    "ito":       [3.0,  None,  3.5,   2.0,   2.5,   None,  3.0,  2.5],
}
hours = {
    (w, t): h
    for w, row in hours_table.items()
    for t, h in zip(tasks, row)
    if h is not None
}
MAX_HOURS = 8   # 1人1日8時間まで


def solve_assign(objective, max_load=None):
    prob = pulp.LpProblem("assign", pulp.LpMinimize)

    # 1 なら「w さんが t の作業を担当する」
    x = {(w, t): prob.add_variable(f"x_{w}_{t}", cat="Binary") for (w, t) in hours}

    load = {w: pulp.lpSum(hours[w, t] * x[w, t] for t in tasks if (w, t) in hours) for w in workers}
    total_hours = pulp.lpSum(load.values())
    total_cost = pulp.lpSum(workers[w]["wage"] * hours[w, t] * x[w, t] for (w, t) in hours)

    if objective == "hours":
        prob += total_hours, "total_hours"
    elif objective == "cost":
        prob += total_cost, "total_cost"
    elif objective == "max_load":
        z = prob.add_variable("max_load", lowBound=0)   # いちばん忙しい人の作業時間
        prob += z, "max_load"
        for w in workers:
            prob += load[w] <= z, f"le_max_{w}"

    for t in tasks:
        prob += pulp.lpSum(x[w, t] for w in workers if (w, t) in hours) == 1, f"one_{t}"
    for w in workers:
        prob += load[w] <= (MAX_HOURS if max_load is None else max_load), f"cap_{w}"

    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return {"status": stats.status_str}
    return {
        "status": stats.status_str,
        "cost": pulp.value(total_cost),
        "hours": pulp.value(total_hours),
        "load": {w: pulp.value(load[w]) for w in workers},
        "tasks": {w: [t for t in tasks if (w, t) in hours and x[w, t].value() > 0.5] for w in workers},
    }


def show(title, r):
    print(f"■ {title}: {r['status']}")
    if r["status"] != "Optimal":
        return
    print(f"  人件費 {r['cost']:,.0f} 円 / 合計 {r['hours']:.1f} 時間 / いちばん忙しい人 {max(r['load'].values()):.1f} 時間")
    for w in workers:
        names = "・".join(tasks[t] for t in r["tasks"][w]) or "（なし）"
        print(f"  {workers[w]['label']}: {r['load'][w]:.1f} 時間  {names}")


if __name__ == "__main__":
    show("合計時間を最小", solve_assign("hours"))
    show("人件費を最小", solve_assign("cost"))

    fair = solve_assign("max_load")
    best_max = max(fair["load"].values())
    show(f"公平（いちばん忙しい人を最小：{best_max:.1f} 時間）のなかで人件費を最小",
         solve_assign("cost", max_load=best_max + 1e-6))
