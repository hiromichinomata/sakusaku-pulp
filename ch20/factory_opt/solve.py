"""解法：設定に従ってソルバーを選び、解いて、結果を普通の辞書で返す"""
import pulp

SOLVERS = {
    "HiGHS": pulp.HiGHS,
    "CBC": pulp.COIN_CMD,
    "GLPK": pulp.PYGLPK,
    "SCIP": pulp.SCIP_PY,
}


class SolveError(Exception):
    """使える解が得られなかったときに投げる例外"""


def make_solver(cfg: dict):
    name = cfg.get("name", "HiGHS")
    if name not in SOLVERS:
        raise SolveError(f"知らないソルバー: {name}")
    solver = SOLVERS[name](msg=cfg.get("msg", False), timeLimit=cfg.get("time_limit"), gapRel=cfg.get("gap_rel"))
    if not solver.available():
        raise SolveError(f"ソルバー {name} が使えません（インストールを確認してください）")
    return solver


def solve(prob, make, cfg: dict) -> dict:
    stats = prob.solve(make_solver(cfg))
    if not stats.has_solution:
        raise SolveError(f"解が得られませんでした: {stats.status_str}")
    return {
        "status": stats.status_str,
        "profit": pulp.value(prob.objective),
        "make": {k: v.value() for k, v in make.items()},
        "seconds": stats.time,
        "solver": stats.solver,
    }
