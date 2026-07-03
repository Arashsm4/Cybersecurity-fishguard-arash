"""
preprocess.py

Small text-cleaning and indicator-extraction tools for PhishGuard.

The model needs clean, consistent text. The report/demo also needs a few
human-readable indicators, so the result is not only "phishing/legitimate"
but also shows why the email looked suspicious.
"""

from __future__ import annotations

import re
import string
from typing import Dict, List


# Basic link detection. It is intentionally simple because this project focuses
# on text classification, not full URL reputation analysis.
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

# Basic email-address detection for body text.
EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+", re.IGNORECASE)


# Words commonly seen in pressure-based phishing messages.
URGENT_WORDS = {
    "urgent", "immediately", "now", "warning", "final", "suspended",
    "blocked", "expires", "expire", "verify", "confirm", "action required",
    "terminated", "deleted", "security alert", "unusual login",
}

# Words connected to login details, identity checks, and credentials.
CREDENTIAL_WORDS = {
    "password", "pin", "login", "credential", "credentials", "account",
    "verify", "identity", "seed phrase", "tan code", "bank details",
    "card number", "username",
}

# Words connected to payments, fake rewards, banking, or financial pressure.
MONEY_WORDS = {
    "bank", "payment", "billing", "invoice", "refund", "prize",
    "reward", "fee", "crypto", "wallet", "card", "money",
}

# One sorted list makes the displayed result easier to read.
SUSPICIOUS_KEYWORDS = sorted(URGENT_WORDS | CREDENTIAL_WORDS | MONEY_WORDS)


def clean_text(text: str) -> str:
    """
    Clean raw email text before TF-IDF vectorization.

    Steps:
    1. Convert to lowercase.
    2. Replace URLs with the token URL.
    3. Replace email addresses with the token EMAIL.
    4. Remove punctuation.
    5. Normalize spacing.

    The cleaning is deliberately explainable. A small assessment project should
    be clear enough that every step can be defended in the report.
    """
    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = URL_PATTERN.sub(" URL ", text)
    text = EMAIL_PATTERN.sub(" EMAIL ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()

    return text


def find_suspicious_keywords(text: str) -> List[str]:
    """
    Return suspicious words and phrases found in the email.

    This function does not replace the machine-learning model. It adds a simple
    explanation layer for the user, the demo, and the written report.
    """
    lowered = text.lower()
    found = [word for word in SUSPICIOUS_KEYWORDS if word in lowered]
    return sorted(set(found))


def extract_security_features(text: str) -> Dict[str, int]:
    """
    Extract simple security indicators from the raw email text.

    These indicators are stored in SQLite. They help show that the system tracks
    useful details for later review, not only the final prediction.
    """
    lowered = text.lower()

    return {
        "number_of_links": len(URL_PATTERN.findall(text)),
        "number_of_emails": len(EMAIL_PATTERN.findall(text)),
        "urgent_word_count": sum(1 for word in URGENT_WORDS if word in lowered),
        "credential_word_count": sum(1 for word in CREDENTIAL_WORDS if word in lowered),
        "money_word_count": sum(1 for word in MONEY_WORDS if word in lowered),
        "exclamation_count": text.count("!"),
        "uppercase_word_count": sum(
            1 for token in text.split() if token.isupper() and len(token) > 2
        ),
    }
