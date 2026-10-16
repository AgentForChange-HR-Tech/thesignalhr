"""Build /compare/crm/index.html from data.py, using another site page's header and footer.
Usage (from the repo root): python3 _tools/crm/build_crm.py compare/ats/index.html compare/crm/index.html
The first argument is only a template for the site header and footer; the ATS page works.
"""
import html, json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as D

E = lambda s: html.escape(str(s), quote=True)
tpl = open(sys.argv[1], encoding="utf-8").read()
head = tpl[:tpl.index('<main id="main">')]
foot = tpl[tpl.index('</main>'):]

URL = "https://thesignalhr.com/compare/crm/"
TITLE = "Recruiting CRMs Compared (2026): 17 Platforms, Side by Side — The Signal HR"
DESC = ("17 recruiting CRMs compared for HR leaders: Beamery, Gem, Phenom, Eightfold, Avature, Radancy and the CRM inside "
        "Workday, SAP, Oracle, iCIMS, Greenhouse and more. Check whether you need one, filter to your ATS and compare side by side. No vendor pays.")
head = re.sub(r"<title>.*?</title>", f"<title>{TITLE.replace('&', '&amp;')}</title>", head, flags=re.S)
for attr in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
    head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(DESC) + m.group(2), head)
for attr in ['property="og:title"', 'name="twitter:title"']:
    head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(TITLE) + m.group(2), head)
head = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + URL + m.group(2), head)
head = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + URL + m.group(2), head)
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Article", "headline": "Recruiting CRMs compared", "datePublished": "2026-10-16", "dateModified": "2026-10-16",
     "author": {"@type": "Person", "name": "Alex Rivera"},
     "publisher": {"@type": "Organization", "name": "The Signal HR", "url": "https://thesignalhr.com/"}, "mainEntityOfPage": URL},
    {"@type": "ItemList", "name": "Recruiting CRMs compared", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": p["name"], "url": f"{URL}#p-{p['id']}"} for i, p in enumerate(D.P)]},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "The Signal HR", "item": "https://thesignalhr.com/"},
        {"@type": "ListItem", "position": 2, "name": "Comparison Hub", "item": "https://thesignalhr.com/compare/"},
        {"@type": "ListItem", "position": 3, "name": "Recruiting CRMs", "item": URL}]}]}
head = re.sub(r'<script type="application/ld\+json">.*?</script>',
              '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', head, flags=re.S)
# drop any page-specific style blocks inherited from the template, then inline ours
head = re.sub(r"<style>\n/\* (ATS|CRM) comparison page.*?</style>\n", "", head, flags=re.S)
CSS = open(os.path.join(HERE, "crm.css"), encoding="utf-8").read()
head = head.replace("</head>", f"<style>\n{CSS}\n</style>\n</head>")
assert URL in head and "compare/ats/" not in head, "head still points at the template page"

CAPN = dict(D.CAPS)
LEVEL = {2: ("Native", "lv-2"), 1: ("Partial or add-on", "lv-1"), 0: ("Not a strength", "lv-0")}
GOVL = {2: "Certified", 1: "Partial", 0: "None found"}
ATSN = dict(D.ATS_OPTS)
REQN = {"workday": "Workday HCM and Workday Recruiting", "sap": "SAP SuccessFactors Recruiting", "oracle": "Oracle Fusion Cloud HCM",
        "greenhouse": "Greenhouse Recruiting", "lever": "Lever", "ashby": "Ashby", "jobvite": "Jobvite",
        "smartrecruiters": "the SmartRecruiters ATS", "icims": "iCIMS"}
SEGN = {"smb": "Under 500", "mid": "500–5,000", "ent": "5,000+"}
MODN = {"professional": "Professional", "volume": "High-volume hourly", "campus": "Campus"}
CATTAG = {"ats": "tag-signal", "suite": "tag-teal", "sourcing": "tag-amber", "ti": "tag-coral", "marketing": "tag-amber"}

def works(p):
    if p.get("req"):
        return "Requires " + REQN[p["req"]]
    if p["ats_int"]:
        extra = " (says it works with others)" if p.get("claims_other") else ""
        return "Documented ATS integrations: " + ", ".join(ATSN[a] for a in p["ats_int"]) + extra
    return "No ATS integrations documented by name" + (" (cites many connectors)" if p.get("claims_other") else "")
for p in D.P:
    p["works"] = works(p)

