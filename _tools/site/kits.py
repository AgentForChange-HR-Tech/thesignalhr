"""Buyer kits page and the "Pro" wording swap. Run from the repo root:
    python3 -B _tools/site/kits.py
Idempotent. Builds /kits/ from the About page's header and footer; replaces "when Pro launches"
wording across the site with a link to /kits/; adds /kits/ to footers and the sitemap.
Edit KITS below and rerun to change the page.
"""
import glob, html, json, os, re

E = lambda s: html.escape(str(s), quote=True)
EMAIL = "alex@thesignalhr.com"
TODAY = "2026-10-20"
changed = []

def rw(path, fn):
    s = open(path, encoding="utf-8", newline="").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)

KITS = [
    dict(id="ats", n="Kit 1", name="ATS Selection Kit", sub="with a hiring-AI governance module",
         who="TA operations, recruiting systems and HRIS leads running an ATS selection or replacement.",
         inside=["An editable evaluation scorecard, weighted to your hiring model",
                 "A demo script: the scenarios to make vendors show, not tell",
                 "The RFP question bank, ready to paste, with scoring guidance",
                 "A go-live readiness check: resourcing, approvals, scope and data",
                 "A business-case template for your CFO and CHRO",
                 "Governance module: what to check about the match score before you switch it on, by where you hire"],
         builds=[("ATS comparison", "/compare/ats/"), ("go-live drivers check", "/compare/ats/#implementation"), ("RFP bank", "/compare/ats/#rfp")]),
    dict(id="governance", n="Kit 2", name="Hiring-AI Governance Kit", sub="with a monthly rules update",
         who="TA, HR compliance and HR technology leads using AI to screen, score or rank applicants.",
         inside=["An inventory template for every AI feature touching candidates",
                 "A rules checklist by country, state and province, kept current",
                 "Candidate-notice and works-council briefing drafts to adapt with counsel",
                 "A vendor due-diligence questionnaire: audits, explanations, off switch",
                 "A bias-testing log with a review cadence",
                 "A monthly update: what changed where you hire, and what to do"],
         builds=[("applicant match comparison", "/compare/match/"), ("rules check for 38 places", "/compare/match/#rules")],
         note="Templates are drafts to adapt with your counsel, not legal advice."),
]

CSS = """
/* Kits page (scoped) */
.kits{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:1.2rem;margin-top:.4rem}
.kit{display:flex;flex-direction:column;gap:.8rem;padding:1.5rem 1.5rem 1.4rem}
.kit .kit-n{font-size:var(--text-xs);font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft)}
.kit h2{font-family:var(--font-display);font-weight:400;font-size:var(--text-xl);line-height:1.15}
.kit h2 small{display:block;font-family:var(--font-body);font-size:var(--text-sm);color:var(--signal);margin-top:.3rem;font-weight:600}
.kit .who{font-size:var(--text-sm);color:var(--ink-mid)}
.kit h3{font-family:var(--font-body);font-weight:700;font-size:var(--text-xs);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft);margin-top:.3rem}
.kit ul{padding-left:1.1rem;display:grid;gap:.35rem;font-size:var(--text-sm);color:var(--ink-mid)}
.kit .builds{font-size:var(--text-sm);color:var(--ink-mid)}
.kit .kit-note{font-size:var(--text-xs);color:var(--ink-soft)}
.kit .vote{margin-top:auto;align-self:flex-start}
.kit .vote[disabled]{opacity:.75;cursor:default}
.kits-note{font-size:var(--text-xs);color:var(--ink-soft);margin-top:1rem;max-width:46em}
.kits-thanks{margin-top:1rem;font-size:var(--text-sm);color:var(--ink);font-weight:600}
.kits-thanks[hidden]{display:none}
.shape p{color:var(--ink-mid);max-width:46em}
"""

JS = """
(function () {
  var thanks = document.getElementById("kits-thanks");
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("button[data-kit]");
    if (!b || b.disabled) return;
    if (typeof gtag === "function") gtag("event", "kit_vote", { kit: b.getAttribute("data-kit") });
    document.querySelectorAll("button[data-kit]").forEach(function (x) { x.disabled = true; });
    b.textContent = "Counted. Thank you.";
    if (thanks) thanks.hidden = false;
  });
})();
"""

def kit_card(k):
    inside = "".join(f"<li>{E(i)}</li>" for i in k["inside"])
    builds = ", ".join(f'<a href="{u}">{E(t)}</a>' for t, u in k["builds"])
    note = f'<p class="kit-note">{E(k["note"])}</p>' if k.get("note") else ""
    return f'''
        <article class="card kit" id="kit-{k["id"]}">
          <span class="kit-n">{E(k["n"])} · In development</span>
          <h2>{E(k["name"])}<small>{E(k["sub"])}</small></h2>
          <p class="who"><strong>For:</strong> {E(k["who"])}</p>
          <h3>What's inside</h3>
          <ul>{inside}</ul>
          <p class="builds"><strong>Builds on the free</strong> {builds}.</p>{note}
          <button type="button" class="btn btn-primary vote" data-kit="{k["id"]}">I'd use this first</button>
        </article>'''

