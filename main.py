"""Phase 1 pipeline: crawl, scrape, clean, QA, EDA, and visualize."""

from crawler.robots_checker import fetch_robots_txt, parse_rules, is_allowed
from crawler.crawler import crawl_topic_links
from crawler.scraper import scrape_questions
from processing.cleaning import add_tokens
from processing.quality import quality_filter
from analysis.eda import run_eda
from analysis.visualization import plot_word_frequency, plot_question_lengths
import json


def main():
    print("[1/8] Checking robots.txt ...")
    robots = fetch_robots_txt()
    rules = parse_rules(robots)
    for path in ["/group-discussion/", "/group-discussion/topics-with-answers/"]:
        print(f"  {path}: allowed={is_allowed(path, rules)}")

    print("[2/8] Crawling topic links ...")
    urls = crawl_topic_links(limit=120)
    print(f"  collected {len(urls)} topic URLs")

    print("[3/8] Scraping discussion questions ...")
    records = scrape_questions(urls, output_path="storage/dataset.json", limit=120)
    print(f"  scraped {len(records)} raw records")

    print("[4/8] Cleaning text ...")
    records = add_tokens(records)

    print("[5/8] Running data quality checks ...")
    records = quality_filter(records)

    print("[6/8] Saving cleaned dataset ...")
    with open("storage/dataset.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print("[7/8] Running EDA ...")
    eda = run_eda(records)

    print("[8/8] Generating charts ...")
    plot_word_frequency(eda["top10"])
    plot_question_lengths(eda["lengths"])
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
