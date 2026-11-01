from pathlib import Path
from ch17_plan import load_data, validate, solve_to_tables

data = load_data(Path(__file__).parent / "data_more")
assert not validate(data)
profit, plan, summary, res = solve_to_tables(data)
print(f"利益: {profit:,.0f} 円")
print(summary.to_string(index=False))
