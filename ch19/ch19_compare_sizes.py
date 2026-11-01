import time
import pulp
from ch19_compare import SOLVERS, build

print("| 候補の数 | ソルバー | 状態 | 目的関数 | 秒 |")
print("|-------:|---------|------|-------:|---:|")
for n in [100, 200, 300]:
    for name, make_solver in SOLVERS.items():
        prob = build(n)
        start = time.perf_counter()
        stats = prob.solve(make_solver(msg=False, timeLimit=60))
        print(f"| {n} | {name} | {stats.status_str} | {pulp.value(prob.objective):,.0f} | {time.perf_counter() - start:.2f} |")
