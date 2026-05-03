"""Matplotlib charts for word frequency and question lengths."""

import matplotlib.pyplot as plt


def plot_word_frequency(top10, out_path="analysis/word_frequency.png"):
    words = [w for w, _ in top10]
    counts = [c for _, c in top10]

    plt.figure(figsize=(10, 5))
    plt.bar(words, counts)
    plt.title("Top 10 Word Frequencies")
    plt.xlabel("Word")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_question_lengths(lengths, out_path="analysis/question_lengths.png"):
    plt.figure(figsize=(8, 5))
    plt.hist(lengths, bins=15)
    plt.title("Question Length Distribution")
    plt.xlabel("Words per Question")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
