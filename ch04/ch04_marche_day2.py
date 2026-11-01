import pulp

prob = pulp.LpProblem("marche_day2", pulp.LpMaximize)

# 意思決定変数（単位：瓶・パック）
jam = prob.add_variable("jam", lowBound=10, cat="Integer")                    # 予約10瓶
syrup = prob.add_variable("syrup", lowBound=0, cat="Integer")
umeboshi = prob.add_variable("umeboshi", lowBound=0, upBound=20, cat="Integer")  # 棚は20パック

# 目的関数（円）
profit = 450 * jam + 400 * syrup + 500 * umeboshi
prob += profit, "total_profit"

# 制約条件（単位をそろえる：g と 分）
ume_g = 300 * jam + 400 * syrup + 500 * umeboshi
sugar_g = 200 * jam + 400 * syrup
work_min = 20 * jam + 10 * syrup + 15 * umeboshi

prob += ume_g <= 18 * 1000, "ume_g"        # 梅 18kg
prob += sugar_g <= 10 * 1000, "sugar_g"    # 砂糖 10kg
prob += work_min <= 12 * 60, "work_min"    # 作業 12時間
prob += jam + syrup <= 50, "jars"          # 瓶 50個

stats = prob.solve(pulp.HiGHS(msg=False))

print("状態:", stats.status_str)
print(f"利益: {pulp.value(profit):,.0f} 円")
print(f"ジャム {jam.value():.0f} 瓶 / シロップ {syrup.value():.0f} 瓶 / 梅干し {umeboshi.value():.0f} パック")
print(f"梅   {pulp.value(ume_g):>6,.0f} / 18,000 g")
print(f"砂糖 {pulp.value(sugar_g):>6,.0f} / 10,000 g")
print(f"作業 {pulp.value(work_min):>6,.0f} /    720 分")
print(f"瓶   {pulp.value(jam + syrup):>6,.0f} /     50 個")
