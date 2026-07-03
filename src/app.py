"""
app.py

Command-line interface for PhishGuard.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

import joblib

try:
    from .database import clear_history, init_db, save_analysis_result
    from .preprocess import extract_security_features, find_suspicious_keywords
    from .report import print_history, print_summary
    from .train_model import DEFAULT_MODEL, train_model
except ImportError:
    from database import clear_history, init_db, save_analysis_result
    from preprocess import extract_security_features, find_suspicious_keywords
    from report import print_history, print_summary
    from train_model import DEFAULT_MODEL, train_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_model(model_path: Path = DEFAULT_MODEL) -> Any:
    """
    Load the trained scikit-learn pipeline.

    The saved pipeline contains the TF-IDF vectorizer and Logistic Regression
    classifier together, so prediction needs only one file.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}\n"
            "Train it first with: python src/app.py train"
        )

    return joblib.load(model_path)


def analyze_email(email_text: str, save: bool = True) -> Dict[str, Any]:
    """
    Analyze one email and optionally save the result in SQLite.

    This shared function is used by both the CLI and the browser interface.
    One engine, two dashboards: terminal and web.
    """
    model = load_model()
    prediction = str(model.predict([email_text])[0])

    probabilities = model.predict_proba([email_text])[0]
    classes = list(model.classes_)
    confidence = float(probabilities[classes.index(prediction)])

    suspicious_keywords = find_suspicious_keywords(email_text)
    features = extract_security_features(email_text)

    row_id = None
    if save:
        row_id = save_analysis_result(
            email_text=email_text,
            prediction=prediction,
            confidence=confidence,
            suspicious_keywords=suspicious_keywords,
            features=features,
        )

    return {
        "id": row_id,
        "prediction": prediction,
        "confidence": confidence,
        "suspicious_keywords": suspicious_keywords,
        "features": features,
    }


# Older notes may use the name predict_email, so this alias keeps it available.
predict_email = analyze_email


def print_prediction_result(result: Dict[str, Any]) -> None:
    """Print one prediction result in a readable terminal format."""
    print("\nPhishGuard Analysis Result")
    print("=" * 80)
    print(f"Prediction: {result['prediction'].upper()}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Database ID: {result['id'] if result['id'] is not None else 'Not saved'}")

    keywords = result["suspicious_keywords"]
    print(f"Suspicious keywords: {', '.join(keywords) if keywords else 'None'}")

    print("\nExtracted security indicators:")
    for key, value in result["features"].items():
        print(f"  - {key}: {value}")

    print("\nRecommendation:")
    if result["prediction"] == "phishing":
        print("Treat this email as suspicious. Do not click links, open attachments,")
        print("or provide credentials until the sender and domain are verified.")
    else:
        print("The email looks legitimate according to the current model.")
        print("Still verify any message that asks for sensitive action.")


def command_train(_: argparse.Namespace) -> None:
    """Train the model and print evaluation metrics."""
    _, metrics = train_model()

    print("Model trained successfully.")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1-score:  {metrics['f1_score']:.4f}")
    print(f"Model saved to: {DEFAULT_MODEL}")
    print(f"Evaluation report saved to: {PROJECT_ROOT / 'reports' / 'evaluation_report.txt'}")


def command_analyze(args: argparse.Namespace) -> None:
    """Analyze email text passed directly in the terminal."""
    result = analyze_email(args.text, save=not args.no_save)
    print_prediction_result(result)


def command_analyze_file(args: argparse.Namespace) -> None:
    """Analyze an email stored in a text file."""
    path = Path(args.file)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    email_text = path.read_text(encoding="utf-8")
    result = analyze_email(email_text, save=not args.no_save)
    print_prediction_result(result)


def command_history(args: argparse.Namespace) -> None:
    """Show latest saved database results."""
    print_history(limit=args.limit)


def command_report(_: argparse.Namespace) -> None:
    """Show database statistics and model evaluation."""
    print_summary()


def command_init_db(_: argparse.Namespace) -> None:
    """Create the SQLite database."""
    db_path = init_db()
    print(f"Database initialized at: {db_path}")


def command_clear_history(_: argparse.Namespace) -> None:
    """Clear saved analysis history."""
    clear_history()
    print("Analysis history cleared.")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="phishguard",
        description="PhishGuard - phishing email detection using Python and machine learning.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train the machine-learning model")
    train_parser.set_defaults(func=command_train)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze email text")
    analyze_parser.add_argument("--text", required=True, help="Email text to analyze")
    analyze_parser.add_argument("--no-save", action="store_true", help="Do not save result")
    analyze_parser.set_defaults(func=command_analyze)

    analyze_file_parser = subparsers.add_parser("analyze-file", help="Analyze email text file")
    analyze_file_parser.add_argument("file", help="Path to a .txt email sample")
    analyze_file_parser.add_argument("--no-save", action="store_true", help="Do not save result")
    analyze_file_parser.set_defaults(func=command_analyze_file)

    history_parser = subparsers.add_parser("history", help="Show latest analysis results")
    history_parser.add_argument("--limit", type=int, default=20, help="Number of rows to show")
    history_parser.set_defaults(func=command_history)

    report_parser = subparsers.add_parser("report", help="Show summary report")
    report_parser.set_defaults(func=command_report)

    init_parser = subparsers.add_parser("init-db", help="Create SQLite database")
    init_parser.set_defaults(func=command_init_db)

    clear_parser = subparsers.add_parser("clear-history", help="Delete stored analysis history")
    clear_parser.set_defaults(func=command_clear_history)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the CLI application."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
