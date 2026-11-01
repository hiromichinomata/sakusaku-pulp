"""検証：モデルとは別に、データだけで答えを確かめる"""
TOL = 1e-6


def verify(d: dict, make: dict) -> list[str]:
    problems = []
    total = {p: 0.0 for p in d["products"]}
    for (p, l), x in make.items():
        if abs(x - round(x)) > TOL:
            problems.append(f"{p}×{l}: 整数ではない ({x})")
        if x < -TOL:
            problems.append(f"{p}×{l}: マイナス ({x})")
        total[p] += x
    for l, info in d["lines"].items():
        used = sum(d["line_time"][p, m] * x for (p, m), x in make.items() if m == l)
        if used > info["hours"] + TOL:
            problems.append(f"ライン {l}: {used} 時間 > {info['hours']} 時間")
    for r, cap in d["capacity"].items():
        used = sum(d["usage"].get((p, r), 0) * x for p, x in total.items())
        if used > cap + TOL:
            problems.append(f"資源 {r}: {used} > {cap}")
    for p, info in d["products"].items():
        if total[p] > info["demand"] + TOL:
            problems.append(f"{p}: 需要 {info['demand']} を超える ({total[p]})")
        if total[p] < info["min"] - TOL:
            problems.append(f"{p}: 最低生産数 {info['min']} に届かない ({total[p]})")
    return problems