def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>" if items else ""
def chips(name, opts, kind="radio", default=None):
    return "".join(f'<label class="chip"><input type="{kind}" name="{name}" value="{v}"{" checked" if default == v else ""}><span>{E(l)}</span></label>' for v, l in opts)

out = []
out.append('<main id="main">\n<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">The Signal</a><span>›</span><a href="/compare/">Comparison Hub</a><span>›</span>Recruiting CRMs</nav></div>')
out.append(f'''
  <section class="article-header">
    <div class="wrap">
      <span class="kicker">Comparison Hub · Recruiting CRM</span>
      <h1 style="max-width:17em;">Recruiting CRMs: use the one you own, or <em style="color:var(--signal);">buy another?</em></h1>
      <p class="standfirst" style="max-width:41em;">{len(D.P)} platforms, from the CRM already inside your ATS or HCM suite to standalone CRMs that sit on top of it. Check whether a separate CRM would pay off, filter to your ATS, and compare up to three side by side. No vendor paid to be here, rank higher or be described favorably.</p>
      <div class="article-meta"><span>Reviewed {E(D.VERIFIED)}</span><span>{len(D.P)} platforms</span><span>Independent · unsponsored</span></div>
      <nav class="ats-jump" aria-label="On this page"><a href="#need">Do you need one?</a><a href="#finder">Find your shortlist</a><a href="#compare">Compare</a><a href="#landscape">The landscape</a><a href="#profiles">Platform profiles</a><a href="#rfp">RFP questions</a><a href="#method">How we review</a><a href="/compare/ats/">ATS platforms →</a></nav>
    </div>
  </section>''')

# ---------- Step 1: do you need a separate CRM? ----------
groups_html = []
for gid, gname, gdesc, kind in D.GROUPS:
    cards = []
    for f in [f for f in D.FACTORS if f["group"] == gid]:
        opts = "".join(f'<label class="chip"><input type="radio" name="f-{f["id"]}" value="{i}"><span>{E(lab)}</span></label>' for i, (lab, lv) in enumerate(f["opts"]))
        cards.append(f'''
          <article class="driver" id="d-{f["id"]}" data-kind="{kind}">
            <div class="dtop"><div><span class="dname">{E(f["name"])}</span><h4>{E(f["q"])}</h4></div><span class="dlevel" hidden></span></div>
            <div class="chips" role="radiogroup" aria-label="{E(f["q"])}">{opts}</div>
            <p class="dwhy">{E(f["why"])}</p>
            <details class="dhelp"><summary>{"What to look for" if kind == "need" else "What helps"}</summary><p>{E(f["helps"])}</p></details>
          </article>''')
    groups_html.append(f'''
        <div class="dgroup" id="g-{gid}">
          <div class="dgroup-head"><h3>{E(gname)}</h3><p>{E(gdesc)}</p></div>
          <div class="dgrid">{"".join(cards)}</div>
        </div>''')
FNAME = {f["id"]: f["name"] for f in D.FACTORS}
qgroups = []
for aid, aname in D.AUDIENCES:
    qs = [(f["id"], q) for f in D.FACTORS for a, q in f["ask"] if a == aid]
    if qs:
        qgroups.append(f'<div><h5>{E(aname)}</h5><ul>' + "".join(f'<li>{E(q)} <span class="qf">{E(FNAME[fid])}</span></li>' for fid, q in qs) + "</ul></div>")
nq = sum(len(f["ask"]) for f in D.FACTORS)
out.append(f'''
  <section class="section" id="need" style="padding-top:0;">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Step 1</span><h2>Do you need a <em>separate CRM?</em></h2></div></div>
      <p class="lede">Most ATS platforms and HCM suites now include a CRM, and many teams already pay for one they barely use. A separate CRM pays off when there is enough pipeline work to do and someone to do it. Answer what you know; the verdict, the capabilities to prioritize and your question list build below.</p>
      <form id="drivers" onsubmit="return false">{"".join(groups_html)}
      </form>
      <div class="card drivers-sum" id="drivers-sum">
        <div class="sum-head"><h3>Your verdict</h3><button type="button" class="btn btn-ghost" id="drivers-reset">Reset answers</button></div>
        <div id="drivers-out" aria-live="polite"><p class="sum-line">Answer at least two questions under "What you need it for" to see a verdict.</p></div>
        <details class="qdetails" id="drivers-qwrap">
          <summary><span id="drivers-qsum">Questions to ask, by who answers them ({nq})</span></summary>
          <p class="small">Questions behind the gaps you flag are marked Priority and move to the top.</p>
          <div class="qgroups" id="drivers-qs">{"".join(qgroups)}</div>
          <div class="sum-actions"><button type="button" class="btn btn-primary" id="drivers-copy">Copy questions</button><span class="small" id="drivers-copied" aria-live="polite"></span></div>
        </details>
      </div>
    </div>
  </section>''')

