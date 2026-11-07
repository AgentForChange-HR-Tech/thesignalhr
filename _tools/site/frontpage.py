"""Front page builder (November 2026). Run from the repo root after the Briefing, Coverage, Insights or a
comparison changes (the weekly writer runs it after build_regional.py):
    python3 -B _tools/site/frontpage.py
Rebuilds the <main> of index.html from the live pages, so the home page can't drift from them:
- "This week": the current Briefing's signals. Each <article class="brief-item"> may carry data-short="…", a short
  headline written by the writer and checked by the fact-checker; without it the full headline is used.
- Comparisons and checks: platform and place counts read from the comparison pages' own data.
- Longer reads: the three newest Insights. Ten domains: each Coverage domain's current signal, first sentence.
Styles: frontpage.css (managed block in assets/site.css). Signup form: signup_form.html (see signup.py).
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape

def read(p): return open(p, encoding="utf-8").read()
def text(s): return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()
def data(p):
    m = re.search(r'<script type="application/json" id="ats-data">(.*?)</script>', read(p), flags=re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))
def managed(s, name, body):
    start, end = f"/* >>> {name} (managed by _tools/site/frontpage.py) */", f"/* <<< {name} */"
    block = f"{start}\n{body}\n{end}"
    m = re.search(re.escape(f"/* >>> {name} ") + r".*?" + re.escape(end), s, flags=re.S)
    return s[:m.start()] + block + s[m.end():] if m else s.rstrip("\n") + "\n\n" + block + "\n"

FORM = open(os.path.join(HERE, "signup_form.html"), encoding="utf-8").read().strip("\n")
def form(fid, placement, indent):
    return "\n".join(indent + l for l in FORM.format(id=fid, placement=placement).split("\n")).lstrip()

# ---------------------------------------------------------------- this week (the Briefing)
brief = read("briefing/index.html")
week = re.search(r"Week of ([A-Z][a-z]+ \d{1,2}, \d{4})", brief).group(1)
updated = re.search(r"Updated ([A-Z][a-z]+ \d{1,2}, \d{4})", brief).group(1)
DOT = {"product": "#5c96ee", "market": "#3db3a5", "talent": "#b39ddb", "workforce": "#e0a34e", "risk": "#e57a63",
       "regulation": "#f2c14e", "pay": "#f2c14e", "immigration": "#7fc8a9", "skills": "#9dbff5", "analytics": "#3db3a5"}
REG = {"global": "Global", "americas": "Americas", "emea": "EMEA", "apac": "APAC"}
rows, regions = [], set()
for i, m in enumerate(re.finditer(r'<article class="brief-item"([^>]*)>(.*?)</article>', brief, flags=re.S), 1):
    attrs, body = m.group(1), m.group(2)
    reg = (re.search(r'data-region="([^"]*)"', attrs) or [None, "global"])[1].split()
    regions.update(reg)
    short = re.search(r'data-short="([^"]*)"', attrs)
    tag = text(re.search(r'<span class="tag[^"]*"[^>]*>(.*?)</span>', body, flags=re.S).group(1))
    head = short.group(1) if short else E(text(re.search(r"<h[23][^>]*>(.*?)</h[23]>", body, flags=re.S).group(1)))
    where = " · ".join(REG.get(r, r.title()) for r in reg)
    rows.append(f'          <li><a href="/briefing/#signal-{i}"><span class="fp-num">{i:02d}</span>'
                f'<span class="fp-meta"><i style="background:{DOT.get(tag.lower(), "#8f94a3")}"></i>{E(tag)} · {where}</span>'
                f"<h3>{head}</h3></a></li>")
if not rows:
    sys.exit("no Briefing signals found")
NUM = ["No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
count = NUM[len(rows)] if len(rows) < len(NUM) else str(len(rows))
where_all = " · ".join(REG[r] for r in ("global", "americas", "emea", "apac") if r in regions)

# ---------------------------------------------------------------- comparisons (counts from the pages' own data)
ats, crm, match = (data(f"compare/{n}/index.html") for n in ("ats", "crm", "match"))
places = len(match["juris"])
countries = len([j for j in match["juris"] if not j.get("parent") and j["id"] != "eu"])
reviewed = match.get("verified") or "October 2026"
checked = match.get("checked")
reviewed_line = f"Reviewed {reviewed}" + (f"; checked for changes {checked}" if checked else "")

# ---------------------------------------------------------------- longer reads (newest three Insights)
reads = []
for u, c in re.findall(r'<a[^>]+href="(/insights/[^"]+/)"[^>]*>(.*?)</a>', read("insights/index.html"), flags=re.S)[:3]:
    parts = [p.strip() for p in re.split(r"\s*\|\s*", html.unescape(re.sub(r"\s+", " ", re.sub("<[^>]+>", " | ", c)))) if p.strip()]
    tag, region, title, dek, meta = parts[:5]
    reads.append(f'        <a class="fp-read" href="{u}"><span class="fp-label">{E(tag)} · {E(region)} · {E(meta.split(" · ")[0])}</span>'
                 f"<h3>{E(title)}</h3><p>{E(dek)}</p></a>")

# ---------------------------------------------------------------- ten domains (Coverage current signals)
doms = []
for did, body in re.findall(r'<article class="card" id="([^"]+)"[^>]*>(.*?)</article>', read("coverage/index.html"), flags=re.S):
    name = text(re.search(r'<span class="tag tag-[^"]*">(.*?)</span>', body).group(1))
    m = re.search(r"Current signal · </strong>(.*?)(?:<span class=\"sig-src\"|</div>)", body, flags=re.S)
    first = re.split(r"(?<=[a-z0-9\)])\. (?=[A-Z])", text(m.group(1)))[0].rstrip(".") if m else ""
    doms.append(f'        <a class="fp-domain" href="/coverage/#{did}"><strong>{E(name)}</strong><span>{E(first)}</span></a>')
cov_updated = re.search(r"Updated ([A-Z][a-z]+ \d{1,2}, \d{4})", read("coverage/index.html")).group(1)

MAIN = f"""<main id="main">
  <div class="fp-edition"><div class="wrap"><span><b>The Briefing</b> · Week of {week}</span><span>{count} signals · {where_all}</span><span>Updated {updated}</span></div></div>

  <section class="fp-hero">
    <div class="wrap fp-hero-grid">
      <div>
        <span class="fp-eyebrow">Independent HR intelligence</span>
        <h1>The AI shift in HR, filtered for the people who have to <em>lead it</em>.</h1>
        <p class="fp-lede">One practitioner's weekly read on HR technology, AI and regulation: what changed, what it may mean, and what to check, with every source linked.</p>
        {form("sub-top", "hero", "        ")}
        <div class="fp-standards"><span>Every claim sourced</span><span>Every page dated</span><span>No vendor pays</span><span>AI-assisted, reviewed by Alex Rivera</span><a href="/about/#method">How it's made →</a></div>
      </div>
      <aside class="fp-week" aria-label="This week's signals">
        <div class="fp-week-head"><h2>This week</h2><span>Week of {week}</span></div>
        <ol>
{chr(10).join(rows)}
        </ol>
        <div class="fp-week-foot"><a href="/briefing/">Read the Briefing →</a><span>About a five-minute read · <a href="/briefing/archive/">Archive</a></span></div>
      </aside>
    </div>
  </section>

  <section class="fp-sec">
    <div class="wrap">
      <div class="fp-sec-head"><div><h2>Comparisons and checks</h2><p>Built from each vendor's documentation and the rules themselves, with every claim sourced and dated. {E(reviewed_line)}.</p></div><a href="/compare/">All comparisons →</a></div>
      <div class="fp-tools">
        <a class="fp-tool" href="/compare/ats/"><b>{len(ats["p"])}</b><strong>ATS platforms</strong><p>From standalone ATS to HCM-suite recruiting. Filter to your situation, compare up to three side by side, and see what tends to set a go-live date.</p><em>Open the comparison →</em></a>
        <a class="fp-tool" href="/compare/crm/"><b>{len(crm["p"])}</b><strong>Recruiting CRMs</strong><p>From the CRM inside your ATS or suite to standalone platforms, with a check on whether a separate CRM adds anything for you.</p><em>Open the comparison →</em></a>
        <a class="fp-tool" href="/compare/match/"><b>{places}</b><strong>Places with hiring-AI rules</strong><p>{countries} countries and the EU, down to US states and EU member countries, alongside {len(match["p"])} tools that score or rank applicants.</p><em>Check the rules →</em></a>
      </div>
      <p class="fp-next">Next: HRIS / HCM, in progress. Payroll and L&amp;D are planned, and subscribers vote on the order. Working files for a selection are in development as <a href="/kits/">buyer kits</a>.</p>
    </div>
  </section>

  <section class="fp-sec">
    <div class="wrap">
      <div class="fp-sec-head"><div><h2>Longer reads</h2><p>Analysis of regulation, operating models and the vendor market, each with its sources.</p></div><a href="/insights/">All Insights →</a></div>
      <div class="fp-reads">
{chr(10).join(reads)}
      </div>
    </div>
  </section>

  <section class="fp-sec">
    <div class="wrap">
      <div class="fp-sec-head"><div><h2>Ten domains, tracked weekly</h2><p>The current signal in each area HR teams are working through. Updated {cov_updated}.</p></div><a href="/coverage/">All coverage →</a></div>
      <div class="fp-domains">
{chr(10).join(doms)}
      </div>
    </div>
  </section>

  <section class="fp-sec">
    <div class="wrap fp-about">
      <div>
        <span class="fp-eyebrow">Behind the signal</span>
        <h2 style="margin-top:.7rem">Curated by a practitioner, for practitioners.</h2>
        <p>The Signal is curated by <strong>Alex Rivera</strong>, a practitioner in enterprise HR technology: running migrations, fixing broken implementations, and advising on HR systems and AI strategy. It's one practitioner's read, with the sources linked so you can check them and draw your own conclusions.</p>
        <div class="fp-links"><a href="/about/">About the curator →</a><a href="https://www.linkedin.com/in/alexrivera1/" target="_blank" rel="noopener">LinkedIn →</a></div>
      </div>
      <ol class="fp-steps">
        <li><div><strong>Sourced</strong><span>Primary sources first: the law or regulator, the vendor's own documentation, the original study.</span></div></li>
        <li><div><strong>Checked</strong><span>Automated checks, then a separate source-by-source fact-check of every claim.</span></div></li>
        <li><div><strong>Approved</strong><span>AI helps with research and drafting; Alex reviews and approves every update before it's published.</span></div></li>
        <li><div><strong>Corrected in the open</strong><span>Errors get a dated note and a change-log entry. No vendor pays, and none reviews content first.</span></div></li>
      </ol>
    </div>
  </section>

  <section class="fp-close">
    <div class="wrap">
      <div><h2>Get the signal each week.</h2><p>What changed in HR tech, what it may mean, and what to check. Free.</p></div>
      {form("sub-bottom", "close", "      ")}
    </div>
  </section>
</main>"""

s = read("index.html")
new = s[:s.index('<main id="main">')] + MAIN + s[s.index("</main>") + len("</main>"):]
changed = []
if new != s:
    open("index.html", "w", encoding="utf-8", newline="").write(new)
    changed.append("index.html")
css = read("assets/site.css")
css2 = managed(css, "frontpage", open(os.path.join(HERE, "frontpage.css"), encoding="utf-8").read().strip("\n"))
if css2 != css:
    open("assets/site.css", "w", encoding="utf-8", newline="").write(css2)
    changed.append("assets/site.css")
print(f"front page: {len(rows)} signals, {len(reads)} reads, {len(doms)} domains; {len(changed)} files changed", *changed)
