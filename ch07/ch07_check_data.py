from ch07_fixed import products, resources


def check_data(products, resources):
    """データの書き間違いを探す（モデルを作る前に実行する）"""
    problems = []
    for r, info in resources.items():
        for p in info["use"]:
            if p not in products:
                problems.append(f"{r}: 商品 '{p}' は products にない")
        if info["capacity"] < 0:
            problems.append(f"{r}: 上限がマイナス ({info['capacity']})")
    for p, info in products.items():
        if info["max"] is not None and info["min"] > info["max"]:
            problems.append(f"{p}: 下限 {info['min']} が上限 {info['max']} より大きい")
        if not any(p in info["use"] for info in resources.values()):
            problems.append(f"{p}: どの資源も使っていない")
    return problems


for msg in check_data(products, resources):
    print("-", msg)
