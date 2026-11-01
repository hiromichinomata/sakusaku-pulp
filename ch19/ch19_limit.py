import time
import pulp
from ch19_compare import SOLVERS, build

print("| ソルバー | 時間制限 | 状態 | 解あり | 目的関数 | 上限 | ギャップ | 秒 |")
print("|---------|-------:|------|:----:|-------:|----:|-------:|---:|")
for name, make_solver in SOLVERS.items():
    for limit in [2, 60]:
        prob = build(400)
        start = time.perf_counter()
        stats = prob.solve(make_solver(msg=False, timeLimit=limit))
        obj = pulp.value(prob.objective) if stats.has_solution else None
        bound = stats.best_bound
        gap = (bound - obj) / obj if (obj and bound) else None
        print(f"| {name} | {limit} | {stats.status_str} | {'○' if stats.has_solution else '×'} | "
              f"{'—' if obj is None else f'{obj:,.0f}'} | {bound if bound is None else f'{bound:,.1f}'} | "
              f"{'—' if gap is None else f'{gap:.3%}'} | {time.perf_counter() - start:.2f} |")
