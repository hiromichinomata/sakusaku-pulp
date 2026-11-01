import pulp

# 倉庫の在庫（ケース）と店舗の注文（ケース）。本書用の架空のデータ
supply = {"osaka": 300, "wakayama": 200, "nagoya": 250}
demand = {"kyoto": 150, "kobe": 120, "nara": 100, "tsu": 130, "umeda": 180}

# 1ケースあたりの輸送費（円）。和歌山→津は直通便がない
cost = {
    ("osaka", "kyoto"): 300, ("osaka", "kobe"): 250, ("osaka", "nara"): 280, ("osaka", "tsu"): 600, ("osaka", "umeda"): 100,
    ("wakayama", "kyoto"): 500, ("wakayama", "kobe"): 450, ("wakayama", "nara"): 350, ("wakayama", "umeda"): 350,
    ("nagoya", "kyoto"): 400, ("nagoya", "kobe"): 650, ("nagoya", "nara"): 450, ("nagoya", "tsu"): 250, ("nagoya", "umeda"): 450,
}

labels = {
    "osaka": "大阪倉庫", "wakayama": "和歌山倉庫", "nagoya": "名古屋倉庫",
    "kyoto": "京都店", "kobe": "神戸店", "nara": "奈良店", "tsu": "津店", "umeda": "梅田店",
}


def solve_transport(supply, demand, cost):
    prob = pulp.LpProblem("transport", pulp.LpMinimize)

    ship = {(w, s): prob.add_variable(f"ship_{w}_{s}", lowBound=0) for (w, s) in cost}

    prob += pulp.lpSum(cost[k] * ship[k] for k in cost), "total_cost"

    for w in supply:
        prob += pulp.lpSum(ship[w, s] for s in demand if (w, s) in cost) <= supply[w], f"supply_{w}"
    for s in demand:
        prob += pulp.lpSum(ship[w, s] for w in supply if (w, s) in cost) == demand[s], f"demand_{s}"

    stats = prob.solve(pulp.HiGHS(msg=False))
    return stats, prob, ship


def print_plan(supply, demand, cost, ship):
    stores = list(demand)
    print("| 倉庫 \\ 店舗 | " + " | ".join(labels[s] for s in stores) + " | 出荷計 | 在庫 |")
    print("|---" * (len(stores) + 3) + "|")
    for w in supply:
        row = [f"{ship[w, s].value():.0f}" if (w, s) in cost else "—" for s in stores]
        out = sum(ship[w, s].value() for s in stores if (w, s) in cost)
        print(f"| {labels[w]} | " + " | ".join(row) + f" | {out:.0f} | {supply[w]} |")


if __name__ == "__main__":
    stats, prob, ship = solve_transport(supply, demand, cost)
    print("状態:", stats.status_str)
    print(f"輸送費: {pulp.value(prob.objective):,.0f} 円")
    print_plan(supply, demand, cost, ship)
