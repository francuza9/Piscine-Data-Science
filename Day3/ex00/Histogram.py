import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def plot_knight_histograms(csv_path, output_name, show_target_split=True):
    """Create histograms of all features, optionally colored by knight side."""
    # === Load dataset ===
    df = pd.read_csv(csv_path)
    target_col = "knight"

    # Collect all feature columns except the target
    features = [col for col in df.columns if col != target_col]

    # === Prepare figure grid ===
    n_cols = 4
    n_rows = (len(features) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3 * n_rows))
    axes = axes.flatten()

    sns.set_style("whitegrid")
    sns.set_palette("Set2")

    # === Draw one histogram per feature ===
    for i, feature in enumerate(features):
        ax = axes[i]
        if show_target_split:
            sns.histplot(
                data=df,
                x=feature,
                hue=target_col,
                bins=30,
                kde=True,
                element="step",
                alpha=0.6,
                ax=ax,
            )
        else:
            sns.histplot(
                data=df,
                x=feature,
                bins=30,
                kde=True,
                element="step",
                alpha=0.6,
                color="skyblue",
                ax=ax,
            )
        ax.set_title(feature)
        ax.set_xlabel("")
        ax.set_ylabel("")

    # Remove any unused subplot spaces
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # === Final layout and save ===
    title = f"Knight Skills — {'Jedi vs Sith' if show_target_split else 'All Knights'}"
    fig.suptitle(title, fontsize=18, weight="bold")

    plt.tight_layout()
    plt.subplots_adjust(top=0.92)

    output_path = f"{output_name}.png"
    plt.savefig(output_path, dpi=200)
    plt.close(fig)

    print(f"✅ Saved {output_path} at {os.path.abspath(output_path)}")


# === MAIN EXECUTION ===
if __name__ == "__main__":
    # Test file: overall data distribution
    plot_knight_histograms("Test_knight.csv", "histogram_test", show_target_split=False)

    # Train file: separated by knight side (Jedi vs Sith)
    plot_knight_histograms("Train_knight.csv", "histogram_train", show_target_split=True)