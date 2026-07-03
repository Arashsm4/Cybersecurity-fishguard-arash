# B207 Cyber Security Project Report Draft

## Project Title

PhishGuard: A Machine Learning Based Phishing Email Detection System

## 1. Introduction

Phishing is a common cybersecurity threat that uses social engineering to manipulate users. Instead of
attacking only software or hardware, phishing attacks target human behaviour by using urgency, fear,
authority, fake rewards, or account warnings. The goal is often to make the victim click a malicious
link, open a harmful attachment, or reveal sensitive information such as passwords, payment details, or
personal data.

This project implements a simple phishing email detection system using Python and machine learning. The
system analyzes email text and predicts whether the email is phishing or legitimate. The result is saved
in an SQLite database so previous detections can be reviewed.

## 2. Project Aim

The aim of this project is to build a practical tool that applies cybersecurity and machine learning
concepts to phishing detection. The system demonstrates text preprocessing, TF-IDF feature extraction,
Logistic Regression classification, SQLite database storage, command-line reporting, and a small local
browser interface.

## 3. System Design

The system follows a simple pipeline. First, the user provides email text through the command line, a text
file, or the browser interface. The text is cleaned by lowercasing it, replacing URLs and email addresses,
removing punctuation, and normalizing spaces. The cleaned text is converted into numerical features using
TF-IDF. A Logistic Regression model then predicts whether the email is phishing or legitimate. The
prediction, confidence score, suspicious keywords, and security indicators are stored in the SQLite
database.

## 4. Implementation

Python was selected because it is suitable for text processing, machine learning, and database integration.
The scikit-learn library was used for TF-IDF vectorization and Logistic Regression. SQLite was selected
because it is simple, local, and does not require a separate database server. A small browser interface was
created with HTML, CSS, JavaScript, and a Python standard-library HTTP server.

## 5. Machine Learning Method

The dataset contains two labels: phishing and legitimate. The text is transformed into TF-IDF features.
TF-IDF gives more importance to words or phrases that help distinguish phishing messages from normal
emails. Logistic Regression was used because it is simple, fast, and explainable.

The model is evaluated using accuracy, precision, recall, F1-score, and a confusion matrix. These metrics
are important because phishing detection has two possible errors. A false positive happens when a
legitimate email is classified as phishing. A false negative happens when a phishing email is missed. In
cybersecurity, false negatives can be dangerous because the user may trust a malicious email.

## 6. Browser Interface

The local browser interface allows the user to paste an email and submit it for analysis. JavaScript sends
the text to the Python backend through the `/api/analyze` route. The backend returns the prediction,
confidence score, suspicious keywords, and security indicators as JSON. The result is displayed in the
browser and saved in SQLite.

## 7. Database Storage

SQLite is used to store analysis results. Each record includes the email text, prediction, confidence,
suspicious keywords, number of links, urgent words, credential words, money words, and timestamp. This
provides a simple audit trail and supports later review.

## 8. Security Concepts

This project is connected to social engineering because phishing relies on manipulating users rather than
only attacking technical systems. The project also demonstrates threat detection because it identifies
suspicious text patterns and provides a prediction.

## 9. Testing and Evaluation

Manual testing can be done with:

```bash
python setup_project.py
python src/app.py analyze-file samples/phishing_email.txt
python src/app.py analyze-file samples/legitimate_email.txt
python src/app.py history
python src/app.py report
python src/web_app.py
```

## 10. Limitations and Future Improvements

This system is a coursework prototype. The dataset is suitable for demonstration, but a real phishing
detection system would require a much larger real-world dataset. Future improvements could include sender
domain analysis, email header analysis, URL reputation checking, attachment scanning, and model retraining.

## 11. Conclusion

PhishGuard demonstrates a complete but simple cybersecurity application. It combines phishing detection,
text preprocessing, machine learning, database storage, reporting, and a local browser interface.

## 12. References

- B207 Cyber Security lecture materials.
- scikit-learn documentation.
- Python SQLite documentation.
