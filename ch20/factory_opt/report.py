"""出力：結果を表にして、CSV と Excel に書き出す"""
from pathlib import Path

import pandas as pd


def to_tables(d: dict, result: dict) -> dict:
    plan = pd.DataFrame([
        {"product": p, "label": d["products"][p]["label"], "line": l, "cases": round(x)}
        for (p, l), x in result["make"].items() if round(x) > 0
    ])
    total = plan.groupby("product")["cases"].sum()
    resources = pd.DataFrame([
        {"resource": r, "capacity": cap,
         "used": sum(d["usage"].get((p, r), 0) * int(total.get(p, 0)) for p in d["products"])}
        for r, cap in d["capacity"].items()
    ])
    resources["rate"] = resources["used"] / resources["capacity"]
    summary = pd.DataFrame([{
        "profit": round(result["profit"]), "status": result["status"],
        "solver": result["solver"], "seconds": round(result["seconds"], 3),
    }])
    return {"summary": summary, "plan": plan, "resources": resources}


def save(tables: dict, folder: Path) -> list[Path]:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, df in tables.items():
        path = folder / f"{name}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        paths.append(path)
    xlsx = folder / "report.xlsx"
    with pd.ExcelWriter(xlsx) as writer:
        for name, df in tables.items():
            df.to_excel(writer, sheet_name=name, index=False)
    paths.append(xlsx)
    return paths
