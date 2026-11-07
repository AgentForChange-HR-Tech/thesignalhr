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

## 2. Voice: practitioner to practitioner

The Signal is one practitioner sharing a resource with other practitioners. It isn't the final authority on any of this, and it should never read as a know-it-all.

- **Offer, don't pronounce.** State facts plainly with their source. Frame analysis as what a change may mean and what to check ("may", "can", "worth checking", "one question to ask"), not as certainty or orders.
- **No superlatives about ourselves.** Never "the most reliable", "the definitive", "the authority", "the benchmark", "everything you need" or "zero mistakes". Show reliability with sources, dates, review steps and corrections instead of claiming it.
- **Don't put others down.** No swipes at other sites, analysts, vendors or readers ("affiliate pages in disguise", "vendor theater", "chatbots in a trench coat", "what most people get wrong"). Describe what we do, not what others get wrong.
- **Readers are peers.** Don't tell readers what they need or must do, and don't promise outcomes ("decisions you can't get wrong", "walk in already knowing", "sound informed"). Many readers know their own systems, rules and organizations better than we do.
- **Name the limits.** Say what isn't known, what's unclear or disputed, and where a reader's counsel, team or vendor will know more. The "so what" is one practitioner's read, labeled as analysis.
- **Credentials, stated plainly.** Alex's experience is described as fact ("a practitioner in enterprise HR technology"), without a number of years, never as a trump card ("someone who has actually done it").
- **Invite correction and context.** Make it easy to point out errors or add a different view, and log corrections in the open.
- **Be open about AI.** AI tools help with research, drafting and source checks; the About page (/about/#ai) says how, bylines carry an "AI-assisted" link, and Alex approves every update before it's published. Never claim the site is made without AI ("not an algorithm", "human-written"), and update the About page when the process changes.
- Neutral instructions inside tools are fine ("Pick the countries where you hire"). Telling readers how to run their organization is not.

## 3. Independence

- No vendor pays: no sponsorships, affiliate links, paid placement or paid ranking.
- No vendor reviews content before publication. Vendor outreach doesn't change content; only evidence does, and corrections are noted in the change log.

## 4. Evidence and dates

- Every factual claim links to a source page that was actually opened. Vendor-affiliated sources are labeled.
- Separate what is in production from what is announced, in beta or on a roadmap, with dates.
- Use absolute dates ("from December 2, 2027"), never relative ones ("days away", "next month").
- Every material change to a comparison goes in the change log on /compare/#changelog.

## 5. Privacy

- Don't add data collection (forms, cookies, new trackers, new third-party services) without updating /privacy/ first.
- Analytics never carry personal information. Votes, search and tools don't ask who the reader is.
- **Analytics only with consent where it's required.** Pages load Google Analytics only through the consent loader that `_tools/site/consent.py` installs: off until the visitor allows it in opt-in places (Europe, Brazil, Canada's Eastern time zone, unknown time zones), a one-time notice elsewhere, and off whenever the browser sends Global Privacy Control or Do Not Track. Never paste a raw analytics tag into a page; `verify.py` blocks it. New pages: rerun `consent.py`.
- **No third-party requests that aren't needed.** Fonts are self-hosted in `/assets/fonts/`; don't add Google Fonts or other CDNs.
- The consent setup is orientation, not legal advice. Changes to it go through Alex and, where needed, counsel.

## 6. Build rules

- Where a builder exists, edit the data and the build script, then rebuild; don't hand-edit generated pages:
  - ATS: `python3 -B _tools/ats/build_ats.py compare/ats/index.html compare/ats/index.html`
  - CRM: `python3 -B _tools/crm/build_crm.py compare/ats/index.html compare/crm/index.html`
  - Applicant match: `python3 -B _tools/match/build_match.py compare/ats/index.html compare/match/index.html`
  - Regional radar and calendar: `python3 -B _tools/regional/build_regional.py YYYY-MM-DD`
  - Cookie consent, footer link and self-hosted fonts: `python3 -B _tools/site/consent.py` (rerun after adding a page).
  - Site-wide scripts in `_tools/site/` are idempotent; rerun them after template changes.
- Tag every Briefing, Insights and Coverage item with a region (see `_tools/regional/README.md`).
- After any content change, rebuild site search: `python3 -B _tools/site/search_index.py`.
- Before committing, run the validators: `python3 -B _tools/verify/verify.py`. Zero errors is required; read every warning.
- Follow the six publishing gates in `_tools/PUBLISHING.md`: sourcing, validators, independent fact-check, risk review, Alex's approval, and corrections and freshness after publishing.
- Commit locally; Alex reviews and pushes. Never push, deploy or change DNS.

## 7. Search

- Results are ordered only by how well they match the reader's words. Never boost or bury a vendor, page or product for any other reason.
