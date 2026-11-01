import copy
import pulp

# うめ食品の新工場の計画（本書用の架空のデータ）。金額は円、数量はケース、期間は1か月
products = {
    "jam":      {"label": "ジャム",       "margin": 1500, "demand": 1200, "kettle": 1.0},
    "syrup":    {"label": "シロップ",     "margin": 1200, "demand": 1000, "kettle": 1.0},
    "dressing": {"label": "ドレッシング", "margin": 900,  "demand": 1500, "kettle": 0.5},
}
# 釜の大きさの選択肢：固定費（円/月）と能力（釜を使う量/月）
kettles = {
    "small":  {"label": "小型釜", "fixed": 500_000,   "capacity": 1200},
    "medium": {"label": "中型釜", "fixed": 900_000,   "capacity": 2000},
    "large":  {"label": "大型釜", "fixed": 1_900_000, "capacity": 3000},
}
SETUP = 150_000           # 商品を作るなら、月に1回の段取り費
MIN_LOT = 200             # 商品を作るなら、最低200ケース
LABEL_HAND = 400          # 手作業のラベル貼り（円/ケース）
LABEL_AUTO = 100          # 自動ラベラーのラベル貼り（円/ケース）
AUTO_FIXED = 300_000      # 自動ラベラーのリース料（円/月）


def solve_plant(products, kettles, big_m=None, relax=False):
    prob = pulp.LpProblem("plant", pulp.LpMaximize)
    cat = "Continuous" if relax else "Binary"

    make = {p: prob.add_variable(f"make_{p}", lowBound=0, upBound=d["demand"]) for p, d in products.items()}
    run = {p: prob.add_variable(f"run_{p}", lowBound=0, upBound=1, cat=cat) for p in products}       # 作るか
    size = {k: prob.add_variable(f"size_{k}", lowBound=0, upBound=1, cat=cat) for k in kettles}      # どの釜か
    auto = prob.add_variable("auto", lowBound=0, upBound=1, cat=cat)                                 # 自動ラベラーを入れるか
    by_auto = {p: prob.add_variable(f"by_auto_{p}", lowBound=0) for p in products}                   # 自動でラベルを貼る量

    margin = pulp.lpSum(products[p]["margin"] * make[p] for p in products)
    label = pulp.lpSum(LABEL_HAND * (make[p] - by_auto[p]) + LABEL_AUTO * by_auto[p] for p in products)
    fixed = (SETUP * pulp.lpSum(run.values())
             + pulp.lpSum(kettles[k]["fixed"] * size[k] for k in kettles)
             + AUTO_FIXED * auto)
    prob += margin - label - fixed, "profit"

    # 釜はちょうど1つ選ぶ
    prob += pulp.lpSum(size.values()) == 1, "one_kettle"
    # 釜の能力は、選んだ釜の能力まで
    prob += (pulp.lpSum(products[p]["kettle"] * make[p] for p in products)
             <= pulp.lpSum(kettles[k]["capacity"] * size[k] for k in kettles)), "kettle_capacity"

    for p, d in products.items():
        m = d["demand"] if big_m is None else big_m
        prob += make[p] <= m * run[p], f"run_max_{p}"          # 作らないなら 0
        prob += make[p] >= MIN_LOT * run[p], f"run_min_{p}"    # 作るなら最低ロット以上
        prob += by_auto[p] <= make[p], f"by_auto_le_make_{p}"
    m = sum(d["demand"] for d in products.values()) if big_m is None else big_m
    prob += pulp.lpSum(by_auto.values()) <= m * auto, "auto_link"   # 入れないなら自動では貼れない

    stats = prob.solve(pulp.HiGHS(msg=False))
    return {
        "status": stats.status_str,
        "profit": pulp.value(prob.objective),
        "make": {p: make[p].value() for p in products},
        "run": {p: run[p].value() for p in products},
        "size": {k: size[k].value() for k in kettles},
        "auto": auto.value(),
        "fixed": pulp.value(fixed),
    }


def show(title, r, products, kettles):
    print(f"■ {title}: {r['status']}  利益 {r['profit']:,.0f} 円（固定費 {r['fixed']:,.0f} 円）")
    print("  釜: " + " / ".join(f"{kettles[k]['label']} {v:.2f}" for k, v in r["size"].items()))
    print("  生産: " + " / ".join(f"{products[p]['label']} {r['make'][p]:,.0f}（run={r['run'][p]:.2f}）" for p in products))
    print(f"  自動ラベラー: {r['auto']:.2f}")


if __name__ == "__main__":
    show("基本", solve_plant(products, kettles), products, kettles)

    cheaper = copy.deepcopy(kettles)
    cheaper["large"]["fixed"] = 1_800_000
    show("大型釜が月180万円なら", solve_plant(products, cheaper), products, cheaper)
