import pandas as pd

# === Load and normalize ===
df = pd.read_csv("Train_knight.csv")
df.columns = df.columns.str.strip().str.lower()

# === Encode the target column ===
if df["knight"].dtype == object:
    df["knight"] = df["knight"].map({
        "Jedi": 0,
        "Sith": 1
    })

# === Compute correlation matrix ===
corr = df.corr(numeric_only=True)

# === Extract correlation with knight ===
if "knight" not in corr.columns:
    raise KeyError("Column 'knight' not found after encoding. Check CSV content!")

target_corr = corr["knight"].sort_values(ascending=False)

# === Print results ===
print("\n=== Correlation factors with 'knight' ===\n")
print(target_corr)
