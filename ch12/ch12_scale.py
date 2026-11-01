import random
import time
import pulp


def make_data(n, m=5, seed=1):
    """n 個の候補・m 種類の資源をもつ、ランダムな選択問題を作る"""
    rng = random.Random(seed)
    value = [rng.randint(10, 100) for _ in range(n)]
    use = [[rng.randint(5, 50) for _ in range(n)] for _ in range(m)]
    cap = [sum(row) // 2 for row in use]
    return value, use, cap


def solve(n, cat):
    value, use, cap = make_data(n)
    prob = pulp.LpProblem("select", pulp.LpMaximize)
    x = [prob.add_variable(f"x{i}", lowBound=0, upBound=1, cat=cat) for i in range(n)]
    prob += pulp.lpSum(v * xi for v, xi in zip(value, x))
    for k, row in enumerate(use):
        prob += pulp.lpSum(u * xi for u, xi in zip(row, x)) <= cap[k], f"res_{k}"
    start = time.perf_counter()
    stats = prob.solve(pulp.HiGHS(msg=False, timeLimit=60))
    elapsed = time.perf_counter() - start
    return stats.status_str, pulp.value(prob.objective), elapsed


if __name__ == "__main__":
    print("| 候補の数 | 連続（0〜1） | 秒 | バイナリ | 秒 |")
    print("|-------:|-----------:|---:|-------:|---:|")
    for n in [25, 50, 100, 200, 400]:
        s1, v1, t1 = solve(n, "Continuous")
        s2, v2, t2 = solve(n, "Binary")
        print(f"| {n} | {v1:,.1f} | {t1:.2f} | {v2:,.0f}（{s2}） | {t2:.2f} |")
