"""
setup_project.py

One-command setup for PhishGuard.

Run:
    python setup_project.py

It creates the SQLite database, trains the model, and saves the evaluation
report. The web interface is started separately.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    """Run a command from the project root and stop if it fails."""
    print(f"\n$ {' '.join(command)}")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    print("Setting up PhishGuard...")
    print("Project root:", PROJECT_ROOT)

    for folder in ["models", "reports", "data", "samples", "web"]:
        (PROJECT_ROOT / folder).mkdir(exist_ok=True)

    run([sys.executable, "src/app.py", "init-db"])
    run([sys.executable, "src/app.py", "train"])

    print("\nSetup complete.")
    print("\nCLI examples:")
    print('python src/app.py analyze --text "Your account has been suspended. Verify your password now."')
    print("python src/app.py analyze-file samples/phishing_email.txt")
    print("python src/app.py analyze-file samples/legitimate_email.txt")
    print("python src/app.py history")
    print("python src/app.py report")

    print("\nOptional browser interface:")
    print("python src/web_app.py")
    print("Then open: http://127.0.0.1:8000")


if __name__ == "__main__":
    main()
