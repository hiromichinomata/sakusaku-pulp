"""入力：CSV を読み、検証し、モデル用の辞書にする"""
from pathlib import Path

import pandas as pd

FILES = {
    "products": ["product", "label", "price", "material", "demand", "min"],
    "lines": ["line", "label", "cost_per_h", "hours"],
    "line_time": ["product", "line", "hours"],
    "resources": ["resource", "label", "capacity"],
    "usage": ["product", "resource", "amount"],
}


class DataError(Exception):
    """入力データに問題があるときに投げる例外"""


def load_data(folder: Path) -> dict:
    return {name: pd.read_csv(Path(folder) / f"{name}.csv") for name in FILES}


def validate(data: dict) -> list[str]:
    problems = []
    for name, cols in FILES.items():
        df = data[name]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            problems.append(f"{name}.csv: 列がない {missing}")
            continue
        blank = df[df[cols].isna().any(axis=1)].index + 2
        if len(blank):
            problems.append(f"{name}.csv: 空欄がある（{blank.tolist()} 行目）")
        numeric = df[cols].select_dtypes("number")
        negative = df[(numeric < 0).any(axis=1)].index + 2
        if len(negative):
            problems.append(f"{name}.csv: マイナスの値がある（{negative.tolist()} 行目）")
    if problems:
        return problems

    products = set(data["products"]["product"])
    lines = set(data["lines"]["line"])
    resources = set(data["resources"]["resource"])
    for key, df in [("product", data["products"]), ("line", data["lines"]), ("resource", data["resources"])]:
        dup = df[df[key].duplicated()][key].tolist()
        if dup:
            problems.append(f"{key} が重複している: {dup}")
    for p in set(data["line_time"]["product"]) - products:
        problems.append(f"line_time.csv: 知らない商品 '{p}'")
    for l in set(data["line_time"]["line"]) - lines:
        problems.append(f"line_time.csv: 知らないライン '{l}'")
    for p in set(data["usage"]["product"]) - products:
        problems.append(f"usage.csv: 知らない商品 '{p}'")
    for r in set(data["usage"]["resource"]) - resources:
        problems.append(f"usage.csv: 知らない資源 '{r}'")
    for p in products - set(data["line_time"]["product"]):
        problems.append(f"商品 '{p}' を作れるラインがない")
    bad = data["products"][data["products"]["min"] > data["products"]["demand"]]
    for p in bad["product"]:
        problems.append(f"商品 '{p}' の最低生産数が需要より大きい")
    return problems


def to_dicts(data: dict) -> dict:
    return {
        "products": data["products"].set_index("product").to_dict("index"),
        "lines": data["lines"].set_index("line").to_dict("index"),
        "line_time": data["line_time"].set_index(["product", "line"])["hours"].to_dict(),
        "capacity": data["resources"].set_index("resource")["capacity"].to_dict(),
        "usage": data["usage"].set_index(["product", "resource"])["amount"].to_dict(),
    }


def read_input(folder: Path) -> dict:
    """読み込み → 検証 → 辞書。問題があれば DataError"""
    data = load_data(folder)
    problems = validate(data)
    if problems:
        raise DataError("\n".join(problems))
    return to_dicts(data)
