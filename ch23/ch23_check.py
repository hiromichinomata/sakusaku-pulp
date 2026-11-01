import copy
from ch23_harvest import base, solve_harvest

# テスト1：時間も販売先もたっぷりあれば、捨てる梅は0
d = copy.deepcopy(base)
d["hours"] = {t: 100 for t in d["hours"]}
for p in d["products"].values():
    p["max_kg"] = 10_000
r = solve_harvest(d)
assert r["waste"] < 1e-6, r["waste"]
print("テスト1 OK: 時間と販売先が十分なら、捨てる梅は", round(r["waste"], 3), "kg")

# テスト2：作業時間が0なら、何も加工できず全部捨てる
d = copy.deepcopy(base)
d["hours"] = {t: 0 for t in d["hours"]}
r = solve_harvest(d)
assert abs(r["waste"] - r["total"]) < 1e-6 and abs(r["value"]) < 1e-6
print("テスト2 OK: 作業時間が0なら、価値は", r["value"], "円で全部捨てる")

# テスト3：冷凍庫を足して、価値が下がることはない（選択肢が増えるだけ）
r0 = solve_harvest(base)
d = copy.deepcopy(base)
d["freezer_kg"] = 30
r1 = solve_harvest(d)
assert r1["value"] >= r0["value"] - 1e-6
print(f"テスト3 OK: 冷凍庫なし {r0['value']:,.0f} 円 ≦ 冷凍庫あり {r1['value']:,.0f} 円")