def build():
    tpl = open("about/index.html", encoding="utf-8").read()
    url = "https://thesignalhr.com/kits/"
    title = "Buyer Kits in Development — The Signal HR"
    desc = ("Two buyer kits in development from The Signal HR: an ATS Selection Kit with a hiring-AI governance module, "
            "and a Hiring-AI Governance Kit with a monthly rules update. Tell us which you'd use first.")
    head = tpl[:tpl.index('<main id="main">')]
    main_tpl = tpl[tpl.index('<main id="main">'):tpl.index("</main>")]
    foot = tpl[tpl.index("</main>"):]
    head = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", head, flags=re.S)
    for attr in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
        head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(desc) + m.group(2), head)
    for attr in ['property="og:title"', 'name="twitter:title"']:
        head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(title) + m.group(2), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), head)
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "Buyer kits in development", "url": url, "dateModified": TODAY,
          "publisher": {"@type": "Organization", "name": "The Signal HR", "url": "https://thesignalhr.com/"}}
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", head, flags=re.S)
    head = head.replace('aria-current="page"', "")
    head = head.replace("</head>", f"<style>{CSS}</style>\n</head>")
    assert f'<link rel="canonical" href="{url}">' in head
    band = re.search(r'(  <section class="section" style="padding-top:0;">\s*<div class="wrap">\s*<div class="news-band">.*?</section>)', main_tpl, flags=re.S)
    assert band, "newsletter band not found in About page"
    band = band.group(1).replace("<h2>Walk into Monday <em>already knowing</em>.</h2>", "<h2>Hear when a kit <em>is ready</em>.</h2>")
    band = re.sub(r"(<div class=\"news-band\">.*?<p>).*?(</p>)", lambda m: m.group(1) + "Launch news goes to the newsletter first, along with the weekly signal: what changed in HR tech, what it means, what to do. Free forever." + m.group(2), band, count=1, flags=re.S)
    main = f'''<main id="main">
<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">The Signal</a><span>›</span>Buyer kits</nav></div>

  <section class="article-header">
    <div class="wrap">
      <span class="kicker">Buyer kits · In development</span>
      <h1 style="max-width:17em;">Two buyer kits are in the works. <em style="color:var(--signal);">Which would you use first?</em></h1>
      <p class="standfirst" style="max-width:41em;">The comparisons, checks and RFP banks stay free. The kits turn them into the working files a team builds during a decision: scorecards, scripts, templates and checklists. Neither is on sale yet, and your vote decides which comes first.</p>
      <div class="article-meta"><span>Updated October 20, 2026</span><span>No vendor pays</span><span>Pricing announced at launch</span></div>
    </div>
  </section>
  <section class="section" style="padding-top:0;">
    <div class="wrap">
      <div class="kits">{"".join(kit_card(k) for k in KITS)}
      </div>
      <p class="kits-thanks" id="kits-thanks" hidden aria-live="polite">Thanks. Launch news goes to the newsletter; subscribe below to hear first.</p>
      <p class="kits-note">Voting sends no personal information. We count clicks in Google Analytics, along with conversations with buyers, to decide which kit to build first.</p>
    </div>
  </section>
  <section class="section" style="padding-top:0;">
    <div class="wrap shape">
      <div class="section-head"><div><span class="kicker">Help shape it</span><h2>Making one of these <em>decisions</em> now?</h2></div></div>
      <p>If you're running an ATS selection or rolling out AI screening in the next six months, a 30-minute conversation about how you're doing it shapes what goes in each kit. Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </div>
  </section>
{band}
<script>{JS}</script>
'''
    return head + main + foot

# ---------------------------------------------------------------- the "Pro" wording
NB_OLD = "Free forever — founding readers lock the founding rate when Pro launches."
NB_NEW = 'Free forever. <a href="/kits/">See the buyer kits we\'re building</a>.'
SWAPS = [
    (NB_OLD, NB_NEW),
    ("Free forever — and when Pro launches, founding readers lock the founding rate.", NB_NEW),
    ("— the briefing is free forever; a Pro tier funds independence.",
     '— the briefing and comparisons are free forever; readers, not vendors, will fund the work through <a href="/kits/">buyer kits</a>.'),
    ("The weekly briefing is free forever. A Pro tier (deeper analysis and tools) funds the independence — founding subscribers lock the founding rate.",
     'The weekly briefing and the comparisons are free, for good. Readers, not vendors, will fund the work: paid <a href="/kits/">buyer kits</a> are in development.'),
]

def site(s):
    for old, new in SWAPS:
        s = s.replace(old, new)
    i = s.find("<footer")
    if i >= 0 and 'href="/kits/">Buyer kits</a></li>' not in s[i:]:
        s = s[:i] + re.sub(r'(\n([ \t]*)<li><a href="/compare/match/">Applicant match</a></li>)',
                           lambda m: m.group(1) + "\n" + m.group(2) + '<li><a href="/kits/">Buyer kits</a></li>', s[i:], count=1)
    return s

PAGES = sorted(f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("_", ".", "kits/")))
for f in PAGES:
    rw(f, site)

page = build()   # after the About page's footer has the new link
os.makedirs("kits", exist_ok=True)
old = open("kits/index.html", encoding="utf-8").read() if os.path.exists("kits/index.html") else None
if old != page:
    open("kits/index.html", "w", encoding="utf-8", newline="").write(page)
    changed.append("kits/index.html")

NBCSS = "\n/* newsletter band: links read on the dark band */\n.news-band p a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }\n"
rw("assets/site.css", lambda s: s if ".news-band p a" in s else s.rstrip("\n") + "\n" + NBCSS)

def sitemap(s):
    loc = "https://thesignalhr.com/kits/"
    if loc not in s:
        s = s.replace("</urlset>", f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>")
    return s
rw("sitemap.xml", sitemap)

left = [f for f in PAGES if "when Pro launches" in open(f, encoding="utf-8").read() or "Pro tier" in open(f, encoding="utf-8").read()]
assert not left, f"Pro wording left in: {left}"
print(f"{len(changed)} files changed")
for c in changed:
    print(" ", c)
