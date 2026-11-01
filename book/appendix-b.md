# 付録B　線形計画法・整数計画法の数学用語

本文では数式をできるだけ使わずに説明しました。この付録では、教科書や論文を読むときに出てくる用語と記号を、本書の言葉と対応させて整理します。

---

## B.1　問題の一般形

本書の問題は、どれも次の形で書けます。

```text
最大化（または最小化）  c₁x₁ + c₂x₂ + … + cₙxₙ
制約条件                a₁₁x₁ + a₁₂x₂ + … + a₁ₙxₙ ≦ b₁
                        a₂₁x₁ + a₂₂x₂ + … + a₂ₙxₙ ≦ b₂
                        …
                        xⱼ ≧ 0（j = 1, …, n）
```

Σ（シグマ、合計の記号）を使うと、次のように短く書けます。

```text
最大化   Σⱼ cⱼ xⱼ
制約     Σⱼ aᵢⱼ xⱼ ≦ bᵢ   （すべての i について）
         xⱼ ≧ 0
```

| 記号 | 意味 | 本書の言葉 | PuLP |
|------|------|----------|------|
| xⱼ | j 番目の変数 | 意思決定変数 | `prob.add_variable(...)` |
| cⱼ | 目的関数の係数 | 1個あたりの利益・費用 | `profit[p]` |
| aᵢⱼ | 制約 i の、変数 j の係数 | 1個あたりの使用量 | `use[r][p]` |
| bᵢ | 制約 i の右辺 | 上限・下限 | `capacity[r]` |
| Σⱼ | j について合計 | `for p in products` の合計 | `pulp.lpSum(... for p in products)` |
| ∀i | すべての i について | 資源ごとに制約を作る | `for r in resources:` |

**例**：第3章の梅工房

```text
最大化   800 x_jam + 500 x_syrup
制約     0.6 x_jam + 0.5 x_syrup ≦ 33     （梅）
         0.5 x_jam + 0.2 x_syrup ≦ 21     （作業時間）
         x_jam, x_syrup ≧ 0
```

---

## B.2　問題の種類

| 用語 | 英語 | 意味 | 章 |
|------|------|------|----|
| 線形計画問題 | Linear Programming（LP） | 目的関数も制約も線形で、変数は連続 | 第1・3章 |
| 整数計画問題 | Integer Programming（IP） | 変数が整数 | 第1・12章 |
| 混合整数計画問題 | Mixed Integer Programming（MIP、MILP） | 連続変数と整数変数が混ざる | 第12・14章 |
| 0-1整数計画問題 | Binary Integer Programming | 変数が0か1 | 第11・13章 |
| 非線形計画問題 | Nonlinear Programming（NLP） | 変数どうしの掛け算などを含む。PuLPでは直接扱えない | 第1・7章 |
| 数理最適化 | Mathematical Optimization | これらをまとめた呼び方 | — |
| オペレーションズ・リサーチ | Operations Research（OR） | 最適化を含む、意思決定のための科学 | — |

---

## B.3　解に関する用語

| 用語 | 英語 | 意味 | 章 |
|------|------|------|----|
| 実行可能解 | feasible solution | すべての制約を満たす答え | 第6章 |
| 実行可能領域 | feasible region | 実行可能解の集まり。2変数なら多角形 | 第3章 |
| 最適解 | optimal solution | 実行可能解の中で目的関数が最も良いもの | 第1章 |
| 最適値 | optimal value | 最適解での目的関数の値 | 第1章 |
| 実行不可能 | infeasible | 実行可能解が1つもない | 第7章 |
| 非有界 | unbounded | 目的関数をいくらでも良くできる | 第7章 |
| 頂点 | vertex, extreme point | 実行可能領域の角。LPの最適解は頂点にある | 第3章 |
| 有効な制約 | binding / active constraint | 最適解でぴったり等号になる制約（効いている制約） | 第3・6章 |
| スラック | slack | 制約の右辺と左辺の差（余り） | 第6・18章 |

---

## B.4　解き方に関する用語

