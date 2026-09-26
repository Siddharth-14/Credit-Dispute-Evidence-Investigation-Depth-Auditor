"""Evidence-completeness scoring and reasoning trail generation.

Cross-references an extracted claim against the public Metro 2 reference
table to determine the applicable dispute code, what evidence a genuine
investigation of that dispute type would need, and how much of that
evidence the consumer actually attached. Every step is logged in plain
English so the score is never a black box.
"""

FALLBACK_CODE = "XR"


def _find_code(claim_type: str, disputed_item: str, metro2_reference: dict) -> dict:
    codes = metro2_reference["codes"]
    for code in codes:
        if claim_type in code["typical_dispute_types"]:
            return code
    for code in codes:
        if disputed_item in code["typical_dispute_types"]:
            return code
    for code in codes:
        if code["code"] == FALLBACK_CODE:
            return code
    return codes[0]


def score_case(case: dict, extracted_claim: dict, metro2_reference: dict) -> dict:
    claim_type = extracted_claim["claim_type"]
    disputed_item = case["disputed_item"]
    evidence_attached = case.get("evidence_attached", [])

    reasoning_log = []

    if extracted_claim["matched_phrases"]:
        reasoning_log.append(
            f"Classified dispute as '{claim_type}' based on narrative phrases: "
            f"{extracted_claim['matched_phrases']}."
        )
    else:
        reasoning_log.append(
            f"No strong narrative phrases matched the taxonomy; falling back to the "
            f"case's labeled disputed item, '{claim_type}'."
        )
    reasoning_log.append(f"Extraction confidence: {extracted_claim['confidence']}.")

    metro2_code = _find_code(claim_type, disputed_item, metro2_reference)
    reasoning_log.append(
        f"Mapped claim type '{claim_type}' to Metro2 code {metro2_code['code']} "
        f"({metro2_code['meaning']})."
    )

    expected_evidence = metro2_code["expected_evidence"]
    reasoning_log.append(
        f"A genuine investigation of this dispute type typically expects: "
        f"{', '.join(expected_evidence)}."
    )

    present_evidence = [e for e in expected_evidence if e in evidence_attached]
    missing_evidence = [e for e in expected_evidence if e not in present_evidence]

    if evidence_attached:
        reasoning_log.append(f"Evidence on file: {', '.join(evidence_attached)}.")
    else:
        reasoning_log.append("No evidence was attached - this is a bare-assertion dispute.")

    if present_evidence:
        reasoning_log.append(f"Matched against expected evidence: {', '.join(present_evidence)}.")
    if missing_evidence:
        reasoning_log.append(f"Missing expected evidence: {', '.join(missing_evidence)}.")

    if expected_evidence:
        raw_score = round(100 * len(present_evidence) / len(expected_evidence))
    else:
        raw_score = 100

    if not evidence_attached:
        score = min(raw_score, 5)
        reasoning_log.append(
            f"Score capped at {score}/100 for a bare-assertion dispute with no supporting "
            f"documentation."
        )
    else:
        score = raw_score
        reasoning_log.append(
            f"Score: {score}/100 - {len(present_evidence)} of {len(expected_evidence)} "
            f"expected evidence categories present."
        )

    prior_dispute = case.get("prior_dispute")
    reinsertion_risk = bool(
        prior_dispute
        and prior_dispute.get("disputed_same_item")
        and prior_dispute.get("prior_outcome") == "no change"
    )
    reinsertion_note = None
    if reinsertion_risk:
        reinsertion_note = (
            "This same item was previously disputed and came back 'verified, no change.' "
            "Reporting it again unchanged, without a system to flag repeat/reinsertion "
            "disputes, is exactly the gap the CFPB's January 2025 order against Equifax "
            "identified: no process existed to catch reinsertion of previously disputed "
            "errors or to weigh contradictory evidence across dispute cycles."
        )
        reasoning_log.append(reinsertion_note)

    return {
        "metro2_code": metro2_code["code"],
        "metro2_meaning": metro2_code["meaning"],
        "expected_evidence": expected_evidence,
        "present_evidence": present_evidence,
        "missing_evidence": missing_evidence,
        "score": score,
        "reasoning_log": reasoning_log,
        "reinsertion_risk": reinsertion_risk,
        "reinsertion_note": reinsertion_note,
    }
