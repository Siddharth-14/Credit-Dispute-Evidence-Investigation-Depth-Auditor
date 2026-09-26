import json
from pathlib import Path

import streamlit as st

from engine.extractor import extract_claim
from engine.scorer import score_case

DATA_DIR = Path(__file__).parent / "data"

CONFIDENCE_DISPLAY = {
    "high": ("High match confidence", "success"),
    "medium": ("Medium match confidence", "warning"),
    "low": ("Low match confidence", "error"),
}


@st.cache_data
def load_data():
    seed_data = json.loads((DATA_DIR / "seed_cases.json").read_text())
    metro2_reference = json.loads((DATA_DIR / "metro2_reference.json").read_text())
    return seed_data, metro2_reference


st.set_page_config(page_title="Credit Dispute Evidence Auditor", layout="centered")

seed_data, metro2_reference = load_data()
cases = seed_data["cases"]
response_codes = seed_data["furnisher_response_codes"]

st.title("Credit Dispute Evidence & Investigation-Depth Auditor")

st.markdown(
    "On January 17, 2025, the CFPB ordered Equifax to pay **$15M** after finding its "
    "dispute process ignored contradictory evidence and had no system to block "
    "reinsertion of previously deleted errors. This tool is a public-data demo of a "
    "transparent QA layer that could sit *alongside* a real dispute workflow: it scores "
    "how complete a consumer's evidence is, classifies the claim against the public "
    "Metro 2 dispute-code taxonomy, and shows its full reasoning instead of a black-box "
    "score."
)

with st.expander("What this tool is NOT"):
    st.markdown(
        "- **Not** connected to Equifax, any credit bureau, or any real consumer data.\n"
        "- **Not** a debt-validity adjudicator - it doesn't decide who's right.\n"
        "- Built entirely on **synthetic, seeded cases** and a hand-built reference "
        "table - no live backend, no database, no LLM API calls.\n"
        "- A portfolio/demo project, not a production compliance tool."
    )

st.divider()

case_labels = {c["id"]: f"{c['id']} - {c['disputed_item']}" for c in cases}
selected_id = st.selectbox(
    "Pick a seeded dispute case",
    options=list(case_labels.keys()),
    format_func=lambda cid: case_labels[cid],
)
case = next(c for c in cases if c["id"] == selected_id)

st.subheader("Consumer narrative")
st.info(case["narrative"])

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Disputed item:** {case['disputed_item']}")
with col2:
    response_meaning = response_codes.get(case["furnisher_response_code"], "Unknown")
    st.markdown(
        f"**Furnisher response code:** {case['furnisher_response_code']} - {response_meaning}"
    )

st.markdown("**Evidence the consumer says they attached:**")
if case["evidence_attached"]:
    for item in case["evidence_attached"]:
        st.markdown(f"- {item}")
else:
    st.markdown("_None provided (bare-assertion dispute)_")

st.divider()

extracted_claim = extract_claim(case["narrative"], case["disputed_item"])
result = score_case(case, extracted_claim, metro2_reference)

st.subheader("Extracted claim")
label, kind = CONFIDENCE_DISPLAY[extracted_claim["confidence"]]
st.markdown(f"**Claim type:** {extracted_claim['claim_type']}")
if extracted_claim["matched_phrases"]:
    st.markdown(f"**Matched phrases:** {', '.join(extracted_claim['matched_phrases'])}")
getattr(st, kind)(label)

st.subheader("Metro2 classification")
st.markdown(f"**Code {result['metro2_code']}:** {result['metro2_meaning']}")

st.subheader("Evidence completeness score")
st.metric("Score", f"{result['score']} / 100")
st.progress(result["score"] / 100)

if result["reinsertion_risk"]:
    st.warning(f"**Reinsertion risk flagged.** {result['reinsertion_note']}")

with st.expander("Full reasoning trail", expanded=False):
    for i, step in enumerate(result["reasoning_log"], start=1):
        st.markdown(f"{i}. {step}")
