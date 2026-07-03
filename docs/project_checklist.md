# Project Checklist

## Core Features

- Basic machine learning concept applied to a cybersecurity problem: yes
- Text analysis for security: yes
- Complete Python application: yes
- Threat detection and false positive/false negative explanation: yes
- Practical phishing email detection tool: yes

## Python Application

- Email text extraction and preprocessing: `src/preprocess.py`
- Feature extraction from email content: TF-IDF in `src/train_model.py`
- Machine learning model implementation: Logistic Regression in `src/train_model.py`
- Command-line interface: `src/app.py`
- Basic reporting: `src/report.py`

## Machine Learning

- scikit-learn used: yes
- TF-IDF vectorization used: yes
- Logistic Regression classifier used: yes
- Model evaluation metrics: accuracy, precision, recall, F1-score, confusion matrix
- Evaluation report saved: `reports/evaluation_report.txt`

## Database Storage

- SQLite integration: yes
- Stores analysis results: yes
- Tracks detected phishing attempts: yes
- Saves extracted features for future reference: yes
- Database file: `phishguard.db`

## Optional Browser Interface

- HTML page: `web/index.html`
- CSS file: `web/styles.css`
- JavaScript file: `web/app.js`
- Python backend: `src/web_app.py`
- API route for analysis: `/api/analyze`
- API route for history: `/api/history`
- API route for report: `/api/report`

## Demo

- Sample phishing email: `samples/phishing_email.txt`
- Sample legitimate email: `samples/legitimate_email.txt`
- Demo script: `docs/demo_script.md`

## One-Script Setup

- `setup_project.py` initializes the database and trains the model.
