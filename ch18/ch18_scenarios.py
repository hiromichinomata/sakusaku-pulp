import copy
import time
from pathlib import Path

import pandas as pd
import pulp
from ch17_plan import load_data, validate, to_dicts, build_model

OUT = Path(__file__).parent / "output"


# ---- シナリオ：基本のデータ（辞書）を受け取り、変更したコピーを返す関数 ----
def base(d):
    return d


def material_up_20(d):
    """原材料費が2割上がる"""
    for p in d["products"].values():
        p["material"] = p["material"] * 1.2
    return d


def demand_down_20(d):
    """需要が2割減る（端数は切り捨て）"""
    for p in d["products"].values():
        p["demand"] = int(p["demand"] * 0.8)
    return d


def pack_50h(d):
    """包装の時間を週50時間に増やす"""
    d["capacity"]["pack_h"] = 50
    return d


def line_b_30h(d):
    """ラインBが点検で週30時間しか使えない"""
    d["lines"]["B"]["hours"] = 30
    return d


SCENARIOS = {
    "基本": base,
    "原材料費+20%": material_up_20,
    "需要-20%": demand_down_20,
    "包装50時間": pack_50h,
    "ラインB 30時間": line_b_30h,
}


def run_scenario(i, name, change, base_dicts):
    d = change(copy.deepcopy(base_dicts))   # 元のデータを壊さない
    prob, make, total = build_model(d)
    start = time.perf_counter()
    stats = prob.solve(pulp.HiGHS(msg=False))
    stats.toJson(OUT / f"stats_{i:02d}.json")   # 実行の記録（第2章）
    row = {"scenario": name, "status": stats.status_str, "seconds": round(time.perf_counter() - start, 3)}
    if stats.status_str != "Optimal":
        return row
    row["profit"] = round(pulp.value(prob.objective))
    for p in d["products"]:
        row[p] = round(pulp.value(total[p]))
    # 効いている制約（余りがほぼ0の制約）の名前
    row["binding"] = " ".join(c.name for c in prob.constraints() if c.slack is not None and abs(c.slack) < 1e-6)
    return row


if __name__ == "__main__":
    data = load_data(Path(__file__).parent / "data")
    assert not validate(data)
    base_dicts = to_dicts(data)

    OUT.mkdir(exist_ok=True)
    rows = [run_scenario(i, name, change, base_dicts) for i, (name, change) in enumerate(SCENARIOS.items())]
    table = pd.DataFrame(rows)
    table["vs_base"] = table["profit"] - table.loc[0, "profit"]

    print(table[["scenario", "status", "profit", "vs_base", "jam", "syrup", "umeboshi", "dressing"]].to_string(index=False))
    print()
    print(table[["scenario", "binding"]].to_string(index=False))

    table.to_csv(OUT / "scenarios.csv", index=False, encoding="utf-8-sig")
    print()
    print("保存しました:", sorted(p.name for p in OUT.iterdir()))
