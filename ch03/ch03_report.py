import pulp

prob = pulp.LpProblem("ume_kobo", pulp.LpMaximize)

jam = prob.add_variable("jam", lowBound=0)
syrup = prob.add_variable("syrup", lowBound=0)

profit = 800 * jam + 500 * syrup
ume_used = 0.6 * jam + 0.5 * syrup
hours_used = 0.5 * jam + 0.2 * syrup

prob += profit, "total_profit"
prob += ume_used <= 33, "ume_kg"
prob += hours_used <= 21, "work_hours"

stats = prob.solve(pulp.HiGHS(msg=False))

print(f"状態: {stats.status_str}")
print(f"ジャムを {jam.value():.1f} kg、シロップを {syrup.value():.1f} L 作ると、")
print(f"利益は {pulp.value(profit):,.0f} 円で最大になります。")
print(f"梅は {pulp.value(ume_used):.1f} / 33 kg、作業時間は {pulp.value(hours_used):.1f} / 21 時間 使います。")
