# 付録C　よくあるエラーと解決方法

本書の題材を解く中で出会いやすいエラーと、その原因・解決方法をまとめます。環境は PuLP 4.0.1、HiGHS 1.13.1、Python 3.13、macOS 26 です。

---

## C.1　インストール・環境

| 症状 | 原因 | 解決方法 | 章 |
|------|------|---------|----|
| `pip install pulp` が失敗する、または古い版が入る | PuLP 4 は Python 3.12 以上が必要 | `python3 --version` を確かめ、3.12 以上を入れる | 第2章 |
| `import pulp` で `ModuleNotFoundError: No module named 'numpy'` | PuLP 本体だけを入れた | `pip install "pulp[highs]"` | 第2章 |
| `zsh: no matches found: pulp[highs]` | zsh が `[ ]` を特別な記号として扱う | `"pulp[highs]"` のように引用符で囲む | 第2章 |
| `pulp.listSolvers(onlyAvailable=True)` が `[]` | ソルバーが入っていない | `pip install "pulp[highs]"` など | 第2章 |
| `AttributeError: module 'pulp' has no attribute 'LpProblem'` | 自分のファイル名が `pulp.py` | ファイル名を変える（`ch02_...py` など） | 第2章 |
| `AttributeError: partially initialized module 'pulp' ... circular import` | 自分のファイル名が `inspect.py` など標準ライブラリと同じ | ファイル名を変える | 第2章 |
| CBC で `PulpSolverError: Pulp: Error while trying to execute` | macOS で CBC が `Killed: 9`。同梱ライブラリの署名が壊れている（cbcbox 2.935） | 3つの `.dylib` を `codesign --force --sign -` で署名し直す。または HiGHS を使う | 第19章 |
| `pip install` したのに `ModuleNotFoundError` | 仮想環境が有効になっていない | `source .venv/bin/activate`（Windows は `.venv\Scripts\Activate.ps1`） | 第2章 |

---

## C.2　PuLP 3.x の書き方を使ったとき

| 症状 | 原因 | PuLP 4 の書き方 |
|------|------|--------------|
| `TypeError: LpVariable.__init__() got an unexpected keyword argument 'lowBound'` | `pulp.LpVariable(...)` で変数を作った | `prob.add_variable(...)` |
| `AttributeError: type object 'LpVariable' has no attribute 'dicts'` | `pulp.LpVariable.dicts(...)` | `prob.add_variable_dict(...)` または辞書内包表記 |
| `AttributeError: module 'pulp' has no attribute 'LpStatus'` | `pulp.LpStatus[prob.status]` | `stats = prob.solve(...)` の `stats.status_str` |
| `AttributeError: 'LpProblem' object has no attribute 'status'` | `prob.status` | `stats.status` / `stats.status_str` |
| `AttributeError: module 'pulp' has no attribute 'PULP_CBC_CMD'` | CBC が同梱されなくなった | `pulp.HiGHS(...)`、CBC なら `pulp[cbc]` を入れて `pulp.COIN_CMD(...)` |
| `TypeError: 'method' object is not subscriptable` | `prob.constraints["名前"]` | `prob.get_constraint_by_name("名前")` |
| `NotImplementedError: Cannot change RHS of constraint already in model` | `changeRHS` で右辺を変えようとした | データを変えてモデルを作り直す |

詳しくは付録Eを参照してください。

---

## C.3　モデルを書くとき（実行エラー）

| 症状 | 原因 | 解決方法 | 章 |
|------|------|---------|----|
| `PulpError: No solver available` | `prob.solve()` を引数なしで呼んだ | `prob.solve(pulp.HiGHS(msg=False))` | 第2章 |
| `TypeError: Non-constant expressions cannot be multiplied` | 変数どうしの掛け算 | 線形に直す（バイナリ変数と Big-M など） | 第7・14章 |
| `TypeError: unsupported operand type(s) for ** or pow()` | 変数の二乗 | PuLP では書けない。モデルを見直す | 第7章 |
| `TypeError: unsupported operand type(s) for /: 'int' and 'LpVariable'` | 変数で割った | 両辺に分母を掛けて線形にする | 第7・8章 |
| `TypeError: '>' not supported between instances of 'LpVariable' and 'LpVariable'` | Python の `max()` を使った | 補助変数で最大値を表す | 第7・11章 |
| `TypeError: '<' not supported ...` | `<` や `>` を使った | `<=`、`>=` を使う | 第7章 |
| `TypeError: '<=' not supported between instances of 'LpAffineExpression' and 'numpy.int64'` | pandas の値をそのまま右辺に使った | `to_dict` で Python の数にする、または `int(...)` | 第17章 |
| `TypeError: A False object cannot be passed as a constraint` | `式 == numpy.int64` が `False` になった | 同上 | 第17章 |
| `KeyError` | 辞書にない組み合わせのキーを使った | `x.get(キー, 0)` を使う、または変数の作り方を見直す | 第5・15章 |
| `UserWarning: Overwriting previously set objective.` | 比較のない式を2回 `prob +=` した | 目的関数の `prob +=` は1回だけにする | 第3章 |
| `PulpError: Repeated variable names` | 同じ名前の変数を作った（`writeLP` で発覚） | 名前にキーを含める。`prob.checkDuplicateVars()` | 第5章 |

