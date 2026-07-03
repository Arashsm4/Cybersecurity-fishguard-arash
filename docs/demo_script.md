# PhishGuard Demo Script

## 1. Introduction

This project is called PhishGuard. It is a simple phishing email detection system built with Python.
It analyzes email text, predicts whether the email is phishing or legitimate, and stores the result in
an SQLite database.

## 2. Setup

```bash
pip install -r requirements.txt
python setup_project.py
```

This creates the database and trains the model.

## 3. Command-Line Test

```bash
python src/app.py analyze-file samples/phishing_email.txt
python src/app.py analyze-file samples/legitimate_email.txt
python src/app.py history
python src/app.py report
```

## 4. Browser Interface

```bash
python src/web_app.py
```

Open `http://127.0.0.1:8000`. Paste an email and click Analyze. The browser sends the email text to
the Python backend. The backend returns prediction, confidence, suspicious keywords, and security
indicators. The result is also stored in SQLite.

## 5. Conclusion

PhishGuard demonstrates phishing detection, text preprocessing, machine learning, database storage,
command-line reporting, and a small browser interface in one simple project.
