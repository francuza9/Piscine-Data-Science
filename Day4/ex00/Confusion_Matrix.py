import sys
import matplotlib.pyplot as plt

def read_file(path):
	"""Read file lines, clean them, and ensure they contain only 'Jedi' or 'Sith'."""
	try:
		with open(path, "r") as f:
			lines = [line.strip().capitalize() for line in f if line.strip()]
		for val in lines:
			if val not in ("Jedi", "Sith"):
				raise ValueError(f"Invalid label '{val}' in {path}")
		return lines
	except FileNotFoundError:
		print(f"Error: file not found -> {path}")
		sys.exit(1)

def compute_confusion_matrix(truths, preds):
	"""Return 2x2 confusion matrix: [[TP_jedi, FN_jedi], [FP_jedi, TP_sith]]"""
	if len(truths) != len(preds):
		print("Error: predictions and truth files must have the same number of lines.")
		sys.exit(1)

	P_JEDI = P_SITH = N_JEDI = N_SITH = 0

	for t, p in zip(truths, preds):
		if t == "Jedi" and p == "Jedi":
			P_JEDI += 1
		elif t == "Jedi" and p == "Sith":
			N_SITH += 1        # not N_JEDI
		elif t == "Sith" and p == "Jedi":
			N_JEDI += 1
		elif t == "Sith" and p == "Sith":
			P_SITH += 1

	return [[P_JEDI, N_JEDI],
			[N_SITH, P_SITH]]

def precision_recall_f1(TP, FP, FN):
	"""Return precision, recall, f1 for a single class."""
	precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
	recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
	f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
	return precision, recall, f1

def main():
	if len(sys.argv) != 3:
		print("Usage: python3 Confusion_Matrix.py predictions.txt truth.txt")
		sys.exit(1)

	preds = read_file(sys.argv[1])
	truths = read_file(sys.argv[2])

	matrix = compute_confusion_matrix(truths, preds)
	total = len(truths)

	P_JEDI, N_JEDI = matrix[0]
	N_SITH, P_SITH = matrix[1]
	total_jedi = P_JEDI + N_JEDI
	total_sith = P_SITH + N_SITH

	# FIXED metric formulas
	prec_jedi, rec_jedi, f1_jedi = precision_recall_f1(P_JEDI, N_SITH, N_JEDI)
	prec_sith, rec_sith, f1_sith = precision_recall_f1(P_SITH, N_JEDI, N_SITH)

	accuracy = (P_JEDI + P_SITH) / total if total else 0

	print(f"Jedi {prec_jedi:.2f} {rec_jedi:.2f} {f1_jedi:.2f} {total_jedi}")
	print(f"Sith {prec_sith:.2f} {rec_sith:.2f} {f1_sith:.2f} {total_sith}")
	print(f"\naccuracy {accuracy:.2f} {total}")
	print(f"\n[[{matrix[0][0]} {matrix[0][1]}]\n [{matrix[1][0]} {matrix[1][1]}]]")

	# Display confusion matrix heatmap
	plt.imshow(matrix, cmap="Blues")
	plt.title("Confusion Matrix")
	plt.xticks([0, 1], ["Pred Jedi", "Pred Sith"])
	plt.yticks([0, 1], ["True Jedi", "True Sith"])

	for i in range(2):
		for j in range(2):
			plt.text(j, i, str(matrix[i][j]), ha="center", va="center", color="black")

	plt.xlabel("Predicted")
	plt.ylabel("True")
	plt.tight_layout()

	output_file = "confusion_matrix.png"
	plt.savefig(output_file)
	print(f"✅ Confusion matrix saved as '{output_file}'")


if __name__ == "__main__":
	main()
