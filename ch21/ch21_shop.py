import copy
from pathlib import Path

import pandas as pd
import pulp

HERE = Path(__file__).parent
TOL = 1e-6


# ---- 入力 ----
def read_input(folder):
    products = pd.read_csv(folder / "products.csv")
    resources = pd.read_csv(folder / "resources.csv")
    settings = pd.read_csv(folder / "settings.csv")
    problems = []
    if products.isna().any().any() or resources.isna().any().any():
        problems.append("空欄がある")
    for r in resources["resource"]:
        if r not in products.columns:
            problems.append(f"products.csv に資源 '{r}' の列がない")
    if (products.select_dtypes("number") < 0).any().any():
        problems.append("products.csv にマイナスの値がある")
    if problems:
        raise ValueError("\n".join(problems))
    return {
        "products": products.set_index("product").to_dict("index"),
        "capacity": resources.set_index("resource")["capacity"].to_dict(),
        "labels": resources.set_index("resource")["label"].to_dict(),
        "settings": settings.set_index("key")["value"].to_dict(),
    }


# ---- モデル ----
def build_model(d):
    P, cap, s = d["products"], d["capacity"], d["settings"]
    prob = pulp.LpProblem("ume_shop", pulp.LpMaximize)

    make = {p: prob.add_variable(f"make_{p}", lowBound=0, upBound=P[p]["demand"], cat="Integer") for p in P}
    launch = {p: prob.add_variable(f"launch_{p}", cat="Binary") for p in P}

    margin = pulp.lpSum((P[p]["price"] - P[p]["material"] - s["shipping"]) * make[p] for p in P)
    launch_cost = pulp.lpSum(P[p]["launch_cost"] * launch[p] for p in P)
    material = pulp.lpSum(P[p]["material"] * make[p] for p in P)
    prob += margin - launch_cost, "profit"

    for r in cap:
        prob += pulp.lpSum(P[p][r] * make[p] for p in P) <= cap[r], f"res_{r}"
    prob += material + launch_cost <= s["budget"], "budget"           # 仕入れと発売準備に使えるお金
    prob += pulp.lpSum(launch.values()) <= s["max_items"], "max_items"
    for p, info in P.items():
        prob += make[p] <= info["demand"] * launch[p], f"launch_max_{p}"
        prob += make[p] >= info["min_lot"] * launch[p], f"launch_min_{p}"
        if info["must"]:
            prob += launch[p] == 1, f"must_{p}"
    return prob, make, launch


# ---- 解く・検証する ----
def solve(d):
    prob, make, launch = build_model(d)
    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        raise RuntimeError(f"最適解が得られませんでした: {stats.status_str}")
    qty = {p: round(make[p].value()) for p in d["products"]}
    launched = [p for p in d["products"] if launch[p].value() > 0.5]
    return {"profit": pulp.value(prob.objective), "qty": qty, "launched": launched}


def verify(d, result):
    P, cap, s = d["products"], d["capacity"], d["settings"]
    q, launched = result["qty"], result["launched"]
    problems = []
    for r in cap:
        used = sum(P[p][r] * q[p] for p in P)
        if used > cap[r] + TOL:
            problems.append(f"{r}: {used} > {cap[r]}")
    spend = sum(P[p]["material"] * q[p] for p in P) + sum(P[p]["launch_cost"] for p in launched)
    if spend > s["budget"] + TOL:
        problems.append(f"予算: {spend} > {s['budget']}")
    if len(launched) > s["max_items"]:
        problems.append(f"商品数: {len(launched)} > {s['max_items']}")
    for p, info in P.items():
        if p in launched and not (info["min_lot"] <= q[p] <= info["demand"]):
            problems.append(f"{p}: {q[p]} が最低ロット〜需要の範囲外")
        if p not in launched and q[p] != 0:
            problems.append(f"{p}: 出さないのに {q[p]} 個作っている")
        if info["must"] and p not in launched:
            problems.append(f"{p}: 必須なのに出していない")
    profit = sum((P[p]["price"] - P[p]["material"] - s["shipping"]) * q[p] for p in P) \
        - sum(P[p]["launch_cost"] for p in launched)
    if abs(profit - result["profit"]) > 1e-3:
        problems.append(f"利益の計算が合わない: {profit} と {result['profit']}")
    return problems


