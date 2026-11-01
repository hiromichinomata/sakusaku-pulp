import pulp
from ch05_data_model import products, resources, build_model
from ch06_verify import verify

TOL = 1e-6


def solve_and_collect(products, resources):
    prob, make, used = build_model(products, resources)
    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        raise RuntimeError(f"最適解が得られませんでした: {stats.status_str}")

    raw = {p: var.value() for p, var in make.items()}
    problems = verify(raw, products, resources)
    if problems:
        raise RuntimeError(f"検証に失敗しました: {problems}")

    result = {
        "profit": pulp.value(prob.objective),
        "make": {p: round(x) for p, x in raw.items()},   # 整数変数なので丸めて持つ
        "resources": {},
    }
    for r, info in resources.items():
        u = pulp.value(used[r])
        result["resources"][r] = {
            "used": u,
            "capacity": info["capacity"],
            "slack": info["capacity"] - u,
            "rate": u / info["capacity"],
            "binding": info["capacity"] - u < TOL,
        }
    return result


def print_report(result, products, resources):
    print(f"利益合計: {result['profit']:,.0f} 円")
    print()
    print("| 商品 | 数 | 利益 |")
    print("|------|---:|-----:|")
    for p, n in result["make"].items():
        print(f"| {products[p]['label']} | {n} | {products[p]['profit'] * n:,} |")
    print()
    print("| 資源 | 使用量 | 上限 | 余り | 使用率 | 効いている |")
    print("|------|------:|-----:|-----:|------:|:---------:|")
    for r, d in result["resources"].items():
        mark = "★" if d["binding"] else ""
        print(f"| {resources[r]['label']} | {d['used']:,.0f} | {d['capacity']:,} | "
              f"{d['slack']:,.0f} | {d['rate']:.0%} | {mark} |")


if __name__ == "__main__":
    result = solve_and_collect(products, resources)
    print_report(result, products, resources)