| 用語 | 英語 | 意味 | 章 |
|------|------|------|----|
| ソルバー | solver | 問題を解くプログラム | 第1・19章 |
| モデラー | modeler | 問題を書くための道具。PuLPはこれ | 第1章 |
| 単体法 | simplex method | LPを頂点から頂点へたどって解く方法 | 第3章 one more thing |
| 内点法 | interior point method | 実行可能領域の内側を通ってLPを解く方法 | — |
| 緩和問題 | relaxation | 整数の条件を外した問題 | 第12章 |
| LP緩和 | LP relaxation | 整数計画問題の整数の条件を外したLP | 第12章 |
| 分枝限定法 | branch and bound | 緩和問題を解きながら、問題を分けて枝を打ち切る方法 | 第12章 |
| 暫定解 | incumbent | これまでに見つかった最良の整数解 | 第12章 |
| 上界・下界 | upper / lower bound | 最適値がとりうる範囲の上限・下限 | 第2・12章 |
| 双対ギャップ（ギャップ） | (optimality) gap | 暫定解と上界（下界）の差 | 第2・19章 |
| 切除平面 | cutting plane | 緩和問題の答えを削って、上界を締める制約 | 第12章 |
| ヒューリスティック | heuristic | 最適とは限らないが、良い解を速く見つける方法 | 第1章（効率順に選ぶ） |
| 貪欲法 | greedy algorithm | その場で一番良く見えるものから選ぶ方法 | 第1・13章 |

---

## B.5　感度分析に関する用語

| 用語 | 英語 | 意味 | PuLP | 章 |
|------|------|------|------|----|
| 双対価格（シャドープライス） | dual value, shadow price | 制約の右辺を1増やしたときの目的関数の変化 | `制約.pi` | 第18章 |
| 被約費用 | reduced cost | 0の変数を1増やしたときの目的関数の変化 | `変数.dj` | 第18章 |
| 双対問題 | dual problem | 元の問題（主問題）と対になる問題。双対価格はその解 | — | — |
| 感度分析 | sensitivity analysis | データが変わったときの答えの変わり方を調べること | — | 第18章 |
| パレート最適 | Pareto optimal | 一方を良くすると、もう一方が必ず悪くなる状態 | — | 第18・22章 |

---

## B.6　モデリングの技法に関する用語

| 用語 | 英語 | 意味 | 章 |
|------|------|------|----|
| Big-M法 | big-M method | 大きな数 M とバイナリ変数で、条件付きの制約を書く方法 | 第12・14章 |
| 半連続変数 | semi-continuous variable | 0か、ある値以上をとる変数 | 第14章 |
| 補助変数 | auxiliary variable | 最大値などを表すために足す変数 | 第11・15章 |
| ソフト制約 | soft constraint | 破ってもよいが罰金がかかる条件 | 第10・15章 |
| ハード制約 | hard constraint | 必ず守る条件 | 第15章 |
| SOS（特殊順序集合） | Special Ordered Set | 0でない変数の数を制限する仕組み | 第14章 one more thing |
| 指示制約 | indicator constraint | バイナリ変数が1のときだけ効く制約 | 第14章 one more thing |
| ロバスト最適化 | robust optimization | 不確かさのどの場合にも耐える答えを探す | 第23章 one more thing |
| 確率計画法 | stochastic programming | 不確かさの確率を使って、平均で良い答えを探す | 第23章 one more thing |

---

## B.7　代表的な問題の名前

| 問題の名前 | 英語 | 本書の章 |
|----------|------|--------|
| 生産計画問題 | production planning | 第3・9章 |
| 配合問題（栄養問題） | blending / diet problem | 第8章 |
| 輸送問題 | transportation problem | 第10章 |
| 割り当て問題 | assignment problem | 第11章 |
| ナップサック問題 | knapsack problem | 第13章 |
| 施設配置問題 | facility location problem | 第16章 |
| 勤務スケジューリング | staff / shift scheduling | 第15・22章 |
| ロットサイズ決定問題 | lot sizing problem | 第18章（在庫つきの計画） |