# ---- レポート ----
def report(d, result, scenarios):
    P, cap, s = d["products"], d["capacity"], d["settings"]
    q = result["qty"]
    lines = ["# 梅しごと工房 来月の生産計画", ""]
    lines.append(f"- 見込み利益: **{result['profit']:,.0f} 円**（発売準備の費用を引いたあと）")
    spend = sum(P[p]["material"] * q[p] for p in P) + sum(P[p]["launch_cost"] for p in result["launched"])
    lines.append(f"- 仕入れと発売準備に使うお金: {spend:,.0f} / {s['budget']:,} 円")
    lines.append("")
    lines.append("## 作る商品")
    lines.append("")
    lines.append("| 商品 | 個数 | 需要 | 1個の粗利 |")
    lines.append("|------|----:|----:|-------:|")
    for p in result["launched"]:
        unit = P[p]["price"] - P[p]["material"] - s["shipping"]
        lines.append(f"| {P[p]['label']} | {q[p]} | {P[p]['demand']} | {unit:,} 円 |")
    skipped = [P[p]["label"] for p in P if p not in result["launched"]]
    lines.append("")
    lines.append(f"出さない商品: {'、'.join(skipped)}")
    lines.append("")
    lines.append("## 資源の使い方")
    lines.append("")
    lines.append("| 資源 | 使う量 | 上限 | 使用率 |")
    lines.append("|------|------:|----:|------:|")
    for r in cap:
        used = sum(P[p][r] * q[p] for p in P)
        mark = " ★" if cap[r] - used < TOL else ""
        lines.append(f"| {d['labels'][r]} | {used:,.0f} | {cap[r]:,} | {used / cap[r]:.0%}{mark} |")
    lines.append("")
    lines.append("★ は使い切っている資源（増やせば利益が増える可能性がある）")
    lines.append("")
    lines.append("## もしも")
    lines.append("")
    lines.append("| 条件 | 見込み利益 | 差 | 作る商品 |")
    lines.append("|------|--------:|---:|---------|")
    for name, r in scenarios.items():
        diff = r["profit"] - result["profit"]
        items = "・".join(f"{P[p]['label']}{r['qty'][p]}" for p in r["launched"])
        lines.append(f"| {name} | {r['profit']:,.0f} 円 | {diff:+,.0f} | {items} |")
    return "\n".join(lines)


def scenario(d, **changes):
    """capacity や settings の一部を変えたコピーを返す"""
    d2 = copy.deepcopy(d)
    for key, value in changes.items():
        if key in d2["capacity"]:
            d2["capacity"][key] = value
        else:
            d2["settings"][key] = value
    return d2


if __name__ == "__main__":
    d = read_input(HERE / "data")
    result = solve(d)
    problems = verify(d, result)
    if problems:
        raise SystemExit("検証に失敗しました:\n" + "\n".join(problems))

    scenarios = {}
    for name, changes in {
        "梅が不作（45kg）": {"ume_g": 45000},
        "砂糖を40kgに": {"sugar_g": 40000},
        "予算を15万円に": {"budget": 150000},
        "梅80kg・砂糖50kg・予算15万円": {"ume_g": 80000, "sugar_g": 50000, "budget": 150000},
    }.items():
        d2 = scenario(d, **changes)
        r = solve(d2)
        assert not verify(d2, r)
        scenarios[name] = r

    text = report(d, result, scenarios)
    (HERE / "report.md").write_text(text, encoding="utf-8")
    print(text)
