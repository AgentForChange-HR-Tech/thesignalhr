# Recruiting CRM comparison — source

The page at /compare/crm/ is generated. Edit the data, then rebuild.

- `data.py` — every platform, capability rating, ATS integration, AI status, pricing model, delivery model, implementation note and source, plus the "Do you need a separate CRM?" check (`GROUPS`, `FACTORS`, `NEED_CAPS`) and the RFP bank. Update `VERIFIED` when you re-check.
- `build_crm.py` — builds the page. Run from the repo root, after any ATS rebuild:
  `python3 -B _tools/crm/build_crm.py compare/ats/index.html compare/crm/index.html`
  (the ATS page is only used as a template for the site header and footer).
- `crm.css`, `crm.js` — page styles and the check, finder and compare logic, inlined at build time.

Conventions shared with `_tools/ats`: no implementation timeline estimates, pricing model only (no dollar figures), AI split into "in production" versus announced/beta/roadmap with dates, ATS integrations listed only when documented on a marketplace, partner or help page, and AI certification rated 2 = independent certification, 1 = published independent bias audit or narrower-scope certification, 0 = none found.

Folders starting with an underscore are not published by GitHub Pages (Jekyll), so these files stay private to the repo.
