from pathlib import Path

import pandas as pd
import pulp

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "output"


# ---- 1. 読み込み ----
def load_data(folder):
    return {
        "products": pd.read_csv(folder / "products.csv"),
        "lines": pd.read_csv(folder / "lines.csv"),
        "line_time": pd.read_csv(folder / "line_time.csv"),
        "resources": pd.read_csv(folder / "resources.csv"),
        "usage": pd.read_csv(folder / "usage.csv"),
    }


# ---- 2. 検証 ----
def validate(data):
    problems = []
    required = {
        "products": ["product", "label", "price", "material", "demand", "min"],
        "lines": ["line", "label", "cost_per_h", "hours"],
        "line_time": ["product", "line", "hours"],
        "resources": ["resource", "label", "capacity"],
        "usage": ["product", "resource", "amount"],
    }
    for name, cols in required.items():
        df = data[name]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            problems.append(f"{name}.csv: 列がない {missing}")
            continue
        # CSV の行番号（見出しが1行目なので、データの1件目は2行目）
        blank = df[df[cols].isna().any(axis=1)].index + 2
        if len(blank):
            problems.append(f"{name}.csv: 空欄がある（{blank.tolist()} 行目）")
        numeric = df[cols].select_dtypes("number")
        negative = df[(numeric < 0).any(axis=1)].index + 2
        if len(negative):
            problems.append(f"{name}.csv: マイナスの値がある（{negative.tolist()} 行目）")
    if problems:
        return problems   # 列や空欄の問題があると、以下の検査ができない

    products = set(data["products"]["product"])
    lines = set(data["lines"]["line"])
    resources = set(data["resources"]["resource"])
    for key, df in [("product", data["products"]), ("line", data["lines"]), ("resource", data["resources"])]:
        dup = df[df[key].duplicated()][key].tolist()
        if dup:
            problems.append(f"{key} が重複している: {dup}")
    for _, row in data["line_time"].iterrows():
        if row["product"] not in products:
            problems.append(f"line_time.csv: 知らない商品 '{row['product']}'")
        if row["line"] not in lines:
            problems.append(f"line_time.csv: 知らないライン '{row['line']}'")
    for _, row in data["usage"].iterrows():
        if row["product"] not in products:
            problems.append(f"usage.csv: 知らない商品 '{row['product']}'")
        if row["resource"] not in resources:
            problems.append(f"usage.csv: 知らない資源 '{row['resource']}'")
    for p in products - set(data["line_time"]["product"]):
        problems.append(f"商品 '{p}' を作れるラインがない")
    bad = data["products"][data["products"]["min"] > data["products"]["demand"]]
    for p in bad["product"]:
        problems.append(f"商品 '{p}' の最低生産数が需要より大きい")
    return problems


# ---- 3. モデル ----
def to_dicts(data):
    """DataFrame を、第5章までと同じ形の辞書に変換する（値は Python の int / float になる）"""
    return {
        "products": data["products"].set_index("product").to_dict("index"),
        "lines": data["lines"].set_index("line").to_dict("index"),
        "line_time": data["line_time"].set_index(["product", "line"])["hours"].to_dict(),
        "capacity": data["resources"].set_index("resource")["capacity"].to_dict(),
        "usage": data["usage"].set_index(["product", "resource"])["amount"].to_dict(),
    }


def build_model(d):
    products, lines, line_time = d["products"], d["lines"], d["line_time"]
    capacity, usage = d["capacity"], d["usage"]

    prob = pulp.LpProblem("factory_csv", pulp.LpMaximize)
    make = {(p, l): prob.add_variable(f"make_{p}_{l}", lowBound=0, cat="Integer") for (p, l) in line_time}

    def unit_profit(p, l):
        return products[p]["price"] - products[p]["material"] - line_time[p, l] * lines[l]["cost_per_h"]

    prob += pulp.lpSum(unit_profit(p, l) * make[p, l] for (p, l) in line_time), "total_profit"

    total = {p: pulp.lpSum(v for (q, l), v in make.items() if q == p) for p in products}
    for l in lines:
        prob += pulp.lpSum(line_time[p, m] * make[p, m] for (p, m) in line_time if m == l) \
            <= lines[l]["hours"], f"line_{l}"
    for r in capacity:
        prob += pulp.lpSum(usage.get((p, r), 0) * total[p] for p in products) <= capacity[r], f"res_{r}"
    for p in products:
        prob += total[p] <= products[p]["demand"], f"demand_{p}"
        prob += total[p] >= products[p]["min"], f"min_{p}"
    return prob, make, total


# ---- 4. 解いて表にする ----
def solve_to_tables(data):
    d = to_dicts(data)
    prob, make, total = build_model(d)
    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        raise RuntimeError(f"最適解が得られませんでした: {stats.status_str}")

    plan = pd.DataFrame(
        [{"product": p, "line": l, "cases": round(v.value())} for (p, l), v in make.items()]
    )
    plan = plan[plan["cases"] > 0].reset_index(drop=True)

    products = data["products"].set_index("product")
    summary = products[["label", "demand", "min"]].copy()
    summary["cases"] = [round(pulp.value(total[p])) for p in summary.index]

    res = data["resources"].set_index("resource").copy()
    res["used"] = [sum(d["usage"].get((p, r), 0) * summary.at[p, "cases"] for p in summary.index) for r in res.index]
    res["rate"] = res["used"] / res["capacity"]

    return pulp.value(prob.objective), plan, summary.reset_index(), res.reset_index()


if __name__ == "__main__":
    data = load_data(DATA)
    problems = validate(data)
    if problems:
        for msg in problems:
            print("-", msg)
        raise SystemExit("データに問題があるため、計算を中止しました")

    profit, plan, summary, res = solve_to_tables(data)
    print(f"利益: {profit:,.0f} 円")
    print(plan.to_string(index=False))
    print(summary.to_string(index=False))
    print(res.to_string(index=False))

    OUT.mkdir(exist_ok=True)
    plan.to_csv(OUT / "plan.csv", index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(OUT / "plan.xlsx") as writer:
        plan.to_excel(writer, sheet_name="ライン別", index=False)
        summary.to_excel(writer, sheet_name="商品別", index=False)
        res.to_excel(writer, sheet_name="資源", index=False)
    print("保存しました:", sorted(p.name for p in OUT.iterdir()))
