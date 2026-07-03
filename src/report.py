"""
report.py

Terminal reporting for PhishGuard.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from .database import fetch_history, fetch_statistics
except ImportError:
    from database import fetch_history, fetch_statistics


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVALUATION_REPORT = PROJECT_ROOT / "reports" / "evaluation_report.txt"


def print_history(limit: int = 20) -> None:
    """Print recent saved predictions from SQLite."""
    rows = fetch_history(limit=limit)

    if not rows:
        print("No analysis history found yet.")
        return

    print("\nLatest Analysis Results")
    print("=" * 80)

    for row in rows:
        short_text = row["email_text"].replace("\n", " ")
        if len(short_text) > 90:
            short_text = short_text[:87] + "..."

        print(f"ID: {row['id']}")
        print(f"Time: {row['created_at']}")
        print(f"Prediction: {row['prediction']} | Confidence: {row['confidence']:.2%}")
        print(f"Suspicious keywords: {row['suspicious_keywords'] or 'None'}")
        print(f"Email: {short_text}")
        print("-" * 80)


def print_summary(evaluation_report_path: Optional[Path] = None) -> None:
    """Print database statistics and saved model evaluation."""
    stats = fetch_statistics()

    print("\nPhishGuard Summary")
    print("=" * 80)
    print(f"Total scanned emails:        {stats['total_scanned']}")
    print(f"Phishing predictions:        {stats['phishing_detected']}")
    print(f"Legitimate predictions:      {stats['legitimate_detected']}")
    print(f"Average confidence:          {stats['average_confidence']:.2%}")

    report_path = evaluation_report_path or DEFAULT_EVALUATION_REPORT

    if report_path.exists():
        print("\nSaved Model Evaluation")
        print("=" * 80)
        print(report_path.read_text(encoding="utf-8"))
    else:
        print("\nNo model evaluation report found.")
        print("Run this first: python src/app.py train")
