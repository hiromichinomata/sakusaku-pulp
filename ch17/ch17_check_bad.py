from pathlib import Path
from ch17_plan import load_data, validate

data = load_data(Path(__file__).parent / "data_bad")
for msg in validate(data):
    print("-", msg)
