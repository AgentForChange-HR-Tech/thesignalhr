# The Signal HR: site build guardrails

Read this before changing any page, tool, data file or Briefing. It applies to Alex, to Claude sessions and to scheduled tasks. When a request conflicts with these guardrails, the guardrails win: stop and ask Alex.

## 1. Inform, don't persuade (non-negotiable)

The Signal is objective. It informs readers; it never persuades a person or a company toward or away from a product decision.

- **No product recommendations.** Never tell readers to buy, choose, shortlist, switch to, keep or avoid a specific vendor, product or product category. No "best", "top pick", "winner", "leader", "laggard", "clear choice" or "we recommend" in our own voice.
- **No rankings of vendors.** No overall scores, star ratings or orderings by merit. Lists are alphabetical, or follow the reader's own filters.
- **Tools reflect the reader's criteria, not our verdict.** Finders show which platforms match the filters the reader chose ("Matches all your filters"), never "strong fit" or "best for you". Checks summarize what the reader's answers show and the questions to settle; they don't conclude "buy" or "don't buy".
- **Same treatment for every platform.** Same fields, same depth, same evidence standard. Strengths and limitations sit side by side, and every rating has a stated, published definition.
- **Describe evidence, not conclusions.** Use neutral verbs: documents, offers, requires, has not published, announced. Ratings say what is documented, not what is good.
- **Vendor claims are attributed.** "Vendor X says it was named a Leader by…" is fine; the vendor's claim is not our judgment.
- **"So what" explains implications, not purchases.** The practitioner "so what" in the Briefing and Insights may explain what a change means, what to check and which questions to ask (governance, timing, readiness, contracts). It must not steer readers to or from a product.
- **Regulation is orientation, not legal advice.** Describe what a rule requires and from when; send readers to counsel for decisions.
- **Our own products follow the same rule.** The buyer kits are described plainly; nothing on the site pushes a reader to buy them.

## 2. Independence

- No vendor pays: no sponsorships, affiliate links, paid placement or paid ranking.
- No vendor reviews content before publication. Vendor outreach doesn't change content; only evidence does, and corrections are noted in the change log.

## 3. Evidence and dates

- Every factual claim links to a source page that was actually opened. Vendor-affiliated sources are labeled.
- Separate what is in production from what is announced, in beta or on a roadmap, with dates.
- Use absolute dates ("from December 2, 2027"), never relative ones ("days away", "next month").
- Every material change to a comparison goes in the change log on /compare/#changelog.

## 4. Privacy

- Don't add data collection (forms, cookies, new trackers, new third-party services) without updating /privacy/ first.
- Analytics never carry personal information. Votes, search and tools don't ask who the reader is.

## 5. Build rules

- Where a builder exists, edit the data and the build script, then rebuild; don't hand-edit generated pages:
  - ATS: `python3 -B _tools/ats/build_ats.py compare/ats/index.html compare/ats/index.html`
  - CRM: `python3 -B _tools/crm/build_crm.py compare/ats/index.html compare/crm/index.html`
  - Applicant match: `python3 -B _tools/match/build_match.py compare/ats/index.html compare/match/index.html`
  - Regional radar and calendar: `python3 -B _tools/regional/build_regional.py YYYY-MM-DD`
  - Site-wide scripts in `_tools/site/` are idempotent; rerun them after template changes.
- Tag every Briefing, Insights and Coverage item with a region (see `_tools/regional/README.md`).
- After any content change, rebuild site search: `python3 -B _tools/site/search_index.py`.
- Before committing, run the validators: `python3 -B _tools/verify/verify.py`. Zero errors is required; read every warning.
- Follow the six publishing gates in `_tools/PUBLISHING.md`: sourcing, validators, independent fact-check, risk review, Alex's approval, and corrections and freshness after publishing.
- Commit locally; Alex reviews and pushes. Never push, deploy or change DNS.

## 6. Search

- Results are ordered only by how well they match the reader's words. Never boost or bury a vendor, page or product for any other reason.
