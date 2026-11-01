# 付録D　ソルバーの導入・設定早見表

本書で使った環境（PuLP 4.0.1）での情報です。バージョンが変わると、入れ方やオプションの効き方が変わることがあります。新しい環境では、第2章の `hello_pulp.py` のような小さな問題で動作を確かめてください。

---

## D.1　入れ方と使い方

| ソルバー | 入れ方 | PuLP での書き方 | 呼び出し方 | 本書での位置づけ |
|---------|-------|--------------|----------|-------------|
| HiGHS | `pip install "pulp[highs]"` | `pulp.HiGHS(msg=False)` | Python の中で直接 | **標準** |
| CBC | `pip install "pulp[cbc]"` | `pulp.COIN_CMD(msg=False)` | 別のプログラムを起動 | 比較用（第19章） |
| GLPK | `pip install "pulp[glpk]"` | `pulp.PYGLPK(msg=False)` | Python の中で直接 | 比較用（第19章） |
| SCIP | `pip install "pulp[scip]"` | `pulp.SCIP_PY(msg=False)` | Python の中で直接 | 比較用（第19章） |

まとめて入れる場合:

```bash
pip install "pulp[highs]" "pulp[cbc]" "pulp[glpk]" "pulp[scip]"
```

確認:

```python
import pulp
print(pulp.__version__)
print(pulp.listSolvers(onlyAvailable=True))
```

```text
4.0.1
['PYGLPK', 'COIN_CMD', 'SCIP_PY', 'HiGHS']
```

本書で使ったパッケージのバージョンです。

| パッケージ | バージョン |
|----------|---------|
| PuLP | 4.0.1 |
| highspy（HiGHS） | 1.13.1 |
| cbcbox（CBC） | 2.935 |
| swiglpk（GLPK） | 5.0.13 |
| PySCIPOpt（SCIP） | 6.3.0 |
| numpy | 2.5.4 |

---

## D.2　ライセンス

| ソルバー | ライセンス | 性格 |
|---------|----------|------|
| PuLP | MIT | 寛容 |
| HiGHS | MIT | 寛容 |
| CBC | EPL-2.0 | 弱いコピーレフト |
| GLPK | GPL-3.0 | 強いコピーレフト |
| SCIP | Apache-2.0（SCIP本体）、MIT（PySCIPOpt） | 寛容 |

PuLP から呼び出して使うだけなら、どれも商用・社内利用で困ることはまずありません。ソルバーを自分のソフトに組み込んで配布する場合は、ライセンス文書を確認してください（第19章 19.2）。

---

## D.3　オプション

| オプション | 意味 | HiGHS | CBC | GLPK | SCIP |
|-----------|------|:-----:|:---:|:----:|:----:|
| `msg` | ログを表示 | ○ | ○ | ○ | ○ |
| `timeLimit` | 時間制限（秒） | ○ | ○ | ×（効かなかった） | ○ |
| `gapRel` | 許容する相対ギャップ | ○ | （未確認） | （未確認） | （未確認） |
| `stats.best_bound` | 上限・下限を返す | ○ | ×（`None`） | ×（`None`） | ×（`None`） |

○ は第19章で動作を確かめたもの、× は確かめた結果、効かなかった・返らなかったものです。

---

## D.4　実測の例（第19章）

第12章のランダムな「選ぶ・選ばない」問題（資源5種類）を解いた時間（秒）です。手元の環境での例で、秒数はパソコンによって変わります。

| 候補の数 | HiGHS | CBC | GLPK | SCIP |
|-------:|------:|----:|-----:|-----:|
| 100 | 0.21 | 0.52 | 0.06 | 0.17 |
| 200 | 2.30 | 1.27 | 2.58 | 3.34 |
| 300 | 3.10 | 1.45 | 2.82 | 2.44 |

どのソルバーも同じ最適値になりました。速さの順番は問題の大きさで入れ替わります。**自分の問題で測る** ことが大切です。

---

## D.5　macOS で CBC が動かないとき

症状:

```text
pulp.apis.core.PulpSolverError: Pulp: Error while trying to execute, use msg=True for more details
```

CBC のプログラムを直接動かすと `Killed: 9` で止まります。cbcbox 2.935 に含まれる3つのライブラリの署名が壊れていることが原因でした。

```bash
python -c "import cbcbox, pathlib; print(pathlib.Path(cbcbox.__file__).parent / 'cbc_dist' / 'lib')"
cd （表示されたフォルダ）
codesign --verify libgfortran.5.dylib          # invalid signature と出れば、この問題
codesign --force --sign - libgcc_s.1.1.dylib libgfortran.5.dylib libquadmath.0.dylib
```

署名し直すのが不安な場合は、HiGHS など他のソルバーを使ってください。Windows・Linux では起きません。

この問題は cbcbox の開発元に報告されています（https://github.com/h-g-s/cbcbox/issues/2 ）。修正された版が出ていないか、先に確かめてください。

---

## D.6　商用ソルバー

PuLP 4 には、商用ソルバー用の extra も用意されています（`pulp[gurobi]`、`pulp[cplex]`、`pulp[xpress]`、`pulp[copt]`、`pulp[mosek]` など）。ライセンスの費用がかかりますが、大きな整数計画問題ではオープンソースより大幅に速いことがあります。無料の試用版や、学生・研究者向けのライセンスがある製品もあります。本書では動作を確かめていません。

---

## D.7　選び方の目安

| 状況 | 目安 |
|------|------|
| まず始める | HiGHS |
| 遅いと感じたら | 自分の問題で CBC・SCIP なども測る |
| 時間制限が大事 | 制限が守られるかを試してから使う |
| ギャップを見たい | HiGHS（`best_bound` を返す） |
| 製品に組み込んで配布 | ライセンスを確認する |
| さらに大規模・高速 | 商用ソルバーも検討する |
