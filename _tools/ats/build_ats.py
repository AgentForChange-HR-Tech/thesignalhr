"""Build /compare/ats/index.html from data.py and the existing page's header/footer.
Usage: python3 build_ats.py <template_html> <out_html>
"""
import html, json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D

E = lambda s: html.escape(str(s), quote=True)
tpl = open(sys.argv[1], encoding="utf-8").read()
head_end = tpl.index('<main id="main">')
foot_start = tpl.index('</main>')
head = tpl[:head_end]
foot = tpl[foot_start:]

TITLE = "ATS &amp; Recruiting Platforms Compared (2026): 17 Platforms, Realistic Timelines — The Signal HR"
DESC = ("17 ATS and recruiting platforms compared for HR leaders: Workday, SAP SuccessFactors, Oracle, iCIMS, Greenhouse, "
        "Ashby, SmartRecruiters, Avature, Phenom, Eightfold and more. Filter to your situation, compare side by side, "
        "and see realistic implementation timelines. No vendor pays.")
head = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>", head, flags=re.S)
for attr in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
    head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(DESC) + m.group(2), head)
for attr in ['property="og:title"', 'name="twitter:title"']:
    head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + TITLE + m.group(2), head)
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Article", "headline": "ATS and recruiting platforms compared", "datePublished": "2026-06-28",
     "dateModified": "2026-10-16", "author": {"@type": "Person", "name": "Alex Rivera"},
     "publisher": {"@type": "Organization", "name": "The Signal HR", "url": "https://thesignalhr.com/"},
     "mainEntityOfPage": "https://thesignalhr.com/compare/ats/"},
    {"@type": "ItemList", "name": "ATS and recruiting platforms compared", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": p["name"], "url": f"https://thesignalhr.com/compare/ats/#p-{p['id']}"}
        for i, p in enumerate(D.P)]},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "The Signal HR", "item": "https://thesignalhr.com/"},
        {"@type": "ListItem", "position": 2, "name": "Comparison Hub", "item": "https://thesignalhr.com/compare/"},
        {"@type": "ListItem", "position": 3, "name": "ATS Platforms", "item": "https://thesignalhr.com/compare/ats/"}]}]}
head = re.sub(r'<script type="application/ld\+json">.*?</script>',
              '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', head, flags=re.S)
CSS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ats.css"), encoding="utf-8").read()
head = re.sub(r"<style>\n/\* ATS comparison page.*?</style>\n", "", head, flags=re.S)
head = head.replace("</head>", f"<style>\n{CSS}\n</style>\n</head>")

CAPN = dict(D.CAPS)
LEVEL = {2: ("Native", "lv-2"), 1: ("Partial or add-on", "lv-1"), 0: ("Not a strength", "lv-0")}
GOVL = {2: "Certified", 1: "Partial", 0: "None found"}
HRISN = {"any": "Works with any HRIS", "workday": "Requires Workday HCM", "sap": "Requires SAP SuccessFactors",
         "oracle": "Requires Oracle Fusion HCM", "ukg": "Requires UKG Pro", "dayforce": "Requires Dayforce"}
SEGN = {"smb": "Under 500", "mid": "500–5,000", "ent": "5,000+"}
MODN = {"professional": "Professional", "volume": "High-volume hourly", "agency": "Agency", "campus": "Campus"}
CATTAG = {"standalone": "tag-signal", "suite": "tag-teal", "volume": "tag-amber", "layer": "tag-coral", "agency": "tag-amber"}

def ul(items, cls=""):
    if not items:
        return ""
    return f'<ul class="{cls}">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"

