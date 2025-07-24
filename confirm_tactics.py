import pandas as pd

df = pd.read_csv("csv_data/tactics.csv", encoding="utf-8-sig")
grades = df[df["type"] == "伝授"]["grade"].unique()

for g in grades:
    print(g)