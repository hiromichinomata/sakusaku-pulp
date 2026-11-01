# 付録H　さらに学ぶための公式ドキュメント・参考資料

本書の内容をさらに深めるための資料です。URLは2026年10月時点のものです。

---

## H.1　PuLP

| 資料 | URL | 内容 |
|------|-----|------|
| PuLP 公式ドキュメント | https://coin-or.github.io/pulp/ | 使い方・API・例題。2026年10月時点で 4.0.1 版 |
| PuLP のソースコード | https://github.com/coin-or/pulp | 最新の変更、不具合の報告（Issues） |
| PyPI の PuLP | https://pypi.org/project/PuLP/ | バージョンの履歴、extra の一覧 |

⚠️ PuLP 4 は大きく作り直された版です。ドキュメントやインターネットの記事が 3.x 以前の書き方のことがあります。迷ったら、インストールした PuLP のソースコード（`pulp/core/` フォルダ）を直接読むのが確実です（付録E）。

---

## H.2　ソルバー

| ソルバー | URL | 内容 |
|---------|-----|------|
| HiGHS | https://highs.dev/ | 公式サイト。オプションの一覧、論文 |
| CBC | https://github.com/coin-or/Cbc | ソースコードと説明（EPL-2.0） |
| GLPK | https://www.gnu.org/software/glpk/ | GNU の公式ページ |
| SCIP | https://www.scipopt.org/ | SCIP Optimization Suite の公式サイト（8.0.3 以降 Apache 2.0） |
| PySCIPOpt | https://github.com/scipopt/PySCIPOpt | Python から SCIP を使うライブラリ |
| ソルバーのベンチマーク | https://plato.asu.edu/bench.html | Hans Mittelmann によるソルバーの比較 |

第19章で話したとおり、ベンチマークは目安です。自分の問題では、実際に測って比べましょう。

---

## H.3　Python のライブラリ

| ライブラリ | URL | 本書で使った章 |
|----------|-----|-----------|
| pandas | https://pandas.pydata.org/docs/ | 第17〜22章 |
| openpyxl | https://openpyxl.readthedocs.io/ | 第17章 |
| pytest | https://docs.pytest.org/ | 第20章 |
| tomllib（標準ライブラリ） | https://docs.python.org/3/library/tomllib.html | 第20章 |
| logging（標準ライブラリ） | https://docs.python.org/3/library/logging.html | 第20章 |
| itertools（標準ライブラリ） | https://docs.python.org/3/library/itertools.html | 第1・7・13章 |

---

## H.4　次に学ぶテーマ

本書で扱わなかった、次の一歩になるテーマです。

| テーマ | 内容 | 関係する章 |
|-------|------|----------|
| 単体法・内点法の仕組み | 線形計画問題をソルバーがどう解くか | 第3章 one more thing |
| 双対理論 | 双対価格の背景にある理論 | 第18章 |
| 切除平面法・分枝カット法 | 整数計画問題を速く解く技術 | 第12章 |
| ネットワークフロー | 最短経路・最大流・最小費用流 | 第10章 |
| 制約プログラミング | 複雑なスケジュールなどを、論理的な制約で解く方法 | 第15・22章 |
| ロバスト最適化・確率計画法 | 不確かさを正面から扱う最適化 | 第23章 one more thing |
| 多目的最適化 | 複数の目的のパレートフロントを求める | 第18・22章 |
| メタヒューリスティクス | 遺伝的アルゴリズムなど、最適の保証はないが大きな問題を解く方法 | 第1・12章 |

**関連するほかのライブラリ**

| ライブラリ | 特徴 |
|----------|------|
| OR-Tools（Google） | 線形計画・整数計画に加えて、制約プログラミング（CP-SAT）や経路問題も扱える。PuLP 4 にも `pulp[ortools]` がある |
| Pyomo | 非線形の問題も扱える、本格的なモデリング言語 |
| CVXPY | 凸最適化を、数式に近い書き方で扱える |
| SciPy（`scipy.optimize`） | 小さな線形計画問題（`linprog`、HiGHS を使用）や、割り当て問題（`linear_sum_assignment`）を手軽に解ける |

---

## H.5　本書の読み方の振り返り

| 目的 | 読み直す章 |
|------|----------|
| モデルの作り方を思い出したい | 第3・4・5章 |
| 答えがおかしいとき | 第6・7章、付録C |
| 「選ぶ・選ばない」を書きたい | 第12〜14章、付録A の A.7 |
| 時間の軸がある問題 | 第15・18・22・23章 |
| 実務のプログラムにしたい | 第17〜20章 |
| ソルバーで迷ったら | 第19章、付録D |
| 古い記事のコードを動かしたい | 付録E |
