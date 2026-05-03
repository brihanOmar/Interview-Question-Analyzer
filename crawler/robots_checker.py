"""robots.txt utilities for ethical crawling checks."""

from urllib.request import urlopen

ROBOTS_URL = "https://www.indiabix.com/robots.txt"
USER_AGENT = "*"


def fetch_robots_txt(url=ROBOTS_URL):
    """Download robots.txt content.

    Ethical crawling note:
    Always check robots.txt before scraping any website and honor disallow
    directives so data collection respects site owner rules.
    """
    with urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_rules(robots_text, user_agent=USER_AGENT):
    """Parse allow/disallow rules for the target user agent."""
    rules = {"allow": [], "disallow": []}
    current_agents = []

    for raw_line in robots_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "user-agent":
            current_agents = [a.strip() for a in value.split()] if value else []
            continue

        applies = ("*" in current_agents) or (user_agent in current_agents)
        if not applies:
            continue

        if key == "allow":
            rules["allow"].append(value)
        elif key == "disallow":
            rules["disallow"].append(value)

    return rules


def is_allowed(path, rules):
    """Return True when a path is crawlable according to parsed rules."""
    matched_allow = ""
    matched_disallow = ""

    for allow_path in rules["allow"]:
        if path.startswith(allow_path) and len(allow_path) > len(matched_allow):
            matched_allow = allow_path

    for disallow_path in rules["disallow"]:
        if disallow_path and path.startswith(disallow_path) and len(disallow_path) > len(matched_disallow):
            matched_disallow = disallow_path

    if len(matched_allow) >= len(matched_disallow):
        return True
    return False


def run_check():
    robots_text = fetch_robots_txt()
    rules = parse_rules(robots_text)
    paths = ["/group-discussion/", "/group-discussion/topics-with-answers/"]
    for path in paths:
        print(f"[robots] {path} allowed: {is_allowed(path, rules)}")


if __name__ == "__main__":
    run_check()
