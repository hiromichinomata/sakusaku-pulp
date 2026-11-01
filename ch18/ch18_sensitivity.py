import pulp


def solve_ume(ume_kg=33, work_hours=21):
    prob = pulp.LpProblem("ume_kobo", pulp.LpMaximize)
    jam = prob.add_variable("jam", lowBound=0)
    syrup = prob.add_variable("syrup", lowBound=0)
    prob += 800 * jam + 500 * syrup, "total_profit"
    prob += 0.6 * jam + 0.5 * syrup <= ume_kg, "ume_kg"
    prob += 0.5 * jam + 0.2 * syrup <= work_hours, "work_hours"
    stats = prob.solve(pulp.HiGHS(msg=False))
    return prob, stats, jam, syrup


prob, stats, jam, syrup = solve_ume()
base = pulp.value(prob.objective)
print(f"基本: 利益 {base:,.1f} 円（ジャム {jam.value():.1f} kg / シロップ {syrup.value():.1f} L）")
print()
print("| 制約 | 余り | 双対価格（pi） |")
print("|------|-----:|-------------:|")
for c in prob.constraints():
    print(f"| {c.name} | {abs(c.slack):.1f} | {c.pi:,.1f} |")

print()
for name, kwargs in [("梅を 34 kg に", {"ume_kg": 34}), ("作業を 22 時間に", {"work_hours": 22}),
                     ("梅を 43 kg に", {"ume_kg": 43}), ("梅を 60 kg に", {"ume_kg": 60})]:
    p, s, j, y = solve_ume(**kwargs)
    v = pulp.value(p.objective)
    print(f"{name}: 利益 {v:,.1f} 円（+{v - base:,.1f}） ジャム {j.value():.1f} / シロップ {y.value():.1f}")
