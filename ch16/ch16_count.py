from ch16_location import solve_location, sites

print("| 倉庫の数 | 状態 | 固定費 | 輸送費 | 合計 | 置く倉庫 |")
print("|-------:|------|------:|------:|-----:|---------|")
for n in [1, 2, 3, 4]:
    r = solve_location(capacity=True, n_open=n)
    if r["status"] != "Optimal":
        print(f"| {n} | {r['status']} | — | — | — | — |")
        continue
    print(f"| {n} | {r['status']} | {r['fixed']:,.0f} | {r['transport']:,.0f} | "
          f"{r['fixed'] + r['transport']:,.0f} | {'・'.join(r['open'])} |")