# ---------- Step 2 + 3: finder and compare ----------
out.append(f'''
  <section class="section section-alt" id="finder">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Step 2</span><h2>Find your <em>shortlist</em></h2></div></div>
      <form class="ats-filters" id="ats-filters" onsubmit="return false">
        <fieldset><legend>Company size</legend><div class="chips">{chips("size", [("any","Any"),("smb","Under 500"),("mid","500–5,000"),("ent","5,000+")], default="any")}</div></fieldset>
        <fieldset><legend>Your ATS</legend><div class="chips">{chips("ats", [("any","Not deciding on this")] + D.ATS_OPTS, default="any")}</div></fieldset>
        <fieldset><legend>Who you hire <small>(any that apply)</small></legend><div class="chips">{chips("model", list(MODN.items()), kind="checkbox")}</div></fieldset>
        <fieldset><legend>Must-haves <small>(any that apply)</small></legend><div class="chips">{chips("must", D.CAPS, kind="checkbox")}</div></fieldset>
      </form>
      <p class="ats-count" id="ats-count" aria-live="polite"></p>
      <div class="ats-results" id="ats-results"><noscript><p>The shortlist finder needs JavaScript. Every platform is profiled in full <a href="#profiles">below</a>.</p></noscript></div>
      <details class="ats-excluded" id="ats-excluded-wrap" hidden><summary id="ats-excluded-sum"></summary><ul id="ats-excluded"></ul></details>
    </div>
  </section>
  <section class="section" id="compare">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Step 3</span><h2>Compare <em>side by side</em></h2></div></div>
      <div id="ats-compare"><p class="ats-empty">Tick <strong>Compare</strong> on two or three platforms in your shortlist, or pick them here:</p></div>
      <div class="chips ats-pick" id="ats-pick">''' + "".join(f'<label class="chip"><input type="checkbox" data-cmp="{p["id"]}"><span>{E(p["name"])}</span></label>' for p in D.P) + '''</div>
    </div>
  </section>''')

# ---------- Landscape ----------
land = []
for c, label in D.CATS.items():
    members = [p for p in D.P if p["cat"] == c]
    land.append(f'<div class="card"><span class="tag {CATTAG[c]}">{E(label)}</span><p>{E(D.CAT_BLURB[c])}</p><p class="members">' + " · ".join(f'<a href="#p-{p["id"]}">{E(p["name"])}</a>' for p in members) + "</p></div>")
out.append(f'''
  <section class="section section-alt" id="landscape">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">The landscape</span><h2>Five kinds of <em>CRM</em></h2></div></div>
      <p class="lede">2025–26 reshaped ownership: SAP bought SmartRecruiters and now points its recruiting future there, Workday bought Paradox, Harver bought Symphony Talent, Clinch is now sold as PageUp Clinch under EQT, and Phenom made three acquisitions in 2026. Ownership changes roadmaps, so it's on every profile below.</p>
      <div class="grid grid-3">{"".join(land)}</div>
    </div>
  </section>''')