---

## C.4　解けない・答えがおかしい（エラーにならない）

| 症状 | よくある原因 | 調べ方 | 章 |
|------|-----------|-------|----|
| `Infeasible` | 制約の矛盾、単位の取り違え、データの打ち間違い、等式が厳しすぎる | 制約を1本ずつ外す。データを検査する | 第4・7章 |
| `Unbounded` | 制約の向きの間違い、制約の書き忘れ、下限の書き忘れ | LPファイルを読む | 第7章 |
| `Undefined` | 整数を含む問題で、解けないか際限がないか判別できない | `cat="Continuous"` にして解き直す | 第7章 |
| `Optimal` なのに利益が多すぎる | データのキーの打ち間違い（`get(p, 0)` で0になる）、係数の符号 | データを検査する。LPファイルを読む | 第7章 |
| `Optimal` なのに利益が少なすぎる | Big-M が小さすぎる、余計な制約 | M をデータの最大値にする | 第14章 |
| 小数の答えになる | `cat="Integer"` の書き忘れ | `print(prob)` で変数の型を確かめる | 第2章 |
| 下限が効いていない | `0 <= x <= 5` と書いた | `lowBound`・`upBound` を使うか、制約を2本に分ける | 第7章 |
| 条件分岐が効いていない | `if x >= 3:` と書いた | バイナリ変数で表す | 第7・14章 |
| 目的関数の式まで変わっている | `obj -= ...` で元の式を書き換えた | `obj = obj - ...` | 第15章 |
| 整数変数の値が `13.999999999999995` | 小数の計算の誤差 | 検証後に `round()` | 第6章 |
| `Infeasible` なのに値が0で表示される | 状態を確かめずに値を表示した | `status_str` を確かめてから値を読む | 第4・6章 |
| 制約の `pi` が全部0 | 整数を含むモデル | シナリオで解き直して比べる | 第18章 |
| 毎回、違う答えが出る | 最適解が複数ある | 2段目の目的関数で選ぶ。テストは目的関数の値で比べる | 第6・20章 |

---

## C.5　ソルバーの動き

| 症状 | 原因 | 解決方法 | 章 |
|------|------|---------|----|
| `TimeLimit` で止まる | 時間制限に達した | `has_solution` が真なら使える。ギャップを確かめる | 第19章 |
| 時間制限が効かない | GLPK（PyGLPK）では PuLP 4.0.1 で効かなかった | 別のソルバーを使う | 第19章 |
| `Optimal` なのにギャップが残っている | 許容ギャップ（HiGHS は既定0.01%）以内で止まった | 必要なら `gapRel` を小さくする | 第19章 |
| とても時間がかかる | 整数変数が多い、Big-M が大きい | 変数を減らす、M を小さく、`gapRel` を緩める、ソルバーを比べる | 第12・14・19章 |
| `stats.best_bound` が `None` | ソルバーが上限を返さない | HiGHS を使うか、`msg=True` でログを読む | 第19章 |

---

## C.6　データ・入出力

| 症状 | 原因 | 解決方法 | 章 |
|------|------|---------|----|
| CSV を Excel で開くと文字化けする | BOM がない | `to_csv(..., encoding="utf-8-sig")` | 第17章 |
| `to_excel` で `ModuleNotFoundError: openpyxl` | openpyxl が入っていない | `pip install openpyxl` | 第17章 |
| 検査で行番号がずれる | pandas の番号は0から、CSVは見出しが1行目 | `index + 2` で CSV の行番号にする | 第17章 |
| 自分のスクリプトを import すると実行結果が二重に出る | `if __name__ == "__main__":` がない | 実行部分をその中に入れる | 第6章 |
| 元のデータが変わってしまう | 辞書を直接書き換えた | `copy.deepcopy` してから変える | 第5・18章 |
