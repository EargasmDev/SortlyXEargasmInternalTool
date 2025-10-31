import re
from rapidfuzz import process, fuzz

def normalize_name(name: str) -> str:
    """
    Clean and standardize names for comparison.
    Keeps hyphens since SKUs use them (e.g., HF-blue).
    Removes trailing serials or codes after main SKU.
    """
    name = name.lower().strip()
    # Remove long numeric or serial suffixes (e.g. -123456 or -122025-1)
    name = re.sub(r'-\d+.*$', '', name)
    return name


def fuzzy_match(scan_name: str, job_items):
    """
    Match a scanned barcode against job item SKUs.
    - Direct prefix match if scan starts with SKU
    - Otherwise fuzzy match using RapidFuzz
    """
    scan_clean = normalize_name(scan_name)
    item_names = [normalize_name(i.name) for i in job_items]

    # 1. Direct prefix match (fast + accurate for SKUs like HF-blue-123)
    for original, normalized in zip(job_items, item_names):
        if scan_clean.startswith(normalized):
            return original.name

    # 2. Fallback fuzzy match
    match, score, _ = process.extractOne(scan_clean, item_names, scorer=fuzz.token_sort_ratio)
    if score >= 70:
        index = item_names.index(match)
        return job_items[index].name

    return None
