import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

def main():
	# --- Load dataset ---
	file = "Train_knight.csv"
	try:
		df = pd.read_csv(file)
	except FileNotFoundError:
		print(f"Error: file not found -> {file}")
		sys.exit(1)

	# --- Encode 'knight' column: Jedi=1, Sith=0 ---
	if "knight" not in df.columns:
		print("Error: 'knight' column not found in file.")
		sys.exit(1)

	df["knight"] = df["knight"].apply(lambda x: 1 if str(x).strip().lower() == "jedi" else 0)

	corr = df.corr(numeric_only=True)

	colors_white_red_black = ["#000000","#800080", "#FF0000", "#FFFFFF"]
	cmap_white_red_black = LinearSegmentedColormap.from_list(
		"white_red_black", colors_white_red_black, N=256
	)

	plt.figure(figsize=(12, 10))
	sns.heatmap(
		corr,
		cmap=cmap_white_red_black,
		fmt=".2f",
		linewidths=0.4,
		square=True,
		cbar=True,
		cbar_kws={"shrink": 0.8}
	)

	plt.title("Correlation Heatmap", fontsize=16, pad=15)
	plt.xticks(rotation=45, ha="right")
	plt.yticks(rotation=0)
	plt.tight_layout()

	output_file = "heatmap.png"
	plt.savefig(output_file, dpi=300)
	print(f"✅ Heatmap saved as '{output_file}'")


if __name__ == "__main__":
	main()