# ---------- sections ----------
out = []
out.append('<main id="main">\n<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">The Signal</a><span>›</span><a href="/compare/">Comparison Hub</a><span>›</span>ATS Platforms</nav></div>')
out.append(f'''
  <section class="article-header">
    <div class="wrap">
      <span class="kicker">Comparison Hub · ATS &amp; recruiting platforms</span>
      <h1 style="max-width:17em;">ATS platforms, compared for the decision you're <em style="color:var(--signal);">actually</em> making.</h1>
      <p class="standfirst" style="max-width:40em;">{len(D.P)} platforms across five categories, from standalone ATS to HCM-suite recruiting. Filter to your situation, compare up to three side by side, and see implementation timelines that reflect real projects, not sales decks. No vendor paid to be here, rank higher or be described favorably.</p>
      <div class="article-meta"><span>Reviewed {E(D.VERIFIED)}</span><span>{len(D.P)} platforms</span><span>Independent · unsponsored</span></div>
      <nav class="ats-jump" aria-label="On this page"><a href="#finder">Find your shortlist</a><a href="#compare">Compare</a><a href="#implementation">Implementation timelines</a><a href="#landscape">The landscape</a><a href="#profiles">Platform profiles</a><a href="#rfp">RFP questions</a><a href="#method">How we review</a></nav>
    </div>
  </section>''')

# Finder
def chips(name, opts, kind="radio", default=None):
    h = []
    for val, label in opts:
        chk = " checked" if default == val else ""
        h.append(f'<label class="chip"><input type="{kind}" name="{name}" value="{val}"{chk}><span>{E(label)}</span></label>')
    return "".join(h)
out.append(f'''
  <section class="section" id="finder" style="padding-top:0;">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Step 1</span><h2>Find your <em>shortlist</em></h2></div></div>
      <form class="ats-filters" id="ats-filters" onsubmit="return false">
        <fieldset><legend>Company size</legend><div class="chips">{chips("size", [("any","Any"),("smb","Under 500"),("mid","500–5,000"),("ent","5,000+")], default="any")}</div></fieldset>
        <fieldset><legend>Your HRIS</legend><div class="chips">{chips("hris", [("any","Not deciding on this"),("workday","Workday"),("sap","SAP SuccessFactors"),("oracle","Oracle"),("ukg","UKG"),("dayforce","Dayforce"),("other","Other or none")], default="any")}</div></fieldset>
        <fieldset><legend>Who you hire <small>(any that apply)</small></legend><div class="chips">{chips("model", [("professional","Professional"),("volume","High-volume hourly"),("campus","Campus"),("agency","We're a staffing agency")], kind="checkbox")}</div></fieldset>
        <fieldset><legend>Must-haves <small>(any that apply)</small></legend><div class="chips">{chips("must", [(k, v) for k, v in D.CAPS], kind="checkbox")}</div></fieldset>
      </form>
      <p class="ats-count" id="ats-count" aria-live="polite"></p>
      <div class="ats-results" id="ats-results"><noscript><p>The shortlist finder needs JavaScript. Every platform is profiled in full <a href="#profiles">below</a>.</p></noscript></div>
      <details class="ats-excluded" id="ats-excluded-wrap" hidden><summary id="ats-excluded-sum"></summary><ul id="ats-excluded"></ul></details>
    </div>
  </section>
  <section class="section section-alt" id="compare">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Step 2</span><h2>Compare <em>side by side</em></h2></div></div>
      <div id="ats-compare"><p class="ats-empty">Tick <strong>Compare</strong> on two or three platforms in your shortlist, or pick them here:</p></div>
      <div class="chips ats-pick" id="ats-pick">''' + "".join(f'<label class="chip"><input type="checkbox" data-cmp="{p["id"]}"><span>{E(p["name"])}</span></label>' for p in D.P) + '''</div>
    </div>
  </section>''')

# Implementation
rows = []
for p in D.P:
    tds = "".join(f'<td class="{"na" if "Not a typical" in p["impl"][k] else ""}">{E(p["impl"][k])}</td>' for k in "ABC")
    rows.append(f'<tr><td><a href="#p-{p["id"]}">{E(p["name"])}</a></td><td>{E(D.CATS[p["cat"]])}</td>{tds}</tr>')
