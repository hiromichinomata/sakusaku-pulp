import pulp

# 1. 問題を作る（利益を最大化）
prob = pulp.LpProblem("ume_kobo", pulp.LpMaximize)

# 2. 意思決定変数
jam = prob.add_variable("jam", lowBound=0)      # うめジャムを作る量（kg）
syrup = prob.add_variable("syrup", lowBound=0)  # うめシロップを作る量（L）

# 3. 目的関数：利益の合計
prob += 800 * jam + 500 * syrup, "total_profit"

# 4. 制約条件
prob += 0.6 * jam + 0.5 * syrup <= 33, "ume_kg"
prob += 0.5 * jam + 0.2 * syrup <= 21, "work_hours"

# 5. 解く
stats = prob.solve(pulp.HiGHS(msg=False))

print("状態:", stats.status_str)
print("利益:", pulp.value(prob.objective), "円")
print("ジャム:", jam.value(), "kg")
print("シロップ:", syrup.value(), "L")
