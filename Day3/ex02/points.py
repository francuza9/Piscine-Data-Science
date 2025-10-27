import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


def scatter_plot(csv_path, x_col, y_col, output_name, colored=False):
	"""Create scatter plot with or without Jedi/Sith coloring."""
	df = pd.read_csv(csv_path)
	df.columns = df.columns.str.strip().str.lower()

	plt.figure(figsize=(7, 5))

	if colored and "knight" in df.columns:
		# Jedi vs Sith
		if df["knight"].dtype == object:
			df["knight"] = df["knight"].map({"Jedi": 1, "Sith": 0})
		sns.scatterplot(
			data=df,
			x=x_col,
			y=y_col,
			hue="knight",
			palette={1: "red", 0: "blue"},
			alpha=0.6,
		)
		handles, labels = plt.gca().get_legend_handles_labels()
		plt.legend(handles=handles, labels=["Sith", "Jedi"], title="Knight", loc="upper right")
		legend_text = "(Jedi vs Sith)"
	else:
		# All Knights (gray)
		sns.scatterplot(
			data=df,
			x=x_col,
			y=y_col,
			color="gray",
			alpha=0.6,
			label="Knight"
		)
		plt.legend(title="Group", loc="upper right")
		legend_text = "(All Knights)"

	plt.title(f"{os.path.basename(csv_path)}: {x_col} vs {y_col} {legend_text}")
	plt.tight_layout()
	plt.savefig(output_name, dpi=200)
	plt.close()
	print(f"✅ Saved {output_name}")


if __name__ == "__main__":
	pair1 = ("strength", "empowered")
	pair2 = ("power", "sensitivity")

	# === TRAIN: Jedi vs Sith ===
	scatter_plot("Train_knight.csv", pair1[0], pair1[1], "train_jedi_sith_1.png", colored=True)
	scatter_plot("Train_knight.csv", pair2[0], pair2[1], "train_jedi_sith_2.png", colored=True)

	# === TEST: All Knights ===
	scatter_plot("Test_knight.csv", pair1[0], pair1[1], "test_knight_1.png", colored=False)
	scatter_plot("Test_knight.csv", pair2[0], pair2[1], "test_knight_2.png", colored=False)
