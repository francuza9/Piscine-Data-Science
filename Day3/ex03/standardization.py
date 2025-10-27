import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# === Change this line only when testing ===
FILENAME = "Test_knight.csv"


def standardize_and_plot(csv_path):
	"""Standardize feature data and display Jedi/Sith scatterplot."""
	df = pd.read_csv(csv_path)
	df.columns = df.columns.str.strip().str.lower()

	print("\n=== Original data sample ===")
	print(df.head(3))

	# Encode knight (target)
	if "knight" in df.columns and df["knight"].dtype == object:
		df["knight"] = df["knight"].map({"Jedi": 1, "Sith": 0})

	# Standardize all numeric columns EXCEPT 'knight'
	features = df.drop(columns=["knight"]) if "knight" in df.columns else df.copy()
	scaler = StandardScaler()
	df_std = features.copy()
	df_std[features.columns] = scaler.fit_transform(features)

	# Reattach knight column (unscaled)
	if "knight" in df.columns:
		df_std["knight"] = df["knight"]

	print("\n=== Standardized data sample ===")
	print(df_std.head(3))

	# Plot one Jedi/Sith scatterplot
	x_col, y_col = "strength", "empowered"

	plt.figure(figsize=(7, 5))
	if "knight" in df_std.columns:
		sns.scatterplot(
			data=df_std,
			x=x_col,
			y=y_col,
			hue="knight",
			palette={1: "red", 0: "blue"},
			alpha=0.6,
		)
		handles, labels = plt.gca().get_legend_handles_labels()
		labels = ["Sith" if lbl == "0" else "Jedi" for lbl in labels]
		plt.legend(handles=handles, labels=labels, title="Knight", loc="upper right")
	else:
		sns.scatterplot(
			data=df_std,
			x=x_col,
			y=y_col,
			color="gray",
			alpha=0.6,
			label="Knight"
		)
		plt.legend(title="Group", loc="upper right")

	plt.title(f"{csv_path}: standardized {x_col} vs {y_col}")
	plt.tight_layout()

	output_name = f"{csv_path.split('.')[0]}_standardized.png"
	plt.savefig(output_name, dpi=200)
	plt.close()
	print(f"✅ Saved {output_name}")


if __name__ == "__main__":
	standardize_and_plot(FILENAME)
