import pulp

# 新商品の候補（本書用の架空のデータ）。数量はケース、期間は1か月
candidates = {
    "jelly":   {"label": "梅ゼリー",       "profit": 1800, "hours": 0.50, "demand": 120},
    "tea":     {"label": "梅こんぶ茶",     "profit": 1200, "hours": 0.25, "demand": 200},
    "cider":   {"label": "梅サイダー",     "profit": 1500, "hours": 0.40, "demand": 150},
    "yokan":   {"label": "梅ようかん",     "profit": 2500, "hours": 0.90, "demand": 80},
    "candy":   {"label": "梅のど飴",       "profit": 900,  "hours": 0.15, "demand": 250},
    "sauce":   {"label": "梅だれ",         "profit": 1300, "hours": 0.35, "demand": 100},
}
LINE_HOURS = 100   # 新商品用ラインの稼働時間（1か月）
MIN_LOT = 60       # 採用した商品は、最低60ケース作る
MAX_ITEMS = 3      # 採用できるのは3商品まで（売り場の棚の数）


def solve(use_binary=True, adopt_cat="Binary"):
    prob = pulp.LpProblem("new_products", pulp.LpMaximize)

    make_cat = "Integer" if adopt_cat == "Binary" else "Continuous"
    make = {p: prob.add_variable(f"make_{p}", lowBound=0, cat=make_cat) for p in candidates}
    prob += pulp.lpSum(candidates[p]["profit"] * make[p] for p in candidates), "total_profit"
    prob += pulp.lpSum(candidates[p]["hours"] * make[p] for p in candidates) <= LINE_HOURS, "line"

    if use_binary:
        # 1 なら「その商品を採用する」
        if adopt_cat == "Binary":
            adopt = {p: prob.add_variable(f"adopt_{p}", cat="Binary") for p in candidates}
        else:
            adopt = {p: prob.add_variable(f"adopt_{p}", lowBound=0, upBound=1) for p in candidates}
        for p, c in candidates.items():
            prob += make[p] <= c["demand"] * adopt[p], f"link_max_{p}"   # 採用しないなら 0 ケース
            prob += make[p] >= MIN_LOT * adopt[p], f"link_min_{p}"       # 採用するなら最低ロット以上
        prob += pulp.lpSum(adopt.values()) <= MAX_ITEMS, "max_items"
    else:
        adopt = None
        for p, c in candidates.items():
            prob += make[p] <= c["demand"], f"demand_{p}"

    stats = prob.solve(pulp.HiGHS(msg=False))
    return stats, prob, make, adopt


def show(title, stats, prob, make, adopt):
    print(f"■ {title}: {stats.status_str}  利益 {pulp.value(prob.objective):,.0f} 円")
    used = sum(candidates[p]["hours"] * make[p].value() for p in candidates)
    for p, c in candidates.items():
        a = "" if adopt is None else f"  adopt={adopt[p].value():.2f}"
        if make[p].value() > 0.5 or (adopt is not None and adopt[p].value() > 1e-6):
            print(f"  {c['label']}: {make[p].value():.1f} ケース{a}")
    print(f"  ライン {used:.1f} / {LINE_HOURS} 時間")


if __name__ == "__main__":
    show("採用の判断なし", *solve(use_binary=False))
    show("採用の判断あり（バイナリ）", *solve(use_binary=True))
    show("整数の条件をすべて外す", *solve(use_binary=True, adopt_cat="Continuous"))
