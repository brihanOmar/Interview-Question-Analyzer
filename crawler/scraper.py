"""IndiaBIX Group Discussion scraper.

Scrapes topic pages and extracts the primary question from <h1>, with a
fallback to <title> when needed.
"""

from __future__ import annotations

import re
import time
from html.parser import HTMLParser
from typing import Dict, List, Optional, Set
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

BASE_URL = "https://www.indiabix.com"
TOPICS_LIST_URL = "https://www.indiabix.com/group-discussion/topics-with-answers/"
TOPIC_PATH_PATTERN = re.compile(r"^/group-discussion/[^/]+/?$")


class TopicLinksParser(HTMLParser):
    """Collects Group Discussion topic links from listing pages."""

    def __init__(self) -> None:
        super().__init__()
        self.links: Set[str] = set()

    def handle_starttag(self, tag: str, attrs):
        if tag != "a":
            return

        href = None
        for key, value in attrs:
            if key == "href":
                href = value
                break

        if not href:
            return

        normalized = _normalize_topic_url(href)
        if normalized:
            self.links.add(normalized)


class QuestionParser(HTMLParser):
    """Extracts <h1> and <title> text from topic pages."""

    def __init__(self) -> None:
        super().__init__()
        self._in_h1 = False
        self._in_title = False
        self.h1_parts: List[str] = []
        self.title_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag == "h1":
            self._in_h1 = True
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str):
        if tag == "h1":
            self._in_h1 = False
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str):
        if self._in_h1:
            self.h1_parts.append(data)
        if self._in_title:
            self.title_parts.append(data)

    @property
    def h1_text(self) -> str:
        return " ".join(self.h1_parts)

    @property
    def title_text(self) -> str:
        return " ".join(self.title_parts)


def _fetch_html(url: str, timeout: int = 20) -> Optional[str]:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except (HTTPError, URLError, TimeoutError):
        return None


def _clean_question(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    cleaned = re.sub(r"\s*-\s*IndiaBIX\s*$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _is_valid_question(text: str) -> bool:
    if not text or len(text) < 8:
        return False
    lowered = text.lower()
    if lowered in {"indiabix", "group discussion", "topics with answers"}:
        return False
    return True


def _normalize_topic_url(url: str) -> Optional[str]:
    absolute = urljoin(BASE_URL, url.strip())
    parsed = urlparse(absolute)

    if parsed.scheme not in {"http", "https"}:
        return None

    if parsed.netloc not in {"www.indiabix.com", "indiabix.com"}:
        return None

    path = parsed.path.rstrip("/") + "/"
    if path == "/group-discussion/topics-with-answers/":
        return None

    if not TOPIC_PATH_PATTERN.match(path):
        return None

    return f"https://www.indiabix.com{path}"


def _extract_question_from_html(html: str) -> str:
    parser = QuestionParser()
    parser.feed(html)

    h1 = _clean_question(parser.h1_text)
    if _is_valid_question(h1):
        return h1

    title = _clean_question(parser.title_text)
    return title if _is_valid_question(title) else ""


def _collect_topic_urls(minimum: int = 120, max_pages: int = 40) -> List[str]:
    urls: Set[str] = set()

    for page in range(1, max_pages + 1):
        page_candidates = [
            TOPICS_LIST_URL if page == 1 else f"{TOPICS_LIST_URL}?page={page}",
            f"{TOPICS_LIST_URL}{page}/",
        ]
        if page == 1:
            page_candidates = [TOPICS_LIST_URL]

        grew = False
        for page_url in page_candidates:
            html = _fetch_html(page_url)
            if not html:
                continue

            parser = TopicLinksParser()
            parser.feed(html)
            before = len(urls)
            urls.update(parser.links)
            grew = grew or (len(urls) > before)

        if len(urls) >= minimum and not grew:
            break

        time.sleep(0.05)

    return sorted(urls)


def scrape_indiabix_group_discussion(topic_urls: Optional[List[str]] = None) -> List[Dict]:
    """Scrape IndiaBIX GD questions from full topic URLs."""

    candidate_urls: List[str] = []
    if topic_urls:
        for raw_url in topic_urls:
            normalized = _normalize_topic_url(raw_url)
            if normalized:
                candidate_urls.append(normalized)

    candidate_urls = list(dict.fromkeys(candidate_urls))

    if len(candidate_urls) < 100:
        discovered = _collect_topic_urls(minimum=180, max_pages=60)
        known = set(candidate_urls)
        for url in discovered:
            if url not in known:
                candidate_urls.append(url)
                known.add(url)

    print(f"[DEBUG] Number of URLs received: {len(candidate_urls)}")

    records: List[Dict] = []
    seen_questions: Set[str] = set()
    scraped_pages = 0
    attempted_urls: Set[str] = set()

    while len(records) < 100:
        start_count = len(records)
        for url in candidate_urls:
            if url in attempted_urls:
                continue

            attempted_urls.add(url)
            html = _fetch_html(url)
            if not html:
                continue

            scraped_pages += 1
            question = _extract_question_from_html(html)
            if not _is_valid_question(question):
                continue

            dedupe_key = question.lower()
            if dedupe_key in seen_questions:
                continue

            seen_questions.add(dedupe_key)
            records.append(
                {
                    "id": len(records) + 1,
                    "question": question,
                    "category": "Group Discussion",
                    "source": "IndiaBIX",
                    "url": url,
                }
            )

            if len(records) >= 100:
                break

        if len(records) >= 100:
            break

        # Retry by crawling for more topic links automatically.
        more_urls = _collect_topic_urls(minimum=len(candidate_urls) + 100, max_pages=100)
        known_urls = set(candidate_urls)
        for url in more_urls:
            if url not in known_urls:
                candidate_urls.append(url)
                known_urls.add(url)

        no_progress = len(records) == start_count and len(known_urls) == len(attempted_urls)
        if no_progress:
            break

    print(f"[DEBUG] Number of pages scraped: {scraped_pages}")
    print(f"[DEBUG] Number of successful questions extracted: {len(records)}")

    return records


if __name__ == "__main__":
    data = scrape_indiabix_group_discussion()
    print(f"Scraped records: {len(data)}")
