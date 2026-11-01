from ch14_plant import products, kettles, solve_plant, show

show("Big-M ＝ 需要（整数の条件を外す）", solve_plant(products, kettles, relax=True), products, kettles)
show("Big-M ＝ 100万（整数の条件を外す）", solve_plant(products, kettles, big_m=1_000_000, relax=True), products, kettles)
show("Big-M ＝ 100万", solve_plant(products, kettles, big_m=1_000_000), products, kettles)
show("Big-M ＝ 800（小さすぎる）", solve_plant(products, kettles, big_m=800), products, kettles)
