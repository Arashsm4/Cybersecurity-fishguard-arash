"""
check_dataset.py

Small dataset inspection script.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET = PROJECT_ROOT / "data" / "emails.csv"


def main() -> None:
    df = pd.read_csv(DATASET)

    print("Dataset check")
    print("=" * 40)
    print(f"Path: {DATASET}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nLabel counts:")
    print(df["label"].value_counts())

    missing = df.isna().sum()
    print("\nMissing values:")
    print(missing)

    duplicates = df.duplicated().sum()
    print(f"\nDuplicate rows: {duplicates}")

    if set(df.columns) == {"email_text", "label"} and missing.sum() == 0 and duplicates == 0:
        print("\nResult: Dataset looks complete for the coursework prototype.")
    else:
        print("\nResult: Dataset may need cleanup.")


if __name__ == "__main__":
    main()
