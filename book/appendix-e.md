# 付録E　PuLPのバージョン変更と互換性

本書は **PuLP 4.0.1** を前提にしています。インターネット上の記事や書籍の多くは PuLP 2.x〜3.x の書き方で書かれているため、そのまま写すと動きません。この付録では、本書で実際に確かめた違いをまとめます。

---

## E.1　大きな変化

| 項目 | PuLP 3.x まで | PuLP 4.0.1 |
|------|-------------|-----------|
| 必要な Python | 3.x の幅広い版 | **3.12 以上** |
| ソルバー | CBC が同梱され、何もしなくても使えた | 同梱されない。`pulp[highs]` などで選んで入れる |
| 変数の作り方 | `pulp.LpVariable(...)` で単独に作る | `prob.add_variable(...)` で **問題から** 作る |
| `solve()` の戻り値 | 状態を表す整数 | `LpSolveStats`（状態・目的関数値・時間などをまとめたもの） |
| 状態の文字列 | `pulp.LpStatus[prob.status]` | `stats.status_str` |
| 制約の一覧 | `prob.constraints`（辞書） | `prob.constraints()`（メソッド、リスト） |
| 制約の右辺の変更 | `changeRHS` などで変えられた | 変えられない（`NotImplementedError`） |
| 内部の実装 | Python | 中心部分が Rust（`pulp._rustcore`） |

---

## E.2　書き換え対応表

| やりたいこと | PuLP 3.x まで | PuLP 4.0.1 |
|-----------|-------------|-----------|
| 変数を作る | `x = pulp.LpVariable("x", lowBound=0, cat="Integer")` | `x = prob.add_variable("x", lowBound=0, cat="Integer")` |
| 変数の辞書 | `x = pulp.LpVariable.dicts("x", items, lowBound=0)` | `x = prob.add_variable_dict("x", items, lowBound=0)` |
| 2段の辞書 | `pulp.LpVariable.dicts("x", (A, B), ...)` | `prob.add_variable_dicts("x", (A, B), ...)` |
| CBC で解く | `prob.solve(pulp.PULP_CBC_CMD(msg=False))` | `prob.solve(pulp.COIN_CMD(msg=False))`（`pulp[cbc]` が必要） |
| 既定のソルバーで解く | `prob.solve()` | ソルバーを明示する（`prob.solve(pulp.HiGHS(msg=False))`） |
| 状態を表示 | `pulp.LpStatus[prob.status]` | `stats.status_str` |
| 状態を比べる | `prob.status == pulp.LpStatusOptimal` | `stats.status == pulp.LpSolveStatus.Optimal` |
| 名前で制約を取り出す | `prob.constraints["c1"]` | `prob.get_constraint_by_name("c1")` |
| 制約を全部見る | `prob.constraints.items()` | `prob.constraints()` |
| 右辺を変える | `prob.constraints["c1"].changeRHS(10)` | データを変えてモデルを作り直す（第5章） |
| ソルバーが動くか試す | `pulp.pulpTestAll()` | 小さな問題を解いて確かめる（第2章） |

`prob` は `pulp.LpProblem(...)` で作った問題、`stats` は `prob.solve(...)` の戻り値です。

---

## E.3　変わらないもの

次の書き方は、PuLP 4.0.1 でもそのまま使えます。

| 書き方 | 意味 |
|--------|------|
| `pulp.LpProblem("名前", pulp.LpMaximize)` | 問題を作る |
| `prob += 式, "名前"` | 目的関数・制約条件を足す |
| `pulp.lpSum(...)`、`pulp.lpDot(...)` | 式の合計・内積 |
| `pulp.value(prob.objective)`、`prob.objective.value()` | 目的関数の値 |
| `x.value()`、`x.varValue` | 変数の値 |
| `prob.variables()`、`prob.variablesDict()` | 変数の一覧 |
| `prob.writeLP(...)`、`prob.writeMPS(...)` | ファイルへの書き出し |
| `pulp.LpContinuous`、`pulp.LpInteger`、`pulp.LpBinary` | 変数の型（文字列 `"Continuous"` などと同じ） |
| `制約.slack`、`制約.pi`、`変数.dj` | 余り・双対価格・被約費用 |

---

## E.4　4.0.1 で気をつけること

PuLP 4.0.1 で特に気をつけたい点です。

| 注意点 | 内容 | 章 |
|-------|------|----|
| `pip install pulp` だけでは import できない | numpy が必要。`pulp[highs]` で入れる | 第2章 |
| `prob.solve()` が `No solver available` | HiGHS だけの環境では、既定のソルバーとして選ばれない | 第2章 |
| `numpy.int64` との比較が `TypeError` | `式 <= numpy.int64(3)` が動かない。`numpy.float64` や掛け算は動く | 第17章 |
| `式 -= ...` がその場で書き換わる | `obj = cost; obj -= ...` で `cost` も変わる | 第15章 |
| 名前の重複が黙って通る | `writeLP` や `checkDuplicateVars()` で初めて分かる | 第5章 |
| 整数を含むモデルの `pi` は0 | 双対価格は連続変数のモデルでだけ使う | 第18章 |

---

## E.5　古い記事のコードを動かすには

1. `pulp.LpVariable(...)` を探して、`prob.add_variable(...)` に書き換える（問題を先に作っておく）
2. `pulp.LpVariable.dicts(...)` を `prob.add_variable_dict(...)` か辞書内包表記に書き換える
3. `prob.solve()` に `pulp.HiGHS(msg=False)` を渡す
4. `pulp.LpStatus[prob.status]` を、`solve()` の戻り値の `.status_str` に書き換える
5. `prob.constraints[...]` を `prob.get_constraint_by_name(...)` に書き換える
6. 右辺を書き換えている部分は、データを変えてモデルを作り直す形にする

⚠️ PuLP 4 系は大きく作り直されたばかりの版です。今後の更新で、本書の内容と違う動きになる可能性があります。困ったときは、公式ドキュメント（付録H）と、インストールした PuLP のソースコード（`pulp/core/` フォルダ）を確かめてください。
