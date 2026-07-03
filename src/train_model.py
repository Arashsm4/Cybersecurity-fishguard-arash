"""
train_model.py

Training code for the phishing detector.

Flow:
1. Load the CSV dataset.
2. Validate labels and columns.
3. Split into training and testing data.
4. Convert text into TF-IDF features.
5. Train Logistic Regression.
6. Save the model and evaluation report.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Tuple

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

try:
    from .preprocess import clean_text
except ImportError:
    from preprocess import clean_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "emails.csv"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "phishing_model.joblib"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "evaluation_report.txt"


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    """Load and validate the dataset before training."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)

    required_columns = {"email_text", "label"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    df = df.dropna(subset=["email_text", "label"]).copy()
    df["email_text"] = df["email_text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.lower().str.strip()

    allowed_labels = {"phishing", "legitimate"}
    bad_labels = set(df["label"].unique()) - allowed_labels
    if bad_labels:
        raise ValueError(f"Labels must be phishing or legitimate. Found: {sorted(bad_labels)}")

    if len(df) < 40:
        raise ValueError("Dataset is too small. Use at least 40 emails for this prototype.")

    return df


def build_pipeline() -> Pipeline:
    """Create the text vectorizer and classifier pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=clean_text,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=207,
                ),
            ),
        ]
    )


def train_model(
    dataset_path: Path = DEFAULT_DATASET,
    model_path: Path = DEFAULT_MODEL,
    report_path: Path = DEFAULT_REPORT,
    test_size: float = 0.25,
) -> Tuple[Pipeline, Dict[str, float]]:
    """Train, evaluate, save model, and write a report file."""
    df = load_dataset(dataset_path)

    X = df["email_text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=207,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "total_samples": int(len(df)),
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    report_lines = [
        "PhishGuard - Model Evaluation Report",
        "=" * 48,
        f"Dataset: {dataset_path}",
        f"Total samples: {len(df)}",
        f"Training samples: {len(X_train)}",
        f"Testing samples: {len(X_test)}",
        "",
        f"Accuracy:  {accuracy:.4f}",
        f"Precision: {precision:.4f}",
        f"Recall:    {recall:.4f}",
        f"F1-score:  {f1:.4f}",
        "",
        "Confusion Matrix",
        "Rows = real labels, columns = predicted labels",
        "Label order: legitimate, phishing",
        str(confusion_matrix(y_test, y_pred, labels=["legitimate", "phishing"])),
        "",
        "Classification Report",
        classification_report(y_test, y_pred, zero_division=0),
        "",
        "Dataset Check",
        str(df["label"].value_counts()),
        "",
        "Important Note",
        (
            "This is a coursework prototype. A real phishing detector would need "
            "a larger real-world dataset, email headers, URL reputation checks, "
            "attachment scanning, and continuous testing."
        ),
    ]

    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return pipeline, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the PhishGuard phishing detector.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="Path to emails.csv")
    parser.add_argument("--model", default=str(DEFAULT_MODEL), help="Output model path")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Output report path")
    args = parser.parse_args()

    _, metrics = train_model(
        dataset_path=Path(args.dataset),
        model_path=Path(args.model),
        report_path=Path(args.report),
    )

    print("Model trained successfully.")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1-score:  {metrics['f1_score']:.4f}")


if __name__ == "__main__":
    main()
