# 付録A　PuLP主要APIクイックリファレンス

本書で使ったPuLPの書き方を、目的別にまとめます。すべて **PuLP 4.0.1** で動作を確認しています。PuLP 3.x 以前との違いは付録Eを参照してください。

---

## A.1　問題を作る

```python
import pulp

prob = pulp.LpProblem("名前", pulp.LpMaximize)   # 最大化
prob = pulp.LpProblem("名前", pulp.LpMinimize)   # 最小化
```

| 引数 | 意味 |
|------|------|
| 1つ目 | 問題の名前（英数字と `_`） |
| 2つ目 | `pulp.LpMaximize` または `pulp.LpMinimize` |

---

## A.2　変数を作る

変数は、問題から作ります（PuLP 4 の書き方）。

```python
x = prob.add_variable("x", lowBound=0, upBound=10, cat="Integer")
```

| 引数 | 省略時 | 指定できる値 |
|------|-------|-----------|
| `name` | （必須） | 英小文字・数字・`_` を推奨 |
| `lowBound` | 下限なし | 数値、`None` |
| `upBound` | 上限なし | 数値、`None` |
| `cat` | `"Continuous"` | `"Continuous"`・`"Integer"`・`"Binary"` |

まとめて作る書き方:

```python
# 辞書内包表記（商品ごとに上下限を変えられる）。本書の基本
make = {p: prob.add_variable(f"make_{p}", lowBound=0, cat="Integer") for p in products}

# 全部同じ上下限なら
make = prob.add_variable_dict("make", products, lowBound=0, cat="Integer")
# → {'jam': make_jam, ...}

# 2段の辞書
ship = prob.add_variable_dicts("ship", (warehouses, stores), lowBound=0)
# → {'w1': {'s1': ship_w1_s1, ...}, ...}
```

作った後で上下限を変えることもできます。

```python
x.upBound = 30
```

---

## A.3　式・目的関数・制約条件

```python
total = pulp.lpSum(profit[p] * make[p] for p in products)   # 足し算の式

prob += total, "total_profit"                     # 比較のない式 → 目的関数
prob += pulp.lpSum(...) <= 100, "cap_name"        # 比較のある式 → 制約条件
prob += x >= 5, "min_x"
prob += x + y == 10, "balance"
```

| 書き方 | 意味 | 章 |
|--------|------|----|
| `pulp.lpSum(式 for ...)` | 式の合計 | 第1章 |
| `数 * 変数`、`変数 / 数` | 係数を掛ける・割る | 第3章 |
| `<=`・`>=`・`==` | 制約条件（`<`・`>` は使えない） | 第3・7章 |
| `prob += 式, "名前"` | 目的関数・制約条件の追加 | 第3章 |

⚠️ 目的関数を組み立てるときは `obj = obj - 式` と書きます。`obj -= 式` は元の式をその場で書き換えます（第15章）。

⚠️ 右辺に pandas から取り出した `numpy.int64` を使うと `TypeError` になります。`to_dict` で Python の数にしてから使います（第17章）。

---

## A.4　解く

```python
stats = prob.solve(pulp.HiGHS(msg=False))
```

ソルバーは必ず明示します。引数なしの `prob.solve()` は、HiGHS だけの環境では `PulpError: No solver available` になります（第2章）。

| ソルバー | 書き方 | 入れ方 |
|---------|-------|-------|
| HiGHS | `pulp.HiGHS(...)` | `pip install "pulp[highs]"` |
| CBC | `pulp.COIN_CMD(...)` | `pip install "pulp[cbc]"` |
| GLPK | `pulp.PYGLPK(...)` | `pip install "pulp[glpk]"` |
| SCIP | `pulp.SCIP_PY(...)` | `pip install "pulp[scip]"` |

| 共通のオプション | 意味 |
|--------------|------|
| `msg=True` | ログを表示する |
| `timeLimit=60` | 時間制限（秒） |
| `gapRel=0.001` | 許容する相対ギャップ |
| `gapAbs=10` | 許容する絶対ギャップ |

