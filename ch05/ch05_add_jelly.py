import pulp
from ch05_data_model import products, resources, build_model, report

# 商品を1つ追加：梅ゼリー
products["jelly"] = {"label": "ゼリー", "profit": 350, "min": 0, "max": None}

# 既存の資源に使用量を追加
resources["ume_g"]["use"]["jelly"] = 200
resources["sugar_g"]["use"]["jelly"] = 100
resources["work_min"]["use"]["jelly"] = 10

# 資源を1つ追加：冷蔵ケースの棚（ゼリーだけが使う）
resources["fridge"] = {"label": "冷蔵棚(個)", "capacity": 24, "use": {"jelly": 1}}

prob, make, used = build_model(products, resources)
stats = prob.solve(pulp.HiGHS(msg=False))
report(prob, stats, make, used, products, resources)
