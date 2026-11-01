"""実行の入口：python -m factory_opt.main --data data --config config.toml"""
import argparse
import logging
import platform
import sys
import tomllib
from pathlib import Path

import pulp

from .data_io import DataError, read_input
from .model import build_model
from .report import save, to_tables
from .solve import SolveError, solve
from .verify import verify

log = logging.getLogger("factory_opt")


def run(data_folder: Path, config: dict) -> dict:
    log.info("PuLP %s / Python %s / ソルバー %s", pulp.__version__, platform.python_version(), config["solver"]["name"])
    log.info("入力を読み込みます: %s", data_folder)
    d = read_input(data_folder)
    log.info("商品 %d 件・ライン %d 本・資源 %d 種類", len(d["products"]), len(d["lines"]), len(d["capacity"]))

    prob, make = build_model(d)
    log.info("モデル: 変数 %d 個・制約 %d 本", prob.numVariables(), prob.numConstraints())

    result = solve(prob, make, config["solver"])
    log.info("解きました: %s / 利益 %s 円 / %.3f 秒", result["status"], f"{result['profit']:,.0f}", result["seconds"])

    problems = verify(d, result["make"])
    if problems:
        raise SolveError("検証に失敗しました:\n" + "\n".join(problems))
    log.info("検証: OK")

    paths = save(to_tables(d, result), Path(config["output"]["folder"]))
    log.info("保存しました: %s", ", ".join(p.name for p in paths))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="うめ食品の生産計画を作る")
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler("run.log", encoding="utf-8")])
    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    try:
        run(args.data, config)
    except DataError as e:
        log.error("入力データに問題があります:\n%s", e)
        return 1
    except SolveError as e:
        log.error("%s", e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
