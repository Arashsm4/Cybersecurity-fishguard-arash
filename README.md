# PhishGuard

PhishGuard is a B207 Cyber Security coursework project. It detects phishing-style emails using
Python, TF-IDF text vectorization, Logistic Regression, and SQLite database storage.

The project includes both a command-line interface and a small local browser interface. The CLI is the
main required application. The browser interface is included as an optional demo layer to show how a
backend can return analysis results to a user.

## Features

- Email text preprocessing
- TF-IDF feature extraction
- Logistic Regression classifier
- Model evaluation with accuracy, precision, recall, F1-score, and confusion matrix
- SQLite database storage
- Analysis history
- Summary report
- Simple local HTML/CSS/JavaScript interface
- Dataset checker

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

## One-Command Setup

```bash
python setup_project.py
```

This creates the SQLite database and trains the model.

## CLI Commands

```bash
python src/app.py train
python src/app.py analyze --text "Your account has been suspended. Verify your password now."
python src/app.py analyze-file samples/phishing_email.txt
python src/app.py history
python src/app.py report
python src/check_dataset.py
python src/app.py clear-history
```

## Optional Browser Interface

Start the local web server:

```bash
python src/web_app.py
```

Open:

```text
http://127.0.0.1:8000
```

The browser uses JavaScript `fetch()` to send email text to the Python backend. The backend returns a
JSON result and saves the analysis in SQLite.

## Dataset

The dataset is stored in `data/emails.csv` and contains two columns:

```text
email_text,label
```

Allowed labels are `phishing` and `legitimate`.

## Security Notes

The browser interface uses `textContent` when displaying user-provided email text. This prevents pasted
HTML from being rendered as active page content.

This is a local coursework prototype. A real phishing detection system would need a larger dataset,
email header analysis, URL reputation checks, attachment scanning, and continuous validation.
