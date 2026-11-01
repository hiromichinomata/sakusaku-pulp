import itertools
from ch13_invest import candidates, BUDGET

names = list(candidates)
best_value, best_pick, checked = -1, None, 0
for picks in itertools.product([0, 1], repeat=len(names)):
    checked += 1
    chosen = [n for n, p in zip(names, picks) if p]
    groups = [candidates[n]["group"] for n in chosen]
    if (sum(candidates[n]["cost"] for n in chosen) <= BUDGET
            and groups.count("promo") <= 1
            and len(chosen) <= 4
            and "hygiene" in chosen
            and groups.count("people") >= 1):
        value = sum(candidates[n]["value"] for n in chosen)
        if value > best_value:
            best_value, best_pick = value, chosen

print("調べた組み合わせ:", checked)
print("最良:", best_value, [candidates[n]["label"] for n in best_pick])
