# サクサクPuLP — サンプルコード

「サクサクPuLP」のハンズオンで使うコードとデータです。Python の最適化ライブラリ PuLP 4 で、線形計画・整数計画の問題を解きます。データはすべて本書用の架空のものです。

本の本文は [`book/`](book/README.md) にあります。

## 必要なもの

| | バージョン |
|---|---|
| Python | 3.12 以上（PuLP 4.0.1 の条件） |
| PuLP ＋ HiGHS | `pulp[highs]==4.0.1` |
| pandas・openpyxl | 3.0.6・3.1.5（第17章から） |
| pytest | 9.1.1（第20章） |

## 準備

```bash
cd sakusaku-pulp
python3 -m venv .venv
source .venv/bin/activate        # Windows は .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

第19章のソルバー比較を試すときは、`requirements.txt` のコメントにある `pulp[cbc]`・`pulp[glpk]`・`pulp[scip]` も入れます。macOS で CBC が `Killed: 9` で止まるときは、第19章 19.3（付録D の D.5）の手順を参照してください。

## 実行

各章のフォルダに移動して実行します。

```bash
cd ch01
python ch01_brute_force.py
```

第20章はパッケージになっているので、`ch20/` で次のように実行します。

```bash
cd ch20
python -m factory_opt.main
python -m pytest -v
```

最適解が複数ある問題では、ソルバーやバージョンによって、目的関数の値が同じまま、変数の値だけが本文と違うことがあります。

## フォルダ

| フォルダ | 内容 |
|---------|------|
| `ch01/` 〜 `ch23/` | 各章のコード。ほかの章から import するファイルも、そのフォルダに入れてある |
| `chNN/data*/` | CSV データ（第17・18・20・21・22章） |
| `chNN/expected/` | 本文に載せた実行結果（出力を見比べるときに使う） |
| `book/` | 本の本文（章ごとの Markdown） |

ファイルの一覧は付録G を参照してください。
