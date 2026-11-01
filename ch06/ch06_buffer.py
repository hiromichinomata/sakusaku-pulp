import copy
from ch05_data_model import products, resources
from ch06_report import solve_and_collect, print_report

# 作業時間に1割の余裕を残す（720分 → 648分しか計画に使わない）
buffered = copy.deepcopy(resources)
buffered["work_min"]["capacity"] = int(12 * 60 * 0.9)

result = solve_and_collect(products, buffered)
print_report(result, products, buffered)
