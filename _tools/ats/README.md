# ATS comparison — source

The page at /compare/ats/ is generated. Edit the data, then rebuild.

- `data.py` — every platform, capability rating, AI status, pricing model, implementation range and source. Update `VERIFIED` when you re-check.
- `build_ats.py` — builds the page. Run from the repo root:
  `python3 _tools/ats/build_ats.py compare/ats/index.html compare/ats/index.html`
  (it reuses the page's own header and footer as the template).
- `ats.css`, `ats.js` — page styles and the finder/compare logic, inlined into the page at build time.

Folders starting with an underscore are not published by GitHub Pages (Jekyll), so these files stay private to the repo.