scen = "".join(f'<div class="card scen"><span class="tag tag-signal">Scenario {k}</span><h3>{E(v["name"])}</h3><p>{E(v["def"])}</p></div>' for k, v in D.SCENARIOS.items())
drivers = "".join(f"<li><strong>{E(a)}.</strong> {E(b)}</li>" for a, b in D.DRIVERS)
out.append(f'''
  <section class="section" id="implementation">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Reality check</span><h2>Implementation, <em>realistically</em></h2></div></div>
      <p class="lede">Vendor timelines describe a clean build with a ready customer. These ranges run from contract signature to go-live for your first population, for three typical scenarios. Plan another three to nine months of stabilization after go-live.</p>
      <div class="grid grid-3">{scen}</div>
      <div class="matrix-scroll" style="margin-top:1.4rem;"><table class="matrix impl"><thead><tr><th>Platform</th><th>Category</th><th>A · Focused</th><th>B · Multi-site</th><th>C · Global enterprise</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>
      <p class="note">"Not a typical fit" means few organizations of that shape choose the platform, not that it can't be done. Suite modules assume the HCM is already live; add the HCM program if it isn't.</p>
      <div class="grid grid-2" style="margin-top:1.6rem;align-items:start;">
        <div><h3 class="sub">What adds months</h3><ol class="drivers">{drivers}</ol></div>
        <div class="card evidence"><span class="tag tag-amber">Evidence</span><h3>Even an "add-on" takes most of a year</h3><p>The University of Washington, already on Workday HCM, approved Workday Recruiting in March 2024, implemented from September 2024 to August 2025, then planned a nine-month adapt phase to May 2026. AI résumé screening was left out of the initial scope.</p><p class="src"><a href="https://hr.uw.edu/talent/hiring-process/workday-recruiting-job-aids/workday-recruiting-project/" target="_blank" rel="noopener">University of Washington project page</a></p></div>
      </div>
    </div>
  </section>''')

# Landscape
land = []
for c, label in D.CATS.items():
    members = [p for p in D.P if p["cat"] == c]
    blurb = {
        "standalone": "A recruiting system that sits beside your HRIS. Best recruiter experience and fastest innovation; you own the HRIS integration.",
        "suite": "The recruiting module of your HCM suite. One data model and no hire sync to build; recruiter experience and pace depend on the suite.",
        "volume": "Conversational apply, screening and scheduling for hourly roles. Usually runs alongside a core ATS.",
        "layer": "Talent intelligence, CRM and candidate experience above or beside the ATS. Decide first whether you're replacing or layering.",
        "agency": "Built for staffing firms: clients, submittals, placements and pay-and-bill.",
    }[c]
    land.append(f'<div class="card"><span class="tag {CATTAG[c]}">{E(label)}</span><p>{E(blurb)}</p><p class="members">' + " · ".join(f'<a href="#p-{p["id"]}">{E(p["name"])}</a>' for p in members) + "</p></div>")
out.append(f'''
  <section class="section section-alt" id="landscape">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">The landscape</span><h2>Five kinds of <em>platform</em></h2></div></div>
      <p class="lede">2025–26 reshaped ownership: Workday bought Paradox, SAP bought SmartRecruiters, Thoma Bravo took Dayforce private and Phenom bought two assessment companies. Ownership changes roadmaps, so it's on every profile below.</p>
      <div class="grid grid-3">{"".join(land)}</div>
    </div>
  </section>''')

# Profiles
prof = []
for p in D.P:
    lv = lambda k, v: (GOVL[v] if k == "gov" else LEVEL[v][0])
    caps = "".join(f'<li class="{LEVEL[p["caps"][k]][1]}"><span>{E(CAPN[k])}</span><b>{lv(k, p["caps"][k])}</b></li>' for k, _ in D.CAPS)
    impl = "".join(f'<li><span>{k} · {E(D.SCENARIOS[k]["name"])}</span><b>{E(p["impl"][k])}</b></li>' for k in "ABC")
    src = " · ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in p["src"])
    ai_next = f'<h4>Announced or in beta</h4>{ul(p["ai_next"])}' if p["ai_next"] else ""
    fit = " · ".join([SEGN[s] for s in p["seg"]]) + " employees · " + ", ".join(MODN[m] for m in p["models"])
    prof.append(f'''
      <details class="profile" id="p-{p["id"]}">
        <summary><span class="pname">{E(p["name"])}</span><span class="tag {CATTAG[p["cat"]]}">{E(D.CATS[p["cat"]])}</span><span class="powner">{E(p["owner"])}</span></summary>
        <div class="pbody">
          <p class="pbest"><strong>Best for:</strong> {E(p["best"])} <strong>Not for:</strong> {E(p["notfor"])}</p>
          <p class="pmeta">{E(fit)} · {E(HRISN[p["hris"]])}</p>
          <p class="powner-note">{E(p["owner_note"])}</p>
          <div class="pgrid">
            <div><h4>Strengths</h4>{ul(p["strengths"])}<h4>Watch-outs</h4>{ul(p["watch"], "watch")}</div>
            <div><h4>Capabilities</h4><ul class="caps">{caps}</ul><h4>AI in production</h4>{ul(p["ai_live"])}{ai_next}<h4>AI governance evidence</h4><p>{E(p["gov"])}</p></div>
            <div><h4>How it's priced</h4><p>{E(p["pricing"])}</p>{ul(p["traps"], "watch")}<h4>Implementation</h4><ul class="caps impl-l">{impl}</ul><p class="small">{E(p["impl_note"])}</p><h4>Ask in the demo</h4>{ul(p["ask"], "ask")}</div>
          </div>
          <p class="src">Verified {E(D.VERIFIED)} · Sources: {src}</p>
        </div>
      </details>''')
