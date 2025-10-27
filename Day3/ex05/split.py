import pandas as pd
import sys
from sklearn.model_selection import train_test_split


def split_dataset(csv_path, train_ratio=0.8):
	"""Split the dataset into training and validation CSVs."""
	try:
		df = pd.read_csv(csv_path)
	except FileNotFoundError:
		print(f"❌ File not found: {csv_path}")
		sys.exit(1)

	total_rows = len(df)
	if total_rows == 0:
		print("❌ The file is empty.")
		sys.exit(1)

	# Random split (80% training / 20% validation)
	train_df, val_df = train_test_split(df, train_size=train_ratio, random_state=42, shuffle=True)

	# Output filenames
	train_name = "Training_knight.csv"
	val_name = "Validation_knight.csv"

	# Save CSVs
	train_df.to_csv(train_name, index=False)
	val_df.to_csv(val_name, index=False)

	print("✅ Split completed successfully:")
	print(f"  • Total rows: {total_rows}")
	print(f"  • Training set: {len(train_df)} rows ({train_ratio*100:.0f}%) → {train_name}")
	print(f"  • Validation set: {len(val_df)} rows ({(1-train_ratio)*100:.0f}%) → {val_name}")


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python split.py <csv_file>")
		sys.exit(1)

	csv_file = sys.argv[1]
	split_dataset(csv_file, train_ratio=0.8)
