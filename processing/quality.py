"""Dataset quality checks and filtering."""


def quality_filter(records, min_len=3):
    total = len(records)
    clean = []
    seen = set()
    duplicates_removed = 0

    for r in records:
        q = (r.get("question") or "").strip()
        if not q:
            continue

        key = q.lower()
        if key in seen:
            duplicates_removed += 1
            continue
        seen.add(key)

        if len(q.split()) < min_len:
            continue
        clean.append(r)

    print(f"[quality] total records: {total}")
    print(f"[quality] duplicates removed: {duplicates_removed}")
    print(f"[quality] clean records: {len(clean)}")
    return clean
