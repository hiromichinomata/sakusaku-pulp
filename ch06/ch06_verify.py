import pulp
from ch05_data_model import products, resources, build_model

TOL = 1e-6


def get_solution(make):
    """変数の値を {商品: 数} の普通の辞書にする"""
    return {p: var.value() for p, var in make.items()}


def verify(solution, products, resources):
    """ソルバーの答えを、データだけを使って自分で確かめる"""
    problems = []
    for p, x in solution.items():
        info = products[p]
        if abs(x - round(x)) > TOL:
            problems.append(f"{p}: 整数ではない ({x})")
        if x < info["min"] - TOL:
            problems.append(f"{p}: 下限 {info['min']} を下回る ({x})")
        if info["max"] is not None and x > info["max"] + TOL:
            problems.append(f"{p}: 上限 {info['max']} を超える ({x})")
    for r, info in resources.items():
        used = sum(info["use"].get(p, 0) * x for p, x in solution.items())
        if used > info["capacity"] + TOL:
            problems.append(f"{r}: 上限 {info['capacity']} を超える ({used})")
    return problems


if __name__ == "__main__":
    prob, make, used = build_model(products, resources)
    stats = prob.solve(pulp.HiGHS(msg=False))

    if stats.status_str != "Optimal":
        raise SystemExit(f"最適解が得られませんでした: {stats.status_str}")

    solution = get_solution(make)
    print("解:", solution)

    problems = verify(solution, products, resources)
    print("検証:", "OK" if not problems else problems)

    # わざと間違った案を検証してみる
    bad = {"jam": 20, "syrup": 13, "umeboshi": 14.5}
    print("間違った案の検証:")
    for msg in verify(bad, products, resources):
        print("  -", msg)