```python
pulp.listSolvers(onlyAvailable=True)   # 使えるソルバーの一覧
pulp.HiGHS().available()               # そのソルバーが使えるか
```

---

## A.5　結果を読む

| 書き方 | 返すもの | 章 |
|--------|---------|----|
| `stats.status_str` | `"Optimal"`・`"Infeasible"`・`"Unbounded"`・`"Undefined"`・`"TimeLimit"` など | 第2・6章 |
| `stats.has_solution` | 使える解があるか | 第19章 |
| `stats.objective` | 目的関数の値 | 第6章 |
| `stats.best_bound` | 上限（最小化なら下限）。HiGHS のみ | 第19章 |
| `stats.time` | 計算時間（秒） | 第2章 |
| `print(stats)` | 要約 | 第2章 |
| `stats.toJson("file.json")` | 実行の記録を保存 | 第2・18章 |
| `pulp.value(prob.objective)` | 目的関数の値 | 第1章 |
| `x.value()` | 変数の値 | 第1章 |
| `pulp.value(式)` | 式に解を代入した値 | 第3章 |
| `prob.constraints()` | 制約のリスト | 第18章 |
| `prob.get_constraint_by_name("名前")` | 名前で制約を取り出す | 第5章 |
| `制約.slack` | 余り | 第18章 |
| `制約.pi` | 双対価格（連続変数のモデルのみ意味がある） | 第18章 |
| `変数.dj` | 被約費用 | 第18章 |

⚠️ 整数変数の値は `round(x.value())` で整数にします。`int()` は切り捨てなので使いません（第6章）。

---

## A.6　モデルを確かめる・保存する

| 書き方 | 用途 | 章 |
|--------|------|----|
| `print(prob)` | モデルの中身を表示 | 第2章 |
| `prob.writeLP("model.lp")` | LP形式で保存（人が読む） | 第7章 |
| `prob.writeMPS("model.mps")` | MPS形式で保存（機械向け） | 第19章 |
| `pulp.LpProblem.fromMPS("model.mps", sense=pulp.LpMaximize)` | MPSから読み込む。`(変数の辞書, 問題)` を返す | 第19章 |
| `prob.numVariables()` / `prob.numConstraints()` | 変数・制約の数 | 第20章 |
| `prob.checkDuplicateVars()` | 変数名の重複を検査 | 第5章 |
| `prob.checkDuplicateConstraints()` | 制約名の重複を検査 | 第5章 |

---

## A.7　よく使う形（パターン集）

| やりたいこと | 書き方 | 章 |
|-----------|-------|----|
| 作れない組み合わせを禁止 | その変数を作らない | 第9・11・16章 |
| ちょうど1つ選ぶ | `pulp.lpSum(y.values()) == 1` | 第11・14章 |
| k 個まで選ぶ | `pulp.lpSum(y.values()) <= k` | 第13章 |
| A を選ぶなら B も | `y_A <= y_B` | 第13・16章 |
| A と B は同時に選ばない | `y_A + y_B <= 1` | 第13・15章 |
| 選ばないなら0、選ぶなら最低量以上 | `x <= M * y` と `x >= 最低量 * y` | 第12・14章 |
| 固定費 | 目的関数に `固定費 * y` | 第14章 |
| 割合の上限 | `A <= r * 全体`（分母を掛ける） | 第8章 |
| いちばん大きい値を最小化 | `値[i] <= z` として `z` を最小化 | 第11・15章 |
| 量の刻み | `x = 刻み * 整数変数` | 第8章 |
| 不足を許して罰金 | `入る量 + 不足 == 需要` と目的関数に `罰金 * 不足` | 第10章 |
| 期間をまたぐ在庫 | `先期在庫 + 生産 - 販売 == 今期在庫` | 第18章 |
| 通過点の流れ | `入る量 == 出る量` | 第10章 |
| 連続 k 日の上限 | 窓をずらしながら `Σ（k 日分） <= 上限` | 第15章 |
| 2段階の目的 | 1段目の最適値を制約に固定して、2段目を解く | 第6・11章 |
