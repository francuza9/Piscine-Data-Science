import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# === Change this line to test the other dataset ===
# FILENAME = "Train_knight.csv"
FILENAME = "Train_knight.csv"


def normalize_and_plot(csv_path):
	"""Normalize numeric data and display Jedi/Sith scatterplot."""
	df = pd.read_csv(csv_path)
	df.columns = df.columns.str.strip().str.lower()

	print("\n=== Original data sample ===")
	print(df.head(3))

	# Encode target (Jedi = 1, Sith = 0)
	if "knight" in df.columns and df["knight"].dtype == object:
		df["knight"] = df["knight"].map({"Jedi": 1, "Sith": 0})

	# Normalize all numeric columns except 'knight'
	features = df.drop(columns=["knight"]) if "knight" in df.columns else df.copy()
	scaler = MinMaxScaler()
	df_norm = features.copy()
	df_norm[features.columns] = scaler.fit_transform(features)

	# Reattach target
	if "knight" in df.columns:
		df_norm["knight"] = df["knight"]

	print("\n=== Normalized data sample ===")
	print(df_norm.head(3))

	# Choose same feature pair as in ex03
	x_col, y_col = "strength", "empowered"

	plt.figure(figsize=(7, 5))
	if "knight" in df_norm.columns:
		# Jedi vs Sith
		sns.scatterplot(
			data=df_norm,
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
		# No knight column (test data)
		sns.scatterplot(
			data=df_norm,
			x=x_col,
			y=y_col,
			color="gray",
			alpha=0.6,
			label="Knight"
		)
		plt.legend(title="Group", loc="upper right")


	plt.title(f"{csv_path}: normalized {x_col} vs {y_col}")
	plt.tight_layout()

	output_name = f"{csv_path.split('.')[0]}_normalized.png"
	plt.savefig(output_name, dpi=200)
	plt.close()
	print(f"✅ Saved {output_name}")


if __name__ == "__main__":
	normalize_and_plot(FILENAME)
