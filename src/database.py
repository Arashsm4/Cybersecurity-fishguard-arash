"""
database.py

SQLite storage for PhishGuard.

SQLite keeps the project light: one local database file, no server setup, and
enough structure to show that analysis results are stored properly.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "phishguard.db"


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_text TEXT NOT NULL,
    prediction TEXT NOT NULL,
    confidence REAL NOT NULL,
    suspicious_keywords TEXT,
    number_of_links INTEGER DEFAULT 0,
    number_of_emails INTEGER DEFAULT 0,
    urgent_word_count INTEGER DEFAULT 0,
    credential_word_count INTEGER DEFAULT 0,
    money_word_count INTEGER DEFAULT 0,
    exclamation_count INTEGER DEFAULT 0,
    uppercase_word_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Open a SQLite connection and return rows that can be read by column name."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> Path:
    """Create the database table if it does not already exist."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH

    with get_connection(path) as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()

    return path


def save_analysis_result(
    email_text: str,
    prediction: str,
    confidence: float,
    suspicious_keywords: List[str],
    features: Dict[str, int],
    db_path: Optional[Path] = None,
) -> int:
    """Save one email analysis result and return its database id."""
    init_db(db_path)

    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_results (
                email_text, prediction, confidence, suspicious_keywords,
                number_of_links, number_of_emails, urgent_word_count,
                credential_word_count, money_word_count, exclamation_count,
                uppercase_word_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email_text,
                prediction,
                confidence,
                ", ".join(suspicious_keywords),
                int(features.get("number_of_links", 0)),
                int(features.get("number_of_emails", 0)),
                int(features.get("urgent_word_count", 0)),
                int(features.get("credential_word_count", 0)),
                int(features.get("money_word_count", 0)),
                int(features.get("exclamation_count", 0)),
                int(features.get("uppercase_word_count", 0)),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def fetch_history(limit: int = 20, db_path: Optional[Path] = None) -> List[sqlite3.Row]:
    """Return the latest saved analysis results."""
    init_db(db_path)

    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM analysis_results
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return rows


def fetch_statistics(db_path: Optional[Path] = None) -> Dict[str, float]:
    """Return summary statistics for report output."""
    init_db(db_path)

    with get_connection(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) AS n FROM analysis_results").fetchone()["n"]
        phishing = conn.execute(
            "SELECT COUNT(*) AS n FROM analysis_results WHERE prediction = 'phishing'"
        ).fetchone()["n"]
        legitimate = conn.execute(
            "SELECT COUNT(*) AS n FROM analysis_results WHERE prediction = 'legitimate'"
        ).fetchone()["n"]
        avg_confidence = conn.execute(
            "SELECT AVG(confidence) AS n FROM analysis_results"
        ).fetchone()["n"]

    return {
        "total_scanned": int(total or 0),
        "phishing_detected": int(phishing or 0),
        "legitimate_detected": int(legitimate or 0),
        "average_confidence": float(avg_confidence or 0.0),
    }


def clear_history(db_path: Optional[Path] = None) -> None:
    """Delete saved analysis results. Useful before recording a clean demo."""
    init_db(db_path)

    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM analysis_results")
        conn.commit()
