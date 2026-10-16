# Regional coverage — source

Regions used across the site: `americas`, `emea`, `apac`, `global` (Global items show under every region).

- `regional.py` — the regional calendar (dated effective dates and deadlines) and the regional radar (current developments by region), each with sources. Update `UPDATED` when you re-check.
- `build_regional.py` — injects the radar and calendar into `coverage/index.html` and the next six dates into `briefing/index.html` (between the `<!-- regional:… -->` markers). Run from the repo root with today's date:
  `python3 -B _tools/regional/build_regional.py 2026-10-16`
  Past dates drop off automatically.
- `articles.py`, `build_articles.py` — the three October 2026 regional insight articles. `build_articles.py` wraps them in the site template:
  `python3 -B _tools/regional/build_articles.py insights/eu-ai-act-hr-deadline/index.html`

## Tagging new content (weekly Briefing and new Insights)

- Briefing items: `<article class="brief-item" data-region="americas">` and, in the first column,
  `<div class="b-meta"><span class="tag … b-tag">Topic</span><span class="region-tag">Americas</span></div>`.
  Use more than one region separated by spaces (`data-region="americas emea"`) and `global` for items that apply everywhere.
- Insight cards: `data-region="…"` on the `<a class="card">` and the region tag next to the topic tag.
- Each page with a filter needs the region bar (copy it from `briefing/index.html`); the behavior lives in `assets/site.js` and the styles in `assets/site.css`.
- Aim for at least one EMEA and one APAC item in each weekly edition.
