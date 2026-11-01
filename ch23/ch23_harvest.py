import copy
import pulp

# 梅の収穫シーズン10日間と、そのあと5日間の加工計画（本書用の架空のデータ）
DAYS = list(range(1, 11))        # 収穫する日
WORK_DAYS = list(range(1, 16))   # 加工できる日（11〜15日目はシーズンのあと）

base = {
    # 収穫の見込み（kg）。前半は青梅、後半は完熟梅
    "harvest": {
        "green": {1: 30, 2: 40, 3: 45, 4: 40, 5: 20, 6: 10, 7: 0, 8: 0, 9: 0, 10: 0},
        "ripe":  {1: 0, 2: 0, 3: 0, 4: 10, 5: 25, 6: 40, 7: 50, 8: 50, 9: 35, 10: 20},
    },
    # 家族が加工に使える時間（時間）。6・7日目は週末、11〜15日目はシーズンのあと
    "hours": {1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 10, 7: 10, 8: 4, 9: 4, 10: 4,
              11: 4, 12: 4, 13: 4, 14: 4, 15: 4},
    "products": {
        "syrup":    {"label": "梅シロップ", "kind": "green", "value": 800,  "h_per_kg": 0.10, "max_kg": 150, "freezable": True},
        "umeboshi": {"label": "梅干し",     "kind": "ripe",  "value": 1200, "h_per_kg": 0.20, "max_kg": 120, "freezable": False},
        "jam":      {"label": "梅ジャム",   "kind": "ripe",  "value": 1000, "h_per_kg": 0.25, "max_kg": 100, "freezable": True},
    },
    "freezer_kg": 0,   # 冷凍庫に入る梅の量（kg）。0 なら冷凍庫なし
}
NEXT_DAY = 0.9     # 次の日に加工すると、価値が1割下がる
FROZEN = 0.95      # 冷凍してから加工すると、価値が5%下がる
FREEZE_DAYS = 5    # 冷凍した梅は、5日後までに加工する


def plans(d):
    """(収穫日 h, 加工日 t, 商品 p) の組み合わせと、その価値の倍率"""
    keys = {}
    for p, info in d["products"].items():
        for h in DAYS:
            if d["harvest"][info["kind"]][h] == 0:
                continue
            for t in WORK_DAYS:
                if t == h:
                    keys[h, t, p] = 1.0                 # その日のうちに加工
                elif t == h + 1:
                    keys[h, t, p] = NEXT_DAY            # 次の日に加工
                elif d["freezer_kg"] > 0 and info["freezable"] and h + 2 <= t <= h + FREEZE_DAYS:
                    keys[h, t, p] = FROZEN              # 冷凍して、あとで加工
    return keys


def solve_harvest(d):
    keys = plans(d)
    prob = pulp.LpProblem("harvest", pulp.LpMaximize)
    x = {k: prob.add_variable("x_{}_{}_{}".format(*k), lowBound=0) for k in keys}   # kg
    P = d["products"]

    prob += pulp.lpSum(P[p]["value"] * keys[h, t, p] * v for (h, t, p), v in x.items()), "value"

    for kind, by_day in d["harvest"].items():
        for h in DAYS:
            prob += pulp.lpSum(v for (hh, t, p), v in x.items()
                               if hh == h and P[p]["kind"] == kind) <= by_day[h], f"harvest_{kind}_{h}"
    for t in WORK_DAYS:
        prob += pulp.lpSum(P[p]["h_per_kg"] * v for (h, tt, p), v in x.items() if tt == t) \
            <= d["hours"][t], f"hours_{t}"
    for p in P:
        prob += pulp.lpSum(v for (h, t, pp), v in x.items() if pp == p) <= P[p]["max_kg"], f"max_{p}"
    if d["freezer_kg"] > 0:
        # その日の夜に冷凍庫に入っている梅（収穫日の翌日より後に加工するもの）
        for day in WORK_DAYS:
            prob += pulp.lpSum(v for (h, t, p), v in x.items() if t >= h + 2 and h <= day < t) \
                <= d["freezer_kg"], f"freezer_{day}"

    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return {"status": stats.status_str}
    total = sum(sum(by_day.values()) for by_day in d["harvest"].values())
    done = {p: sum(v.value() for (h, t, pp), v in x.items() if pp == p) for p in P}
    waste_by_day = {}
    for kind, by_day in d["harvest"].items():
        for h in DAYS:
            used = sum(v.value() for (hh, t, p), v in x.items() if hh == h and P[p]["kind"] == kind)
            if by_day[h] - used > 1e-6:
                waste_by_day[kind, h] = by_day[h] - used
    return {
        "status": stats.status_str,
        "value": pulp.value(prob.objective),
        "done": done,
        "waste": total - sum(done.values()),
        "total": total,
        "waste_by_day": waste_by_day,
        "hours_used": {t: sum(P[p]["h_per_kg"] * v.value() for (h, tt, p), v in x.items() if tt == t) for t in WORK_DAYS},
        "frozen": sum(v.value() for (h, t, p), v in x.items() if t >= h + 2),
    }


def show(title, r, d):
    print(f"■ {title}: {r['status']}")
    done = " / ".join(f"{d['products'][p]['label']} {kg:.1f}kg" for p, kg in r["done"].items())
    print(f"  価値 {r['value']:,.0f} 円 / 捨てる梅 {r['waste']:.1f} / {r['total']} kg / 冷凍 {r['frozen']:.1f} kg")
    print(f"  {done}")
    kind_label = {"green": "青梅", "ripe": "完熟梅"}
    waste = ", ".join(f"{h}日目{kind_label[k]} {kg:.1f}" for (k, h), kg in sorted(r["waste_by_day"].items(), key=lambda a: a[0][1]))
    print(f"  捨てる梅の内訳: {waste or 'なし'}")
    print("  作業時間: " + " ".join(f"{r['hours_used'][t]:.1f}/{d['hours'][t]}" for t in WORK_DAYS))


if __name__ == "__main__":
    show("1: 基本", solve_harvest(base), base)

    tournament = copy.deepcopy(base)
    tournament["hours"][6] = 4      # 6日目は道場の試合で、初花がいない
    show("2: 6日目に道場の試合", solve_harvest(tournament), tournament)

    freezer = copy.deepcopy(base)
    freezer["freezer_kg"] = 30
    show("3: 冷凍庫（30kg）を買う", solve_harvest(freezer), freezer)

    more_syrup = copy.deepcopy(freezer)
    more_syrup["products"]["syrup"]["max_kg"] = 200
    show("4: 冷凍庫＋シロップの売り先を増やす", solve_harvest(more_syrup), more_syrup)
