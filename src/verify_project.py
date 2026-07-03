"""
verify_project.py

Runs a small verification pass for the project.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print(f"$ {' '.join(command)}")
    result = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}")


def check_dataset() -> None:
    dataset = PROJECT_ROOT / "data" / "emails.csv"
    df = pd.read_csv(dataset)

    if set(df.columns) != {"email_text", "label"}:
        raise AssertionError("Dataset columns must be email_text and label.")
    if df.isna().sum().sum() != 0:
        raise AssertionError("Dataset contains missing values.")
    if df.duplicated().sum() != 0:
        raise AssertionError("Dataset contains duplicate rows.")
    if set(df["label"].unique()) != {"phishing", "legitimate"}:
        raise AssertionError("Dataset labels must be phishing and legitimate.")

    print("Dataset verification passed.")
    print(df["label"].value_counts())


def check_web_functions() -> None:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

    from web_app import analyze_api_payload, history_api, report_api

    status, body = analyze_api_payload({
        "email_text": "Urgent warning: verify your password now at http://example.com"
    })
    if status != 200 or "prediction" not in body or "confidence" not in body:
        raise AssertionError("Web analyze function failed.")

    status, history = history_api(limit=5)
    if status != 200 or not isinstance(history, list):
        raise AssertionError("Web history function failed.")

    status, report = report_api()
    if status != 200 or "statistics" not in report:
        raise AssertionError("Web report function failed.")

    print("Web function verification passed.")


def main() -> None:
    check_dataset()
    run([sys.executable, "setup_project.py"])
    run([sys.executable, "src/app.py", "clear-history"])
    run([sys.executable, "src/app.py", "analyze-file", "samples/phishing_email.txt"])
    run([sys.executable, "src/app.py", "analyze-file", "samples/legitimate_email.txt"])
    run([sys.executable, "src/app.py", "history"])
    run([sys.executable, "src/app.py", "report"])
    check_web_functions()
    print("Project verification passed.")


if __name__ == "__main__":
    main()
