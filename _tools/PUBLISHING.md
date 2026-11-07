# The Signal HR: publishing pipeline

Nothing reaches thesignalhr.com without passing six gates. The standard is simple: **if a claim can't be verified, it doesn't run. When in doubt, leave it out.** No process makes errors impossible; this one is built so they are rare, caught before publishing, and corrected in the open when they slip through.

Read with `_tools/GUARDRAILS.md`. Where they differ, the stricter rule wins.

**Working files stay private.** Candidates, claims ledgers, reviews and audits live in the `editorial/` folder next to the repo (`The Signal - HR Transformation/editorial/`), not in the public repo.

## Who does what

| Role | Who | When | Can it change the site? |
| --- | --- | --- | --- |
| Scout (identify) | Scheduled task "Signal HR scout" | Thursdays | No. Writes candidates to `editorial/candidates/` |
| Writer (produce) | Scheduled task "Weekly signal briefing refresh" | Mondays, morning | Drafts the Briefing locally and writes a claims ledger |
| Fact-checker (validate) | Scheduled task "Signal HR fact-check", a separate session with no memory of the draft | Mondays, after the writer | Only to correct a figure, date or name that its cited source clearly contradicts; every change logged |
| Validators | `python3 -B _tools/verify/verify.py` | Every run, by every role | No. Errors block publishing |
| Freshness auditor | Scheduled task "Signal HR freshness audit" | Monthly | No. Writes a report with proposed updates |
| Editor-in-chief (approve) | Alex | Before every push | Yes. Only Alex pushes; nothing publishes itself |

## The six gates

### Gate 1: Sourcing (scout, writer)

Every factual claim needs a source page that was actually opened. Use the tiers in `_tools/verify/SOURCES.md`:

- **Tier A (primary):** the law, regulator, court record or official gazette; government statistics; a company's own filing, release notes or announcement (for what that company says about itself).
- **Tier B (independent secondary):** established law firms' client alerts; established news and trade press with named reporters.
- **Tier C (context only):** vendor marketing, analyst summaries, blogs, social posts. Never the only support for a claim.

Rules:
- Laws, effective dates, fines and legal status: Tier A, or two Tier B sources that agree.
- Numbers: the original study or report, not a write-up of it.
- Vendor capabilities: the vendor's own documentation, attributed ("Workday says"), with production separated from announced, beta or roadmap.
- Claims supported only by Tier C are cut.
- The writer records every claim in `editorial/claims/YYYY-MM-DD.md`: claim, exact figure or date, source URL, tier, and where in the source it appears.

### Gate 2: Automated validators

`verify.py` must report **0 errors**. It checks structure and links, that every signal, profile and rule cites a source, guardrail and voice language, the cookie-consent loader and self-hosted fonts, stale or passed dates, numbers quoted across pages, the watchlist, employer and placeholder references, and the search index. Warnings are read and either fixed or explained in the review.

### Gate 3: Independent fact-check

A fresh session with no stake in the draft opens every source and checks every claim in the ledger and on the page: figures, dates, names, titles, quotes and legal status. Each claim is marked **Verified**, **Corrected** (text changed to match the cited source exactly, before and after recorded) or **Cut recommended** (unsupported, or Tier C only). Headlines must be supported by their body and sources. The verdict goes to `editorial/reviews/YYYY-MM-DD.md`: PASS, PASS WITH CORRECTIONS, or FAIL.

### Gate 4: Guardrails and risk review (part of the fact-check)

- **Inform, don't persuade** (GUARDRAILS section 1).
- **Voice** (GUARDRAILS section 2): practitioner to practitioner. No superlatives about The Signal, no swipes at other sites or vendors, no orders to readers, analysis framed as what a change may mean, limits named, and AI use described accurately.
- **Named companies:** only facts from cited sources, attributed and in neutral words. Never characterize a company's intent. "Illegal", "violates", "fraud" and similar appear only when quoting a court or regulator's decision.
- **Litigation:** complaints are described as allegations ("the complaint alleges"), from the docket or a Tier B report, and updated when outcomes change.
- **Analysis is labeled.** The "So what" is analysis; facts and analysis don't blur.
- **Quotes** are exact and linked. Reader quotes need the reader's written permission.
- **Legal and immigration topics** are orientation, not advice, with absolute dates.
- **No employer references.** Nothing about Alex's current or past employers, and no non-public information from any of them. `verify.py` blocks any term listed in `_tools/verify/private-terms.txt` (kept on Alex's computer, never committed).
- **Copyright:** short quotes with attribution only; no images without a license.
- **Privacy:** no personal information about private individuals.

### Gate 5: Editor approval

Alex reads the review file (a few minutes: verdict, corrections, open questions) and pushes only when satisfied. A FAIL is never pushed.

### Gate 6: After publishing

- **Corrections:** fix a verified error promptly, add a dated note on the page and an entry in the change log. Never silently edit facts.
- **Freshness:** the monthly audit re-verifies watchlist items as they come due (`_tools/verify/watchlist.json`) and a rotating third of the comparisons each month, so every profile is re-verified at least quarterly.
- **Watchlist:** every time-sensitive fact (a pending bill, a court stay, a "from" date) goes on the watchlist with a recheck date when it's published.

## Finding the latest updates in each domain

The scout works through the ten domains with the sources in `SOURCES.md`: regulators and legislatures for every place in the rules check, vendors' own release notes and newsrooms for every platform in the comparisons, government labor statistics, and court dockets for tracked cases. It also checks every watchlist item due in the next 14 days. Candidates carry their sources and a confidence note; the writer chooses, the fact-checker verifies, Alex approves.
