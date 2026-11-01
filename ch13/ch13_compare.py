import itertools
import random
import time
import pulp


def make_items(n, seed=7):
    rng = random.Random(seed)
    return {f"item{i:02d}": (rng.randint(50, 400), rng.randint(50, 500)) for i in range(n)}  # (費用, 効果)


def brute_force(items, budget):
    names = list(items)
    best_value, best_pick = -1, None
    for picks in itertools.product([0, 1], repeat=len(names)):
        cost = sum(items[n][0] for n, p in zip(names, picks) if p)
        if cost > budget:
            continue
        value = sum(items[n][1] for n, p in zip(names, picks) if p)
        if value > best_value:
            best_value, best_pick = value, picks
    return best_value


def with_pulp(items, budget):
    prob = pulp.LpProblem("knapsack", pulp.LpMaximize)
    y = {n: prob.add_variable(f"pick_{n}", cat="Binary") for n in items}
    prob += pulp.lpSum(items[n][1] * y[n] for n in items)
    prob += pulp.lpSum(items[n][0] * y[n] for n in items) <= budget
    prob.solve(pulp.HiGHS(msg=False))
    return pulp.value(prob.objective)


if __name__ == "__main__":
    print("| 候補の数 | 組み合わせの数 | 全探索 | 秒 | PuLP | 秒 |")
    print("|-------:|------------:|------:|---:|-----:|---:|")
    for n in [10, 14, 18, 22]:
        items = make_items(n)
        budget = sum(c for c, v in items.values()) // 3
        t0 = time.perf_counter(); bf = brute_force(items, budget); t1 = time.perf_counter()
        pl = with_pulp(items, budget); t2 = time.perf_counter()
        print(f"| {n} | {2 ** n:,} | {bf:,} | {t1 - t0:.2f} | {pl:,.0f} | {t2 - t1:.2f} |")
