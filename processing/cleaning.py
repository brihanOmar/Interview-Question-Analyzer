"""Text cleaning and preprocessing utilities."""

import string

STOPWORDS = {"the", "is", "a", "an", "in", "on", "for", "to", "of"}


def clean_text(text):
    text = (text or "").lower()
    return text.translate(str.maketrans("", "", string.punctuation))


def tokenize(text):
    return [tok for tok in text.split() if tok.strip()]


def remove_stopwords(tokens):
    return [tok for tok in tokens if tok not in STOPWORDS]


def add_tokens(records):
    for record in records:
        cleaned = clean_text(record.get("question", ""))
        tokens = tokenize(cleaned)
        record["tokens"] = remove_stopwords(tokens)
    return records
