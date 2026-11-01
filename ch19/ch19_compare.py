import time
import pulp
from ch12_scale import make_data

SOLVERS = {
    "HiGHS": lambda **kw: pulp.HiGHS(**kw),
    "CBC": lambda **kw: pulp.COIN_CMD(**kw),
    "GLPK": lambda **kw: pulp.PYGLPK(**kw),
    "SCIP": lambda **kw: pulp.SCIP_PY(**kw),
}


def build(n):
    value, use, cap = make_data(n)
    prob = pulp.LpProblem("select", pulp.LpMaximize)
    x = [prob.add_variable(f"x{i}", cat="Binary") for i in range(n)]
    prob += pulp.lpSum(v * xi for v, xi in zip(value, x))
    for k, row in enumerate(use):
        prob += pulp.lpSum(u * xi for u, xi in zip(row, x)) <= cap[k], f"res_{k}"
    return prob


if __name__ == "__main__":
    available = pulp.listSolvers(onlyAvailable=True)
    print("使えるソルバー:", available)
    print()
    print("| ソルバー | 状態 | 目的関数 | 秒 |")
    print("|---------|------|-------:|---:|")
    for name, make_solver in SOLVERS.items():
        prob = build(100)
        solver = make_solver(msg=False, timeLimit=60)
        if not solver.available():
            print(f"| {name} | 使えない | — | — |")
            continue
        start = time.perf_counter()
        try:
            stats = prob.solve(solver)
            print(f"| {name} | {stats.status_str} | {pulp.value(prob.objective):,.0f} | {time.perf_counter() - start:.2f} |")
        except Exception as e:
            print(f"| {name} | エラー: {type(e).__name__} | — | — |")
