import pulp

prob = pulp.LpProblem("ume_min_hours", pulp.LpMinimize)

jam = prob.add_variable("jam", lowBound=20)      # 注文：ジャム20kg以上
syrup = prob.add_variable("syrup", lowBound=20)  # 注文：シロップ20L以上

prob += 0.5 * jam + 0.2 * syrup, "work_hours"
prob += 0.6 * jam + 0.5 * syrup <= 33, "ume_kg"

stats = prob.solve(pulp.HiGHS(msg=False))
print("状態:", stats.status_str)
print("作業時間:", pulp.value(prob.objective), "時間")
print("ジャム:", jam.value(), "kg / シロップ:", syrup.value(), "L")
