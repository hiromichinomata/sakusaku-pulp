import math
import pulp

# 倉庫の候補地（本書用の架空のデータ）。位置は地図上の km、固定費は円/月、能力はケース/月
sites = {
    "A": {"label": "南港",   "x": 0,   "y": 0,  "fixed": 800_000, "capacity": 3000},
    "B": {"label": "堺東",   "x": 20,  "y": 5,  "fixed": 600_000, "capacity": 2000},
    "C": {"label": "北摂",   "x": 10,  "y": 25, "fixed": 700_000, "capacity": 2500},
    "D": {"label": "東大阪", "x": 35,  "y": 20, "fixed": 500_000, "capacity": 1500},
    "E": {"label": "尼崎",   "x": -10, "y": 15, "fixed": 650_000, "capacity": 2000},
}
# 店舗。需要はケース/月
stores = {
    "s1": {"x": 5,  "y": 2,  "demand": 600},
    "s2": {"x": 15, "y": 10, "demand": 500},
    "s3": {"x": 25, "y": 15, "demand": 700},
    "s4": {"x": 30, "y": 25, "demand": 400},
    "s5": {"x": 8,  "y": 20, "demand": 650},
    "s6": {"x": -5, "y": 10, "demand": 550},
    "s7": {"x": 12, "y": 30, "demand": 450},
    "s8": {"x": 38, "y": 12, "demand": 500},
}
RATE = 20   # 輸送費：1ケースを1km運ぶと20円


def distance(w, s):
    return math.hypot(sites[w]["x"] - stores[s]["x"], sites[w]["y"] - stores[s]["y"])


def solve_location(capacity=True, single=True, n_open=None):
    prob = pulp.LpProblem("location", pulp.LpMinimize)

    use = {w: prob.add_variable(f"use_{w}", cat="Binary") for w in sites}   # 倉庫を置くか
    serve = {                                                               # 店 s の需要のうち、倉庫 w が受け持つ割合
        (w, s): prob.add_variable(f"serve_{w}_{s}", lowBound=0, upBound=1,
                                  cat="Binary" if single else "Continuous")
        for w in sites for s in stores
    }

    fixed = pulp.lpSum(sites[w]["fixed"] * use[w] for w in sites)
    transport = pulp.lpSum(RATE * distance(w, s) * stores[s]["demand"] * serve[w, s]
                           for w in sites for s in stores)
    prob += fixed + transport, "total_cost"

    for s in stores:
        prob += pulp.lpSum(serve[w, s] for w in sites) == 1, f"assign_{s}"      # 必ずどこかが受け持つ
    for w in sites:
        for s in stores:
            prob += serve[w, s] <= use[w], f"open_{w}_{s}"                    # 置かない倉庫からは届けない
        if capacity:
            prob += (pulp.lpSum(stores[s]["demand"] * serve[w, s] for s in stores)
                     <= sites[w]["capacity"] * use[w]), f"cap_{w}"
    if n_open is not None:
        prob += pulp.lpSum(use.values()) == n_open, "n_open"

    stats = prob.solve(pulp.HiGHS(msg=False))
    if stats.status_str != "Optimal":
        return {"status": stats.status_str}
    return {
        "status": stats.status_str,
        "fixed": pulp.value(fixed),
        "transport": pulp.value(transport),
        "open": [w for w in sites if use[w].value() > 0.5],
        "serve": {s: {w: serve[w, s].value() for w in sites if serve[w, s].value() > 1e-6} for s in stores},
    }


def draw_map(result):
    """5km を1文字にした簡単な地図。大文字は置いた倉庫、小文字は置かない候補地、数字は店（受け持つ倉庫）"""
    xs = range(-10, 41, 5)
    ys = range(30, -1, -5)
    grid = {(x, y): " ." for x in xs for y in ys}

    def cell(d):
        return round(d["x"] / 5) * 5, round(d["y"] / 5) * 5   # いちばん近いマスに置く

    for w, d in sites.items():
        grid[cell(d)] = f"[{w}]" if w in result["open"] else f" {w.lower()}"
    for s, d in stores.items():
        main = max(result["serve"][s], key=result["serve"][s].get)
        grid[cell(d)] = f"{s[1]}{main}"
    for y in ys:
        print("  " + "".join(f"{grid[x, y]:>4}" for x in xs))


def show(title, r):
    print(f"■ {title}: {r['status']}")
    if r["status"] != "Optimal":
        return
    total = r["fixed"] + r["transport"]
    names = "・".join(f"{w}({sites[w]['label']})" for w in r["open"])
    print(f"  合計 {total:,.0f} 円（固定費 {r['fixed']:,.0f} 円 / 輸送費 {r['transport']:,.0f} 円）  倉庫: {names}")
    for s, part in r["serve"].items():
        if len(part) > 1:
            text = " ＋ ".join(f"{w} {v:.0%}" for w, v in part.items())
            print(f"  店{s[1]} は複数の倉庫から: {text}")
    for w in r["open"]:
        load = sum(stores[s]["demand"] * part.get(w, 0) for s, part in r["serve"].items())
        print(f"  倉庫{w}: {load:,.0f} / {sites[w]['capacity']:,} ケース")


if __name__ == "__main__":
    r = solve_location(capacity=False)
    show("1: 能力を考えない", r)
    r = solve_location(capacity=True)
    show("2: 能力を考える（1店舗は1倉庫から）", r)
    draw_map(r)
    show("3: 能力を考える（1店舗を複数の倉庫から）", solve_location(capacity=True, single=False))
