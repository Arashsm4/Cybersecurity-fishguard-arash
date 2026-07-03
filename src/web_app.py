"""
web_app.py

Small local browser interface for PhishGuard using only Python's standard
library. No extra web framework is needed.

Run:
    python src/web_app.py

Open:
    http://127.0.0.1:8000
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import parse_qs, urlparse

try:
    from .app import analyze_email
    from .database import fetch_history, fetch_statistics, init_db
    from .train_model import DEFAULT_MODEL
except ImportError:
    from app import analyze_email
    from database import fetch_history, fetch_statistics, init_db
    from train_model import DEFAULT_MODEL


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_FOLDER = PROJECT_ROOT / "web"
EVALUATION_REPORT = PROJECT_ROOT / "reports" / "evaluation_report.txt"
HOST = "127.0.0.1"
PORT = 8000


def row_to_dict(row: Any) -> Dict[str, Any]:
    """Convert a SQLite row into a normal dictionary for JSON output."""
    return {
        "id": row["id"],
        "email_text": row["email_text"],
        "prediction": row["prediction"],
        "confidence": row["confidence"],
        "suspicious_keywords": row["suspicious_keywords"],
        "number_of_links": row["number_of_links"],
        "number_of_emails": row["number_of_emails"],
        "urgent_word_count": row["urgent_word_count"],
        "credential_word_count": row["credential_word_count"],
        "money_word_count": row["money_word_count"],
        "exclamation_count": row["exclamation_count"],
        "uppercase_word_count": row["uppercase_word_count"],
        "created_at": row["created_at"],
    }


def analyze_api_payload(payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Analyze JSON-style input and return an HTTP-style status and body."""
    email_text = str(payload.get("email_text", "")).strip()

    if not email_text:
        return 400, {"error": "Email text is required."}

    return 200, analyze_email(email_text, save=True)


def history_api(limit: int = 10) -> Tuple[int, list[Dict[str, Any]]]:
    """Return recent history rows for the browser."""
    limit = max(1, min(int(limit), 50))
    rows = fetch_history(limit=limit)
    return 200, [row_to_dict(row) for row in rows]


def report_api() -> Tuple[int, Dict[str, Any]]:
    """Return database statistics and the saved evaluation report."""
    evaluation_text = ""
    if EVALUATION_REPORT.exists():
        evaluation_text = EVALUATION_REPORT.read_text(encoding="utf-8")

    return 200, {
        "statistics": fetch_statistics(),
        "evaluation_report": evaluation_text,
    }


class PhishGuardHandler(BaseHTTPRequestHandler):
    """Request handler for static files and small JSON API routes."""

    def send_json(self, status_code: int, data: Any) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self.send_json(404, {"error": "File not found."})
            return

        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.send_file(WEB_FOLDER / "index.html", "text/html; charset=utf-8")
            return

        if parsed.path == "/styles.css":
            self.send_file(WEB_FOLDER / "styles.css", "text/css; charset=utf-8")
            return

        if parsed.path == "/app.js":
            self.send_file(WEB_FOLDER / "app.js", "application/javascript; charset=utf-8")
            return

        if parsed.path == "/api/health":
            self.send_json(200, {
                "status": "ok",
                "model_available": DEFAULT_MODEL.exists(),
                "database_ready": True,
            })
            return

        if parsed.path == "/api/history":
            params = parse_qs(parsed.query)
            limit = int(params.get("limit", [10])[0])
            status, body = history_api(limit=limit)
            self.send_json(status, body)
            return

        if parsed.path == "/api/report":
            status, body = report_api()
            self.send_json(status, body)
            return

        self.send_json(404, {"error": "Route not found."})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path != "/api/analyze":
            self.send_json(404, {"error": "Route not found."})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")

        try:
            payload = json.loads(raw_body or "{}")
        except json.JSONDecodeError:
            self.send_json(400, {"error": "Invalid JSON."})
            return

        status, body = analyze_api_payload(payload)
        self.send_json(status, body)

    def log_message(self, format: str, *args: Any) -> None:
        """Keep the terminal output clean during demos."""
        return


def main() -> None:
    """Start the local web server."""
    init_db()

    if not DEFAULT_MODEL.exists():
        print("Model not found. Run this first: python setup_project.py")
        return

    server = ThreadingHTTPServer((HOST, PORT), PhishGuardHandler)
    print("PhishGuard web UI is running.")
    print(f"Open: http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
