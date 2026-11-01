import pulp

print("PuLP:", pulp.__version__)
print("使えるソルバー:", pulp.listSolvers(onlyAvailable=True))

prob = pulp.LpProblem("hello", pulp.LpMaximize)
x = prob.add_variable("x", lowBound=0, upBound=3)

prob += x, "objective"

stats = prob.solve(pulp.HiGHS(msg=False))
print("状態:", stats.status_str)
print("x =", x.value())
