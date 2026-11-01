import pulp


def build(sense):
    prob = pulp.LpProblem("ume_kobo", sense)
    jam = prob.add_variable("jam", lowBound=0)
    syrup = prob.add_variable("syrup", lowBound=0)
    exprs = {
        "profit": 1000 * jam + 400 * syrup,   # ジャムの利益が1,000円、シロップが400円
        "ume": 0.6 * jam + 0.5 * syrup,
        "hours": 0.5 * jam + 0.2 * syrup,
    }
    prob += exprs["ume"] <= 33, "ume_kg"
    prob += exprs["hours"] <= 21, "work_hours"
    return prob, jam, syrup, exprs


def show(title, stats, jam, syrup, exprs):
    print(f"[{title}] {stats.status_str}: 利益 {pulp.value(exprs['profit']):,.0f} 円 / "
          f"ジャム {jam.value():.1f} kg / シロップ {syrup.value():.1f} L / 梅 {pulp.value(exprs['ume']):.1f} kg")


# 1段目：利益を最大化
prob, jam, syrup, exprs = build(pulp.LpMaximize)
prob += exprs["profit"], "total_profit"
stats = prob.solve(pulp.HiGHS(msg=False))
show("利益最大", stats, jam, syrup, exprs)
best = pulp.value(exprs["profit"])

# 2段目：利益は最大のまま、梅の使用量を最小化
prob, jam, syrup, exprs = build(pulp.LpMinimize)
prob += exprs["ume"], "ume_used"
prob += exprs["profit"] >= best - 1e-6, "keep_best_profit"
stats = prob.solve(pulp.HiGHS(msg=False))
show("梅を節約", stats, jam, syrup, exprs)

# 2段目（別案）：利益は最大のまま、シロップを最大化
prob, jam, syrup, exprs = build(pulp.LpMaximize)
prob += syrup, "syrup_amount"
prob += exprs["profit"] >= best - 1e-6, "keep_best_profit"
stats = prob.solve(pulp.HiGHS(msg=False))
show("シロップ多め", stats, jam, syrup, exprs)
