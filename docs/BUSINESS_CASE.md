# Business case: InvestigatorAI + GuardianAI

**Fraud screening and investigation for banks, credit unions and payment companies.**

## Who buys this

The buyer is the head of fraud operations or the BSA/AML officer at a mid-sized bank, credit union, fintech or payment processor. That person is responsible for two numbers: how many risky payments get through, and how many analyst hours go into each case before a Suspicious Activity Report (SAR) is filed or the case is closed. The day-to-day users are fraud analysts and investigators.

## The problem and what it costs

Financial crime compliance is expensive, and the cost keeps rising. A Forrester study commissioned by LexisNexis Risk Solutions put the annual cost of financial crime compliance in the US and Canada at **US$61 billion**. It found that costs had risen at **99%** of institutions, and that **70%** planned to prioritise cutting compliance costs in the next 12 months ([LexisNexis Risk Solutions, Feb 2024](https://risk.lexisnexis.com/about-us/press-room/press-release/20240221-true-cost-of-compliance-us-ca)).

Most of that cost is analyst time. FinCEN's official paperwork estimate is **1.98 hours per SAR**, but that figure leaves out alert review and turning alerts into cases. The Bank Policy Institute surveyed 15 banks with at least $100 billion in assets and estimated **21.41 hours of SAR-related work per SAR filed** ([BPI comment letter to FinCEN, April 2024](https://bpi.com/wp-content/uploads/2024/04/BPI-Comment-Letter-FinCEN-SAR-PRA-Notice-4.12.24.pdf)). FinCEN's own 2020 model assumes that only about 42% of cases become SAR filings, and that a written rationale is still needed for every case that is closed without one ([Federal Register, May 2020](https://www.federalregister.gov/documents/2020/05/26/2020-11247/agency-information-collection-activities-proposed-renewal-comment-request-renewal-without-change-of)).

The work also pulls in two directions. Screening has to answer in milliseconds for every payment. Investigation needs research, regulations and a written report. Putting an LLM on every payment is too slow and too expensive. Rules alone can't write a case narrative.

## How the repo solves it

| Need | What in the repo does it |
|---|---|
| Score every transaction fast and explain why | GuardianAI screening in `api/guardian/`: four lightweight agents (an IsolationForest plus transaction rules, a behavioural nearest-neighbour fraud rate, pattern checks for card testing, night-time and geography, and a weighted decision). No LLM call, about 10 ms per transaction in local runs. |
| Send only the risky ones to people | Thresholds approve, review or escalate. Escalated cases arrive at the investigation stage with the form already filled in. |
| Do the research an analyst does by hand | The LangGraph multi-agent investigation in `api/agents/`: regulatory research over a Qdrant index of regulatory PDFs (hybrid BM25 plus dense retrieval, with Cohere reranking), web and academic search, evidence collection and a compliance check. |
| Produce something reviewable | A written report with a SAR recommendation, streamed to the UI (`/investigate/stream`) and downloadable (`/download/{investigation_id}`). |
| Prove the retrieval is good enough | RAGAS evaluation of the retrieval path, in `notebooks/` and `rag/`. |

## Use-case scenarios

All of these organisations are fictional.

1. **A regional credit union with a three-person fraud team.** Card-not-present fraud alerts arrive in batches overnight. GuardianAI approves the clearly normal ones and escalates the rest. Each escalated case opens with the similar historical transactions and the matching regulations already attached, so the morning shift starts at "decide and write" instead of "gather".
2. **A payment processor serving small merchants.** A new merchant shows a burst of small authorisations, a classic card-testing pattern. The pattern agent flags it at screening time. The investigation agent pulls the relevant card-network and regulatory guidance and drafts the narrative the processor needs for its sponsor bank.
3. **A digital bank's quality-assurance group.** QA re-runs a sample of closed cases through the investigation stage and compares the drafted rationale with the analyst's. Disagreements show where procedures are unclear or where the model needs tighter prompts.

## ROI: a worked model (illustrative)

These figures are **illustrative assumptions**, not measurements. Replace them with your own volumes and timings.

| Input | Value | Basis |
|---|---|---|
| Cases worked per year | 2,000 | Assumption for a mid-sized institution |
| Analyst hours per case today | 6 | Assumption. It sits between FinCEN's 1.98 h per SAR and BPI's 21.41 h per SAR, both sourced above. |
| Share of those hours spent gathering evidence and research | 50% | Assumption |
| Reduction in gathering time with drafted, pre-researched cases | 40% | Assumption, to be measured in a pilot |
| Analyst hourly cost | US$49 | BLS May 2024 median for compliance officers is $78,420 a year, about $37.70 an hour ([BLS](https://www.bls.gov/ooh/business-and-financial/compliance-officers.htm)). Multiplied by an assumed 1.3 for benefits and overhead. |

Hours saved = 2,000 × 6 × 50% × 40% = **4,800 hours a year**, worth about **US$235,000** at $49 an hour. Against that, budget for LLM and search API calls, hosting, and a model-risk review before go-live. The case holds if those costs come in well under the hours saved, and the pilot should show that with real numbers. Screening adds a second benefit (fewer false escalations reaching people), but it is not counted here because it depends entirely on your current rules.

## Path to production

1. **Shadow mode.** Run screening and investigation beside the current process on historical, de-identified cases. Measure precision and recall at the escalate threshold, and the time an analyst takes to accept or edit the draft.
2. **Data integration.** Replace the demo transaction set with the core banking or processor feed, and replace the sample regulations with the institution's own procedures and the current regulatory library.
3. **Controls.** Add authentication, case-level audit logs, PII handling and model documentation that meets the institution's model risk management policy. Keep a human as the decision-maker on every SAR.
4. **Pilot** with one team and one fraud type, with an agreed metric (hours per case, and the analyst's edit rate on drafts).

`PRODUCTIONIZING.md` in this repo lists the engineering work.

## Risks and limits

- The screening models are trained on demo data. Thresholds and features must be re-fitted on the institution's own history before they mean anything.
- LLM output can be wrong or incomplete. The report is a draft for an analyst, not a filing, and regulators expect a human decision.
- Sending case data to hosted LLM and search APIs may not be allowed. A private model deployment may be needed.
- The time-saving figures in the main README are design targets. This document doesn't rely on them, and only a pilot can confirm them.

## Sources

- LexisNexis Risk Solutions / Forrester, *True Cost of Financial Crime Compliance – US and Canada* (Feb 2024): https://risk.lexisnexis.com/about-us/press-room/press-release/20240221-true-cost-of-compliance-us-ca
- Bank Policy Institute, comment letter to FinCEN on SAR burden (Apr 2024): https://bpi.com/wp-content/uploads/2024/04/BPI-Comment-Letter-FinCEN-SAR-PRA-Notice-4.12.24.pdf
- FinCEN SAR renewal notice, Federal Register (May 26, 2020): https://www.federalregister.gov/documents/2020/05/26/2020-11247/agency-information-collection-activities-proposed-renewal-comment-request-renewal-without-change-of
- U.S. Bureau of Labor Statistics, Compliance Officers: https://www.bls.gov/ooh/business-and-financial/compliance-officers.htm and OEWS May 2024: https://www.bls.gov/news.release/archives/ocwage_04022025.pdf
