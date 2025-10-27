import pandas as pd

df = pd.read_csv("Train_knight.csv")
df.columns = df.columns.str.strip().str.lower()

if df["knight"].dtype == object:
    df["knight"] = df["knight"].map({
        "Jedi": 1,
        "Sith": 0
    })

corr = df.corr(numeric_only=True)

if "knight" not in corr.columns:
    raise KeyError("Column 'knight' not found after encoding. Check CSV content!")

target_corr = corr["knight"].sort_values(ascending=False)

print(target_corr)
