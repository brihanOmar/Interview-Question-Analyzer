"""Topic link crawler for IndiaBIX Group Discussion pages."""

from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

START_URL = "https://www.indiabix.com/group-discussion/topics-with-answers/"
BASE_URL = "https://www.indiabix.com"


class TopicLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = ""
        for key, value in attrs:
            if key == "href":
                href = value or ""
                break

        if "/group-discussion/" not in href:
            return

        full_url = urljoin(BASE_URL, href)
        parsed = urlparse(full_url)
        if parsed.netloc not in ("www.indiabix.com", "indiabix.com"):
            return

        clean = f"https://www.indiabix.com{parsed.path}"
        if parsed.path.endswith("/topics-with-answers/"):
            return

        if clean not in self.links:
            self.links.append(clean)


def fetch_html(url):
    with urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def crawl_topic_links(limit=120):
    html = fetch_html(START_URL)
    parser = TopicLinkParser()
    parser.feed(html)
    unique = []
    seen = set()

    for link in parser.links:
        if link not in seen:
            seen.add(link)
            unique.append(link)
        if len(unique) >= limit:
            break

    return unique[:limit]
