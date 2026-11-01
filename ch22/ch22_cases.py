import copy
from pathlib import Path

from ch22_crew import read_input, check_days, solve_crew

d = read_input(Path(__file__).parent / "data")
d["unavailable"].discard(("hayashi", "sat"))
d["unavailable"].add(("hayashi", "fri"))


def mori_off(d):
    """森さんが1週間お休み"""
    for day in d["days"]:
        d["unavailable"].add(("mori", day))
    d["staff"]["mori"]["fair"] = 0   # 休みの人は公平さの比較に入れない
    return d


def hatsuka_sat(d):
    """店主の初花が、土曜だけ仕込みか店番に入る（人件費は0円として計算）"""
    d["staff"]["hatsuka"] = {"label": "初花", "wage": 0, "max_days": 1,
                          "prep": 1, "ship": 0, "shop": 1, "fair": 0}   # 店主は公平さの比較に入れない
    for day in d["days"]:
        if day != "sat":
            d["unavailable"].add(("hatsuka", day))
    return d


def wed_sale(d):
    """水曜にセールをして、発送が2人必要"""
    d["need"]["wed", "ship"] = 2
    return d


def shop3(d):
    """土曜のマルシェが大きくなり、店番が3人必要"""
    d["need"]["sat", "shop"] = 3
    return d


CASES = [
    ("いつもの週", []),
    ("水曜セール", [wed_sale]),
    ("森さんが休み", [mori_off]),
    ("森さんが休み＋初花が土曜に入る", [mori_off, hatsuka_sat]),
    ("土曜の店番3人＋初花が土曜に入る", [shop3, hatsuka_sat]),
]

if __name__ == "__main__":
    print("| 条件 | 解く前の検査 | 状態 | 人件費 | 勤務時間の差 |")
    print("|------|-----------|------|------:|----------:|")
    for name, changes in CASES:
        d2 = copy.deepcopy(d)
        for change in changes:
            d2 = change(d2)
        problems = check_days(d2)
        r = solve_crew(d2, fair_weight=300)
        check = "; ".join(problems) or "OK"
        if r["status"] != "Optimal":
            print(f"| {name} | {check} | {r['status']} | — | — |")
        else:
            print(f"| {name} | {check} | {r['status']} | {r['cost']:,.0f} | {r['gap']:.0f} |")
