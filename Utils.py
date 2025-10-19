from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_confusion_matrix(y_true, y_pred, labels=["Legitimate", "Phishing"], title="Confusion Matrix"):
    """
    Plots a confusion matrix with counts and normalized values.

    Args:
        y_true (array-like): True labels
        y_pred (array-like): Predicted labels
        labels (list, optional): Class labels for the matrix axes
        title (str, optional): Title for the plot
    """
    cm = confusion_matrix(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)

    # Print metrics in console
    print(f"\n✅ Accuracy: {acc:.4f}")
    print("\n📊 Classification Report:\n", classification_report(y_true, y_pred))

    # Normalize confusion matrix for percentages
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, cbar=False)
    plt.title(f"{title}\n(Accuracy: {acc:.2%})", fontsize=13)
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.show()

    # Optional: also plot normalized version
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Greens", xticklabels=labels, yticklabels=labels, cbar=False)
    plt.title("Normalized Confusion Matrix", fontsize=13)
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.show()
