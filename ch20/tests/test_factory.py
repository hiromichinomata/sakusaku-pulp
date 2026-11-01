import copy
import itertools
from pathlib import Path

import pytest

from factory_opt.data_io import DataError, load_data, read_input, validate
from factory_opt.model import build_model, unit_profit
from factory_opt.solve import SolveError, solve
from factory_opt.verify import verify

DATA = Path(__file__).parent.parent / "data"
CFG = {"name": "HiGHS", "msg": False, "time_limit": 60}

# 手で確かめられるくらい小さなデータ
SMALL = {
    "products": {
        "a": {"label": "A", "price": 100, "material": 40, "demand": 5, "min": 0},
        "b": {"label": "B", "price": 120, "material": 50, "demand": 4, "min": 1},
    },
    "lines": {"L": {"label": "ライン", "cost_per_h": 10, "hours": 6}},
    "line_time": {("a", "L"): 1.0, ("b", "L"): 1.5},
    "capacity": {"r": 10},
    "usage": {("a", "r"): 2, ("b", "r"): 1},
}


def brute_force(d):
    keys = list(d["line_time"])
    best = None
    for counts in itertools.product(range(11), repeat=len(keys)):
        make = dict(zip(keys, counts))
        if not verify(d, make):   # 検証で問題がなければ、条件を満たす案
            profit = sum(unit_profit(d, p, l) * x for (p, l), x in make.items())
            best = profit if best is None else max(best, profit)
    return best


def test_base_data_gives_known_profit():
    """いつものデータで、いつもの答え（第9章・第17章）が出る"""
    d = read_input(DATA)
    prob, make = build_model(d)
    result = solve(prob, make, CFG)
    assert result["status"] == "Optimal"
    assert result["profit"] == pytest.approx(470300)
    assert verify(d, result["make"]) == []


def test_small_data_matches_brute_force():
    """小さなデータでは、全探索と同じ答えになる（第7章）"""
    prob, make = build_model(SMALL)
    result = solve(prob, make, CFG)
    assert result["profit"] == pytest.approx(brute_force(SMALL))


def test_validate_finds_unknown_product():
    data = load_data(DATA)
    data["usage"].loc[len(data["usage"])] = ["dresing", "ume_kg", 2]
    assert "usage.csv: 知らない商品 'dresing'" in validate(data)


def test_read_input_raises_on_bad_data(tmp_path):
    data = load_data(DATA)
    data["products"].loc[1, "material"] = None
    for name, df in data.items():
        df.to_csv(tmp_path / f"{name}.csv", index=False)
    with pytest.raises(DataError, match="空欄"):
        read_input(tmp_path)


def test_impossible_minimum_raises():
    """最低生産数がラインの能力を超えると、解がないことを例外で知らせる"""
    d = copy.deepcopy(SMALL)
    d["products"]["b"]["min"] = 4
    d["products"]["a"]["min"] = 5
    prob, make = build_model(d)
    with pytest.raises(SolveError):
        solve(prob, make, CFG)


def test_verify_catches_overuse():
    bad = {("a", "L"): 5, ("b", "L"): 2}   # ライン 5 + 3 = 8 時間 > 6 時間
    assert any("ライン L" in msg for msg in verify(SMALL, bad))

