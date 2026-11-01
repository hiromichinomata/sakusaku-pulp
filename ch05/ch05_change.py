import copy
import pulp
from ch05_data_model import products, resources, build_model, report

# 元のデータを壊さないようにコピーしてから変更する
more_hours = copy.deepcopy(resources)
more_hours["work_min"]["capacity"] = 14 * 60   # 12時間 → 14時間

prob, make, used = build_model(products, more_hours)
stats = prob.solve(pulp.HiGHS(msg=False))
report(prob, stats, make, used, products, more_hours)
