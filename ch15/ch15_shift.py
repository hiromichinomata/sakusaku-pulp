import pulp

# うめ食品 梅田店の1週間のシフト（本書用の架空のデータ）
days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
day_label = {"mon": "月", "tue": "火", "wed": "水", "thu": "木", "fri": "金", "sat": "土", "sun": "日"}
shifts = {"early": "早番", "late": "遅番"}   # 早番 9〜14時、遅番 14〜19時（各5時間）

# 必要人数：平日は早番1人・遅番2人、土日は早番2人・遅番3人
need = {}
for d in days:
    weekend = d in ("sat", "sun")
    need[d, "early"] = 2 if weekend else 1
    need[d, "late"] = 3 if weekend else 2

staff = {
    "aoki":  {"label": "青木", "wage": 1300, "min": 2, "max": 5},
    "inoue": {"label": "井上", "wage": 1250, "min": 2, "max": 5},
    "ueda":  {"label": "上田", "wage": 1100, "min": 2, "max": 5},
    "endo":  {"label": "遠藤", "wage": 1100, "min": 2, "max": 5},
    "ono":   {"label": "小野", "wage": 1000, "min": 2, "max": 5},
    "kato":  {"label": "加藤", "wage": 1000, "min": 2, "max": 5},
}

# 勤務できない日・シフト（学校・ほかの仕事など）
unavailable = {
    ("aoki", "sun", "early"), ("aoki", "sun", "late"),
    ("inoue", "wed", "early"), ("inoue", "wed", "late"),
    ("ueda", "mon", "early"), ("ueda", "tue", "early"), ("ueda", "wed", "early"),
    ("ueda", "thu", "early"), ("ueda", "fri", "early"),
    ("endo", "sat", "late"), ("endo", "sun", "late"),
    ("ono", "thu", "early"), ("ono", "thu", "late"),
    ("kato", "mon", "late"), ("kato", "tue", "late"),
}

# 入りたい（+1）・できれば避けたい（-1）という希望
wish = {
    ("aoki", "sat", "early"): 1, ("aoki", "fri", "late"): 1, ("inoue", "mon", "early"): 1,
    ("ono", "sun", "early"): -1, ("ono", "sat", "late"): -1,
    ("kato", "sat", "early"): -1, ("kato", "sun", "early"): -1, ("kato", "fri", "late"): -1,
}

HOURS = 5
MAX_STREAK = 3        # 4日連続では働かない
WISH_YEN = 1000       # 希望1件を、いくら分の価値とみなすか
FAIR_YEN = 3000       # 勤務回数の差1回を、いくら分の不公平とみなすか


def solve_shift(rules):
    prob = pulp.LpProblem("shift", pulp.LpMinimize)

    keys = [(p, d, s) for p in staff for d in days for s in shifts if (p, d, s) not in unavailable]
    x = {k: prob.add_variable("x_{}_{}_{}".format(*k), cat="Binary") for k in keys}

    def X(p, d, s):
        return x.get((p, d, s), 0)   # 勤務できない枠は 0 として扱う

    count = {p: pulp.lpSum(X(p, d, s) for d in days for s in shifts) for p in staff}
    cost = pulp.lpSum(staff[p]["wage"] * HOURS * x[p, d, s] for (p, d, s) in keys)
    wish_score = pulp.lpSum(w * X(p, d, s) for (p, d, s), w in wish.items())

    objective = cost
    if "wish" in rules:
        objective = objective - WISH_YEN * wish_score
    if "fair" in rules:
        most = prob.add_variable("most", lowBound=0)     # いちばん多い人の勤務回数
        least = prob.add_variable("least", lowBound=0)   # いちばん少ない人の勤務回数
        for p in staff:
            prob += count[p] <= most, f"most_{p}"
            prob += count[p] >= least, f"least_{p}"
        objective = objective + FAIR_YEN * (most - least)
    prob += objective, "objective"

    # 必要人数を満たす
    for (d, s), n in need.items():
        prob += pulp.lpSum(X(p, d, s) for p in staff) >= n, f"need_{d}_{s}"

    for p, info in staff.items():
        prob += count[p] >= info["min"], f"min_{p}"
        prob += count[p] <= info["max"], f"max_{p}"
        for d in days:
            prob += pulp.lpSum(X(p, d, s) for s in shifts) <= 1, f"one_per_day_{p}_{d}"

    if "rest" in rules:
        # 遅番の次の日に早番は入れない（休息時間を確保する）
        for p in staff:
            for d1, d2 in zip(days, days[1:]):
                prob += X(p, d1, "late") + X(p, d2, "early") <= 1, f"rest_{p}_{d1}"

    if "streak" in rules:
        # どの連続する MAX_STREAK+1 日を見ても、勤務は MAX_STREAK 日以下
        for p in staff:
            for i in range(len(days) - MAX_STREAK):
                window = days[i:i + MAX_STREAK + 1]
                prob += pulp.lpSum(X(p, d, s) for d in window for s in shifts) <= MAX_STREAK, \
                    f"streak_{p}_{window[0]}"

    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return {"status": stats.status_str}
    return {
        "status": stats.status_str,
        "cost": pulp.value(cost),
        "wish": pulp.value(wish_score),
        "sol": {k for k, v in x.items() if v.value() > 0.5},
    }


def check(sol):
    """できあがったシフトの「遅番→翌日早番」の数と、最長の連勤日数を数える"""
    late_early = sum(
        1 for p in staff for d1, d2 in zip(days, days[1:])
        if (p, d1, "late") in sol and (p, d2, "early") in sol
    )
    longest = 0
    for p in staff:
        run = 0
        for d in days:
            run = run + 1 if any((p, d, s) in sol for s in shifts) else 0
            longest = max(longest, run)
    return late_early, longest


def show(title, r):
    print(f"■ {title}: {r['status']}")
    if r["status"] != "Optimal":
        return
    late_early, longest = check(r["sol"])
    counts = [sum(1 for (q, d, s) in r["sol"] if q == p) for p in staff]
    print(f"  人件費 {r['cost']:,.0f} 円 / 希望 {r['wish']:+.0f} / 遅→早 {late_early} 件 / "
          f"最長連勤 {longest} 日 / 回数の差 {max(counts) - min(counts)}")
    print("  |      | " + " | ".join(day_label[d] for d in days) + " | 回数 |")
    for p, n in zip(staff, counts):
        cells = []
        for d in days:
            if (p, d, "early") in r["sol"]:
                cells.append("早")
            elif (p, d, "late") in r["sol"]:
                cells.append("遅")
            elif (p, d, "early") in unavailable and (p, d, "late") in unavailable:
                cells.append("×")
            else:
                cells.append("・")
        print(f"  | {staff[p]['label']} | " + " | ".join(cells) + f" |  {n}  |")


if __name__ == "__main__":
    rules = []
    for title, rule in [
        ("1: 必要人数・勤務できない日・回数", None),
        ("2: ＋遅番の翌日は早番にしない", "rest"),
        ("3: ＋4連勤しない", "streak"),
        ("4: ＋希望を考える", "wish"),
        ("5: ＋勤務回数を公平に", "fair"),
    ]:
        if rule:
            rules.append(rule)
        show(title, solve_shift(rules))
