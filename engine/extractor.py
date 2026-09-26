"""Rule-based claim extraction: keyword/phrase matching against a fixed taxonomy.

No ML model, no external API call - just lowercase substring matching against a
hand-built dictionary of phrases typical of each dispute category. This keeps the
tool fully transparent and dependency-free.
"""

TAXONOMY = {
    "account not mine": [
        "never opened",
        "isn't mine",
        "is not mine",
        "not mine",
        "no relationship with",
        "never applied",
        "no idea why",
    ],
    "identity theft": [
        "identity theft",
        "stole my identity",
        "stolen",
        "fraudulent",
        "ftc report",
        "someone opened",
    ],
    "late payment": [
        "late payment",
        "30-day late",
        "days late",
        "was late",
        "posted on time",
        "processing delay",
        "processing issue",
    ],
    "balance incorrect": [
        "balance is wrong",
        "incorrect balance",
        "balance incorrect",
        "owe more than",
        "wrong compared",
        "number on my credit report",
    ],
    "account should be closed": [
        "closed this",
        "asked this lender to close",
        "still showing as open",
        "should be closed",
        "still listed as open",
    ],
    "paid in full/settled": [
        "paid off",
        "paid in full",
        "settled this",
        "settlement agreement",
        "already paid",
    ],
    "duplicate account": [
        "identical entries",
        "duplicate",
        "listed twice",
        "two entries",
        "two identical",
        "same account number",
    ],
}


def extract_claim(narrative: str, disputed_item: str) -> dict:
    """Match narrative text against the taxonomy and return the best-guess claim.

    Returns a dict with claim_type, matched_phrases, and a confidence flag
    (high/medium/low) reflecting how strongly the narrative text itself
    supports the classification, independent of the case's labeled
    disputed_item.
    """
    text = narrative.lower()

    hits_by_category = {}
    for category, phrases in TAXONOMY.items():
        matched = [phrase for phrase in phrases if phrase in text]
        if matched:
            hits_by_category[category] = matched

    if not hits_by_category:
        return {
            "claim_type": disputed_item,
            "matched_phrases": [],
            "confidence": "low",
        }

    best_category = max(hits_by_category, key=lambda c: len(hits_by_category[c]))
    best_matches = hits_by_category[best_category]

    if len(best_matches) >= 2:
        confidence = "high"
    else:
        confidence = "medium"

    return {
        "claim_type": best_category,
        "matched_phrases": best_matches,
        "confidence": confidence,
    }