# ---------- Profiles ----------
prof = []
for p in D.P:
    lv = lambda k, v: (GOVL[v] if k == "gov" else LEVEL[v][0])
    caps = "".join(f'<li class="{LEVEL[p["caps"][k]][1]}"><span>{E(CAPN[k])}</span><b>{lv(k, p["caps"][k])}</b></li>' for k, _ in D.CAPS)
    src = " · ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in p["src"])
    ai_next = f'<h4>Announced or in beta</h4>{ul(p["ai_next"])}' if p["ai_next"] else ""
    fit = " · ".join(SEGN[s] for s in p["seg"]) + " employees · " + ", ".join(MODN[m] for m in p["models"])
    prof.append(f'''
      <details class="profile" id="p-{p["id"]}">
        <summary><span class="pname">{E(p["name"])}</span><span class="tag {CATTAG[p["cat"]]}">{E(D.CATS[p["cat"]])}</span><span class="powner">{E(p["owner"])}</span></summary>
        <div class="pbody">
          <p class="pbest"><strong>Best for:</strong> {E(p["best"])} <strong>Not for:</strong> {E(p["notfor"])}</p>
          <p class="pmeta">{E(fit)} · {E(p["works"])}</p>
          <p class="powner-note">{E(p["owner_note"])}</p>
          <div class="pgrid">
            <div><h4>Strengths</h4>{ul(p["strengths"])}<h4>Watch-outs</h4>{ul(p["watch"], "watch")}</div>
            <div><h4>Capabilities</h4><ul class="caps">{caps}</ul><h4>AI in production</h4>{ul(p["ai_live"])}{ai_next}<h4>AI governance evidence</h4><p>{E(p["gov"])}</p></div>
            <div><h4>How it's priced</h4><p>{E(p["pricing"])}</p>{ul(p["traps"], "watch")}<h4>Implementation</h4><p><strong>Delivery:</strong> {E(p["delivery"])}.</p><p class="small">{E(p["impl_note"])}</p><h4>Ask in the demo</h4>{ul(p["ask"], "ask")}</div>
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

# ---------- RFP + method ----------
rfp = "".join(f"<li>{E(q)}</li>" for q in D.RFP)
out.append(f'''
  <section class="section section-alt" id="rfp">
    <div class="wrap" style="max-width:860px;">
      <div class="section-head"><div><span class="kicker">Free to use</span><h2>The {len(D.RFP)}-question <em>CRM RFP bank</em></h2></div></div>
      <p class="lede">Questions that separate a demo's best campaign from what your recruiters will do on a Tuesday. The discomfort is diagnostic.</p>
      <ol class="rfp">{rfp}</ol>
    </div>
  </section>
  <section class="section" id="method">
    <div class="wrap" style="max-width:860px;">
      <div class="section-head"><div><span class="kicker">Independence</span><h2>How we <em>review</em></h2></div></div>
      <ul class="method">
        <li><strong>No vendor pays.</strong> No sponsorships, affiliate links or paid placement, and no vendor reviews its profile before publication.</li>
        <li><strong>Production versus promise.</strong> AI is listed as "in production" only when the vendor says it is available; everything else is labeled announced, beta, preview or roadmap with its date.</li>
        <li><strong>Capabilities.</strong> Ratings describe the CRM as sold in its CRM tier or module. "Native" means built in; "partial or add-on" means a further module, a partner or limited depth; "not a strength" means we found no strong evidence, so ask. What needs an extra license is in each profile's pricing and cost traps.</li>
        <li><strong>AI certification.</strong> "Certified" means an independent body certified the vendor's AI management (such as ISO/IEC 42001 or TrustArc). "Partial" means a published independent bias audit, or a certification whose scope doesn't name the product. Claims without published evidence count as none found.</li>
        <li><strong>ATS integrations.</strong> Listed only when we found them on a marketplace, partner or help page, not from a vendor's "integrates with every ATS" claim.</li>
        <li><strong>Implementation.</strong> We don't publish timelines. They depend on your campaign capacity, data, consent and ATS sync more than on the platform, so the Step 1 check shows those drivers and the questions that expose them.</li>
        <li><strong>Pricing.</strong> We describe how each vendor charges and where costs grow, not list prices, because enterprise prices are negotiated and change.</li>
        <li><strong>Freshness.</strong> Every profile shows when it was verified. We re-verify quarterly and after major vendor news. Spot something out of date? <a href="/about/">Tell us</a> and we'll fix it with a note.</li>
      </ul>
    </div>
  </section>''')

band = re.search(r'(  <section class="section" style="padding-top:0;">\s*<div class="wrap">\s*<div class="news-band">.*?</section>)', tpl, flags=re.S)
if band:
    out.append(band.group(1))

DATA = {"caps": D.CAPS, "cats": D.CATS, "atsn": ATSN, "reqn": REQN, "segn": SEGN, "modn": MODN, "p": D.P,
        "groups": D.GROUPS, "factors": D.FACTORS, "aud": D.AUDIENCES, "levels": D.LEVELS, "needcaps": D.NEED_CAPS}
JS = open(os.path.join(HERE, "crm.js"), encoding="utf-8").read()
out.append('<div class="ats-tray" id="ats-tray" hidden><div class="wrap"><span id="ats-tray-names"></span><a class="btn btn-primary" href="#compare">Compare</a><button type="button" class="btn btn-ghost" id="ats-clear">Clear</button></div></div>')
out.append('<script type="application/json" id="ats-data">' + json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/") + "</script>")
out.append("<script>\n" + JS + "\n</script>\n")
page = head + "\n".join(out) + "\n" + foot
os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True)
open(sys.argv[2], "w", encoding="utf-8").write(page)
print("wrote", sys.argv[2], len(page), "bytes")
