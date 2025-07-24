<<<<<<< HEAD
import pandas as pd

df = pd.read_csv("csv_data/tactics.csv", encoding="utf-8-sig")
grades = df[df["type"] == "伝授"]["grade"].unique()

for g in grades:
=======
import pandas as pd

df = pd.read_csv("csv_data/tactics.csv", encoding="utf-8-sig")
grades = df[df["type"] == "伝授"]["grade"].unique()

for g in grades:
>>>>>>> 6cc6e22068fd297841f9570f83ea405279f90609
    print(g)