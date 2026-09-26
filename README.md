# Credit Dispute Evidence & Investigation-Depth Auditor

A small, transparent tool that scores how complete a consumer's credit-dispute evidence
is, classifies it against the public Metro 2 dispute-code taxonomy, and shows its full
reasoning trail instead of a black-box score.

## Why

On January 17, 2025, the [CFPB ordered Equifax to pay $15M](https://www.consumerfinance.gov/about-us/newsroom/cfpb-orders-equifax-to-pay-15-million-for-mishandling-consumer-disputes/)
after finding that its dispute-investigation process routinely ignored contradictory
evidence submitted by consumers and had no system in place to prevent previously deleted
errors from being reinserted onto credit reports. Consumer dispute volume across the
credit bureaus has also grown sharply in recent years, per the CFPB's own supervisory
reporting on the Furnisher/CRA dispute ecosystem, which puts more pressure on
investigation quality, not less.

This project is a public-data, weekend-scope demonstration of a QA/audit layer that
could sit **alongside** (never replace) a bureau's real dispute-investigation workflow:
given a dispute narrative and the evidence a consumer says they attached, it classifies
the claim against the public [Metro 2 Format](https://www.cdiaonline.org/resources/furnishers-of-data-metro-2-format/)
compliance-condition/dispute-code taxonomy, scores evidence completeness, and shows every
step of that reasoning in plain English.

## What it does

1. Lets you pick from 18 seeded, synthetic dispute cases (strong-evidence cases,
   bare-assertion cases, and repeat/reinsertion cases).
2. Shows the case's narrative, disputed item, and attached evidence.
3. Runs rule-based (keyword/phrase) claim extraction - no ML, no API call - and shows a
   confidence flag (high/medium/low) for the classification.
4. Maps the claim to a Metro 2 dispute/compliance-condition code and the evidence
   categories a genuine investigation of that dispute type would need.
5. Computes a 0-100 evidence-completeness score from how much of that expected evidence
   is present.
6. Shows a full, step-by-step reasoning trail: what was checked, what's missing, and why
   the score landed where it did.
7. Flags **reinsertion risk** when a case shows the same item was previously disputed and
   came back "verified, no change" - directly referencing the gap the CFPB's Equifax order
   identified.

## What it explicitly does NOT do

- It is **not** connected to Equifax, any credit bureau, or any real consumer data or
  system.
- It does **not** adjudicate debt validity or decide who is "right" in a dispute.
- It makes **no live backend calls, uses no database, and calls no hosted LLM API** -
  everything runs on static seed data bundled in the repo, using plain Python string
  matching against a hand-built taxonomy.
- It is a portfolio/demo project, not a production compliance or legal tool.

## Repo structure

```
credit-dispute-auditor/
  app.py                      # Streamlit entrypoint
  data/
    seed_cases.json           # 18 seeded, synthetic dispute cases
    metro2_reference.json     # public Metro2 dispute/reason-code reference table
  engine/
    extractor.py              # rule-based claim extraction
    scorer.py                 # evidence-completeness scoring + reasoning trail
  requirements.txt
  README.md
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Deploy to Streamlit Community Cloud (free)

1. Push this repo to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, point it at this repo, branch `main`, main file path `app.py`.
4. Click **Deploy**.
5. Once it's live, confirm the dropdown works and that all 18 seeded cases render a
   complete result with no errors.
