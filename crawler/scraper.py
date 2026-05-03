"""Scrape discussion question titles from topic pages."""

from html.parser import HTMLParser
from urllib.request import urlopen
import json
import re


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h1 = False
        self.h1_parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.in_h1 = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_h1:
            self.h1_parts.append(data)

    def get_title(self):
        title = " ".join(self.h1_parts)
        title = re.sub(r"\s+", " ", title).strip()
        return title


def fetch_html(url):
    with urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_question(html):
    parser = TitleParser()
    parser.feed(html)
    return parser.get_title()


def scrape_questions(topic_urls, output_path="storage/dataset.json", limit=120):
    records = []
    seen = set()

    for url in topic_urls:
        if len(records) >= limit:
            break
        try:
            html = fetch_html(url)
            question = extract_question(html)
        except Exception:
            continue

        if not question:
            continue
        key = question.lower()
        if key in seen:
            continue
        seen.add(key)

        records.append(
            {
                "id": len(records) + 1,
                "question": question,
                "category": "Group Discussion",
                "source": "IndiaBIX",
                "url": url,
            }
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    return records
