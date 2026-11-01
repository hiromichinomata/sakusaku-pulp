from pathlib import Path

import pandas as pd
import pulp

HERE = Path(__file__).parent
DAY_LABEL = {"mon": "月", "tue": "火", "wed": "水", "thu": "木", "fri": "金", "sat": "土"}


# ---- 入力 ----
def read_input(folder):
    staff = pd.read_csv(folder / "staff.csv").set_index("staff")
    roles = pd.read_csv(folder / "roles.csv").set_index("role")
    need = pd.read_csv(folder / "need.csv").set_index("day")
    unavailable = pd.read_csv(folder / "unavailable.csv")
    days = list(need.index)
    return {
        "staff": staff.to_dict("index"),
        "roles": roles.to_dict("index"),
        "days": days,
        "need": {(d, r): int(need.at[d, r]) for d in days for r in roles.index},
        "unavailable": set(zip(unavailable["staff"], unavailable["day"])),
    }


def check_days(d):
    """日ごとに「必要な人数」と「出られる人数」を比べる（解く前の簡単な検査）"""
    problems = []
    for day in d["days"]:
        needed = sum(n for (dd, r), n in d["need"].items() if dd == day)
        available = [p for p in d["staff"] if (p, day) not in d["unavailable"]]
        if needed > len(available):
            problems.append(f"{DAY_LABEL[day]}曜: {needed} 人必要なのに、出られるのは {len(available)} 人")
    return problems


# ---- モデル ----
def solve_crew(d, fair_weight=0):
    staff, roles, days = d["staff"], d["roles"], d["days"]
    prob = pulp.LpProblem("crew", pulp.LpMinimize)

    # スキルがあり、出られる日だけ変数を作る
    keys = [(p, day, r) for p in staff for day in days for r in roles
            if staff[p][r] == 1 and (p, day) not in d["unavailable"]]
    x = {k: prob.add_variable("x_{}_{}_{}".format(*k), cat="Binary") for k in keys}

    def X(p, day, r):
        return x.get((p, day, r), 0)

    hours = {p: pulp.lpSum(roles[r]["hours"] * X(p, day, r) for day in days for r in roles) for p in staff}
    cost = pulp.lpSum(staff[p]["wage"] * roles[r]["hours"] * x[p, day, r] for (p, day, r) in keys)
    most = prob.add_variable("most", lowBound=0)
    least = prob.add_variable("least", lowBound=0)
    fair_staff = [p for p in staff if staff[p].get("fair", 1) == 1]   # 公平さを比べる人
    for p in fair_staff:
        prob += hours[p] <= most, f"most_{p}"
        prob += hours[p] >= least, f"least_{p}"
    prob += cost + fair_weight * (most - least), "objective"

    for (day, r), n in d["need"].items():
        prob += pulp.lpSum(X(p, day, r) for p in staff) == n, f"need_{day}_{r}"
    for p, info in staff.items():
        for day in days:
            prob += pulp.lpSum(X(p, day, r) for r in roles) <= 1, f"one_{p}_{day}"
        prob += pulp.lpSum(X(p, day, r) for day in days for r in roles) <= info["max_days"], f"max_days_{p}"

    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return {"status": stats.status_str}
    h = {p: pulp.value(hours[p]) for p in staff}
    return {
        "status": stats.status_str,
        "cost": pulp.value(cost),
        "hours": h,
        "gap": max(h[p] for p in fair_staff) - min(h[p] for p in fair_staff),
        "roster": {(p, day): r for (p, day, r), v in x.items() if v.value() > 0.5},
    }


# ---- 出力 ----
def roster_table(d, result):
    rows = []
    for p, info in d["staff"].items():
        row = {"スタッフ": info["label"]}
        for day in d["days"]:
            if (p, day) in result["roster"]:
                row[DAY_LABEL[day]] = d["roles"][result["roster"][p, day]]["label"]
            elif (p, day) in d["unavailable"]:
                row[DAY_LABEL[day]] = "×"
            else:
                row[DAY_LABEL[day]] = "休"
        row["時間"] = round(result["hours"][p])
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    d = read_input(HERE / "data")

    problems = check_days(d)
    if problems:
        print("解く前の検査で問題が見つかりました:")
        for msg in problems:
            print("  -", msg)
        print("林さんに相談して、休みを土曜から金曜に変えてもらいます。")
        d["unavailable"].discard(("hayashi", "sat"))
        d["unavailable"].add(("hayashi", "fri"))
        assert not check_days(d)
    print()

    # 公平さの重みを変えて、複数の案を比べる
    print("| 公平さの重み | 人件費 | 勤務時間の差 | 森 | 林 | 川口 | 山本 | 中村 | 西田 |")
    print("|----------:|------:|----------:|---:|---:|----:|----:|----:|----:|")
    plans = {}
    for w in [0, 100, 200, 300]:
        r = solve_crew(d, fair_weight=w)
        plans[w] = r
        hs = " | ".join(f"{r['hours'][p]:.0f}" for p in d["staff"])
        print(f"| {w} | {r['cost']:,.0f} | {r['gap']:.0f} | {hs} |")
    print()

    chosen = plans[300]
    table = roster_table(d, chosen)
    print(table.to_string(index=False))
    table.to_csv(HERE / "roster.csv", index=False, encoding="utf-8-sig")
    table.to_excel(HERE / "roster.xlsx", index=False)
