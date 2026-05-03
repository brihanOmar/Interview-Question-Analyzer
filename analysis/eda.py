"""Basic exploratory data analysis for scraped questions."""

from collections import Counter


def run_eda(records):
    total = len(records)
    lengths = [len((r.get("question") or "").split()) for r in records]
    avg_len = (sum(lengths) / total) if total else 0

    all_tokens = []
    for r in records:
        all_tokens.extend(r.get("tokens", []))

    counter = Counter(all_tokens)
    top10 = counter.most_common(10)

    print(f"[eda] total questions: {total}")
    print(f"[eda] average question length: {avg_len:.2f} words")
    print(f"[eda] most frequent words: {top10}")
    print(f"[eda] top 10 keywords: {[w for w, _ in top10]}")

    return {
        "total_questions": total,
        "average_question_length": avg_len,
        "word_counts": counter,
        "top10": top10,
        "lengths": lengths,
    }
