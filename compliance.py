from typing import List

BANNED_CLAIMS = ["guaranteed", "100% uptime", "unlimited" ]

MANDATORY_CLAUSES = [
    "Pricing valid for 30 days from date of issue.",
    "Taxes extra as applicable.",
    "Payment terms: 50% advance, 50% on delivery (sample)."
]

def check_claims(text: str) -> List[str]:
    hits = []
    low = text.lower()
    for w in BANNED_CLAIMS:
        if w in low:
            hits.append(w)
    return hits

def mandatory_clauses() -> List[str]:
    return MANDATORY_CLAUSES.copy()