out.append(f'''
  <section class="section" id="profiles">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Deep dives</span><h2>Platform <em>profiles</em></h2></div><a class="more" href="#" id="ats-expand">Expand all</a></div>
      <p class="lede">Every profile separates AI that is in production from AI that is announced, beta or roadmap, and every claim links to its source. Vendor-affiliated sources are labeled.</p>
      {"".join(prof)}
    </div>
  </section>''')

# RFP + method
rfp = "".join(f"<li>{E(q)}</li>" for q in D.RFP)
out.append(f'''
  <section class="section section-alt" id="rfp">
    <div class="wrap" style="max-width:860px;">
      <div class="section-head"><div><span class="kicker">Free to use</span><h2>The {len(D.RFP)}-question <em>RFP bank</em></h2></div></div>
      <p class="lede">Questions that separate demo theater from deployed reality. Ask them in this order; the discomfort is diagnostic.</p>
      <ol class="rfp">{rfp}</ol>
    </div>
  </section>
  <section class="section" id="method">
    <div class="wrap" style="max-width:860px;">
      <div class="section-head"><div><span class="kicker">Independence</span><h2>How we <em>review</em></h2></div></div>
      <ul class="method">
        <li><strong>No vendor pays.</strong> No sponsorships, affiliate links or paid placement, and no vendor reviews its profile before publication.</li>
        <li><strong>Production versus promise.</strong> AI is listed as "in production" only when the vendor says it is available; everything else is labeled announced, beta, preview or roadmap with its date.</li>
        <li><strong>Capabilities.</strong> "Native" means built into the product; "partial or add-on" means a separate module, a partner or limited depth; "not a strength" means we found no strong evidence, so ask.</li>
        <li><strong>Timelines.</strong> Ranges combine public project evidence with practitioner experience running enterprise HR systems. They describe typical projects, not guarantees.</li>
        <li><strong>Pricing.</strong> We describe how each vendor charges and where costs grow, not list prices, because enterprise prices are negotiated and change.</li>
        <li><strong>Freshness.</strong> Every profile shows when it was verified. We re-verify quarterly and after major vendor news. Spot something out of date? <a href="/about/">Tell us</a> and we'll fix it with a note.</li>
      </ul>
    </div>
  </section>''')

# subscribe band reused from template if present
band = re.search(r'(  <section class="section" style="padding-top:0;">\s*<div class="wrap">\s*<div class="news-band">.*?</section>)', tpl, flags=re.S)
if band:
    out.append(band.group(1))

DATA = {"caps": D.CAPS, "cats": D.CATS, "scen": D.SCENARIOS, "hrisn": HRISN, "segn": SEGN, "modn": MODN, "p": D.P}
JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ats.js"), encoding="utf-8").read()
out.append('<div class="ats-tray" id="ats-tray" hidden><div class="wrap"><span id="ats-tray-names"></span><a class="btn btn-primary" href="#compare">Compare</a><button type="button" class="btn btn-ghost" id="ats-clear">Clear</button></div></div>')
out.append('<script type="application/json" id="ats-data">' + json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/") + "</script>")
out.append("<script>\n" + JS + "\n</script>\n")
page = head + "\n".join(out) + "\n" + foot
open(sys.argv[2], "w", encoding="utf-8").write(page)
print("wrote", sys.argv[2], len(page), "bytes")
