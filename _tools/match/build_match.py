"""Build /compare/match/index.html from data.py, using another site page's header and footer.
Usage (from the repo root): python3 -B _tools/match/build_match.py compare/ats/index.html compare/match/index.html
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

URL = "https://thesignalhr.com/compare/match/"
TITLE = "Applicant Match Scores Compared (2026): 16 Platforms, Rated on Governance — The Signal HR"
DESC = ("16 applicant match and ranking tools compared on what you'd need to defend a score: explanations, recruiter control, "
        "human review, bias audits and AI certification. Greenhouse, Workday HiredScore, Eightfold, Gem, hireEZ and more, "
        "plus the hiring-AI rules in 17 places. No vendor pays.")
head = re.sub(r"<title>.*?</title>", f"<title>{TITLE.replace('&', '&amp;')}</title>", head, flags=re.S)
for attr in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
    head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(DESC) + m.group(2), head)
for attr in ['property="og:title"', 'name="twitter:title"']:
    head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(TITLE) + m.group(2), head)
head = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + URL + m.group(2), head)
head = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + URL + m.group(2), head)
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Article", "headline": "Applicant match scores compared", "datePublished": "2026-10-16", "dateModified": "2026-10-16",
     "author": {"@type": "Person", "name": "Alex Rivera"},
     "publisher": {"@type": "Organization", "name": "The Signal HR", "url": "https://thesignalhr.com/"}, "mainEntityOfPage": URL},
    {"@type": "ItemList", "name": "Applicant match scores compared", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": p["name"], "url": f"{URL}#p-{p['id']}"} for i, p in enumerate(D.P)]},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "The Signal HR", "item": "https://thesignalhr.com/"},
        {"@type": "ListItem", "position": 2, "name": "Comparison Hub", "item": "https://thesignalhr.com/compare/"},
        {"@type": "ListItem", "position": 3, "name": "Applicant match scores", "item": URL}]}]}
head = re.sub(r'<script type="application/ld\+json">.*?</script>',
              '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', head, flags=re.S)
# drop any page-specific style blocks inherited from the template, then inline ours
head = re.sub(r"<style>\n/\* (ATS|CRM|Match) comparison page.*?</style>\n", "", head, flags=re.S)
CSS = open(os.path.join(HERE, "match.css"), encoding="utf-8").read()
head = head.replace("</head>", f"<style>\n{CSS}\n</style>\n</head>")
assert URL in head and "compare/ats/" not in head, "head still points at the template page"

CAPN = dict(D.CAPS)
LEVEL = {2: "Documented", 1: "Partial", 0: "Not documented"}
AUDL = {2: "Recent, public", 1: "Older or narrower", 0: "None found"}
CERTL = {2: "Covers the product", 1: "Narrower scope", 0: "None found"}
def lvl_label(k, v):
    return AUDL[v] if k == "audit" else CERTL[v] if k == "cert" else LEVEL[v]
ATSN = dict(D.ATS_OPTS)
REQN = {"workday": "Workday Recruiting", "sap": "SAP SuccessFactors Recruiting", "oracle": "Oracle Recruiting",
        "greenhouse": "Greenhouse Recruiting", "lever": "Lever", "ashby": "Ashby", "jobvite": "Jobvite",
        "smartrecruiters": "the SmartRecruiters ATS", "icims": "iCIMS"}
SEGN = {"smb": "Under 500", "mid": "500–5,000", "ent": "5,000+"}
SCN = dict(D.SCORES)
OBLN = dict(D.OBL)
REGN = {"americas": "Americas", "emea": "EMEA", "apac": "APAC"}
CATTAG = {"ats": "tag-signal", "suite": "tag-teal", "ti": "tag-coral", "sourcing": "tag-amber"}

def works(p):
    if p.get("req"):
        return "Requires " + REQN[p["req"]]
    if p["ats_int"]:
        extra = " (says it works with others)" if p.get("claims_other") else ""
        return "Documented ATS integrations: " + ", ".join(ATSN[a] for a in p["ats_int"]) + extra
    return "No ATS integrations documented by name" + (" (says it works with others)" if p.get("claims_other") else "")
for p in D.P:
    p["works"] = works(p)

def ul(items, cls=""):
    return f'<ul class="{cls}">' + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>" if items else ""
def chips(name, opts, kind="radio", default=None):
    return "".join(f'<label class="chip"><input type="{kind}" name="{name}" value="{v}"{" checked" if default == v else ""}><span>{E(l)}</span></label>' for v, l in opts)

out = []
out.append('<main id="main">\n<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">The Signal</a><span>›</span><a href="/compare/">Comparison Hub</a><span>›</span>Applicant match scores</nav></div>')
out.append(f'''
  <section class="article-header">
    <div class="wrap">
      <span class="kicker">Comparison Hub · Applicant match scores</span>
      <h1 style="max-width:17em;">Applicant match scores: <em style="color:var(--signal);">can you explain the number?</em></h1>
      <p class="standfirst" style="max-width:41em;">{len(D.P)} platforms that score or rank applicants, from the match score inside your ATS or HCM suite to talent-intelligence and sourcing tools. Rated on what you'd need to defend a score: explanations, recruiter control, human review, an off switch, published bias audits and AI certification. Start with the rules where you hire. No vendor paid to be here, rank higher or be described favorably.</p>
      <div class="article-meta"><span>Reviewed {E(D.VERIFIED)}</span><span>{len(D.P)} platforms</span><span>{len(D.JURIS)} jurisdictions</span><span>Independent · unsponsored</span></div>
      <nav class="ats-jump" aria-label="On this page"><a href="#rules">Rules where you hire</a><a href="#finder">Find your shortlist</a><a href="#compare">Compare</a><a href="#landscape">The landscape</a><a href="#profiles">Platform profiles</a><a href="#rfp">RFP questions</a><a href="#method">How we review</a><a href="/compare/ats/">ATS platforms →</a><a href="/compare/crm/">Recruiting CRMs →</a></nav>
    </div>
  </section>''')

# ---------- Step 1: the rules where you hire ----------
jur_sets = []
for reg, rname in D.REGIONS:
    js = [j for j in D.JURIS if j["region"] == reg]
    jur_sets.append(f'''
          <fieldset class="jur-group"><legend>{E(rname)}</legend>
            <div class="chips">{"".join(f'<label class="chip"><input type="checkbox" name="jur" value="{j["id"]}"><span>{E(j["name"])}</span></label>' for j in js)}</div>
            <button type="button" class="linkbtn" data-all="{reg}">Select all {len(js)}</button>
          </fieldset>''')
out.append(f'''
  <section class="section" id="rules" style="padding-top:0;">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Step 1</span><h2>Before you switch a score on: <em>the rules where you hire</em></h2></div></div>
      <p class="lede">A match score is the AI feature most often switched on without a review, and the one hiring-AI rules are written about. Pick where you hire and how the score will be used. What applies, the capabilities to insist on and the questions for your vendor build below.</p>
      <form id="rules-form" onsubmit="return false">
        <div class="jur-grid">{"".join(jur_sets)}
        </div>
        <fieldset class="use-group"><legend>How the score will be used</legend>
          <div class="chips">{chips("use", D.USES, default="rank")}</div>
        </fieldset>
      </form>
      <div class="card drivers-sum" id="rules-sum">
        <div class="sum-head"><h3>What applies</h3><button type="button" class="btn btn-ghost" id="rules-reset">Clear</button></div>
        <div id="rules-out" aria-live="polite"><p class="sum-line">Pick at least one place you hire.</p></div>
        <div class="sum-actions" id="rules-actions" hidden><button type="button" class="btn btn-primary" id="rules-copy">Copy checklist</button><span class="small" id="rules-copied" aria-live="polite"></span></div>
        <p class="disclaimer"><strong>Orientation, not legal advice.</strong> These are the {len(D.JURIS)} places we track, reviewed {E(D.VERIFIED)}. Coverage thresholds, exemptions and pending rules vary, and anti-discrimination and privacy law apply everywhere, listed or not. Check with counsel where you hire.</p>
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
        <fieldset><legend>Who you'll score <small>(any that apply)</small></legend><div class="chips">{chips("score", D.SCORES, kind="checkbox")}</div></fieldset>
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
      <div class="section-head"><div><span class="kicker">The landscape</span><h2>Four places a <em>score</em> comes from</h2></div></div>
      <p class="lede">Scores are now in most recruiting stacks, often switched on in a release rather than bought. Ownership and litigation shape the risk: Workday owns HiredScore, SAP owns SmartRecruiters and is moving its recruiting there, Employ owns Lever, and Eightfold faces a class action over how candidate profiles are built. Assessments, video interviews and chatbot screening are out of scope here; they carry their own rules.</p>
      <div class="grid grid-2">{"".join(land)}</div>
    </div>
  </section>''')

# ---------- Profiles ----------
prof = []
for p in D.P:
    caps = "".join(f'<li class="lv-{p["caps"][k]}"><span>{E(CAPN[k])}</span><b>{lvl_label(k, p["caps"][k])}</b></li>' for k, _ in D.CAPS)
    src = " · ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in p["src"])
    fit = " · ".join(SEGN[s] for s in p["seg"]) + " employees · Scores " + ", ".join(SCN[s].lower() for s in p["scores"])
    prof.append(f'''
      <details class="profile" id="p-{p["id"]}">
        <summary><span class="pname">{E(p["name"])}</span><span class="tag {CATTAG[p["cat"]]}">{E(D.CATS[p["cat"]])}</span><span class="powner">{E(p["owner"])}</span></summary>
        <div class="pbody">
          <p class="pbest"><strong>Best for:</strong> {E(p["best"])} <strong>Not for:</strong> {E(p["notfor"])}</p>
          <p class="pmeta">{E(fit)} · {E(p["works"])}</p>
          <div class="pgrid">
            <div><h4>What the recruiter sees</h4><p>{E(p["output"])}</p><h4>How the score is set</h4><p>{E(p["how"])}</p><h4>Automatic actions</h4><p>{E(p["auto"])}</p></div>
            <div><h4>Governance</h4><ul class="caps">{caps}</ul><h4>Audit and certification evidence</h4><p>{E(p["gov"])}</p><h4>Strengths</h4>{ul(p["strengths"])}</div>
            <div><h4>Watch-outs</h4>{ul(p["watch"], "watch")}<h4>How it's priced</h4><p>{E(p["pricing"])}</p><h4>Ask in the demo</h4>{ul(p["ask"], "ask")}</div>
          </div>
          <p class="src">Verified {E(D.VERIFIED)} · Sources: {src}</p>
        </div>
      </details>''')
out.append(f'''
  <section class="section" id="profiles">
    <div class="wrap">
      <div class="section-head"><div><span class="kicker">Deep dives</span><h2>Platform <em>profiles</em></h2></div><a class="more" href="#" id="ats-expand">Expand all</a></div>
      <p class="lede">Each profile describes what a recruiter sees, who sets the criteria, what can happen automatically, and the public evidence behind the governance ratings. "Not documented" means we couldn't find it published, not that it's missing: ask.</p>
      {"".join(prof)}
    </div>
  </section>''')

# ---------- RFP + method ----------
rfp = "".join(f"<li>{E(q)}</li>" for q in D.RFP)
out.append(f'''
  <section class="section section-alt" id="rfp">
    <div class="wrap" style="max-width:860px;">
      <div class="section-head"><div><span class="kicker">Free to use</span><h2>The {len(D.RFP)}-question <em>match-score RFP bank</em></h2></div></div>
      <p class="lede">Questions that show whether you could explain a score to a candidate, a regulator or a works council. If the vendor can't answer them, you won't be able to either.</p>
      <ol class="rfp">{rfp}</ol>
    </div>
  </section>
  <section class="section" id="method">
    <div class="wrap" style="max-width:860px;">
      <div class="section-head"><div><span class="kicker">Independence</span><h2>How we <em>review</em></h2></div></div>
      <ul class="method">
        <li><strong>No vendor pays.</strong> No sponsorships, affiliate links or paid placement, and no vendor reviews its profile before publication.</li>
        <li><strong>Scope.</strong> Scores, grades and rankings computed from applications, résumés and profiles. Assessments, games, video interviews and conversational screening are out of scope: they work differently and carry their own rules.</li>
        <li><strong>Ratings reflect public documentation.</strong> "Documented" means the vendor documents it publicly; "Partial" means claimed without detail, or limited; "Not documented" means we found nothing published, so ask. We rate the score as sold, not a test of the product.</li>
        <li><strong>Bias audits.</strong> "Recent, public" means an independent audit or continuous monitoring of the scoring feature, published within about the last 18 months. "Older or narrower" means older, undated, a single model, or hosted by a customer. Audit claims without a published summary count as none found.</li>
        <li><strong>AI certification.</strong> "Covers the product" means an independent certification of the vendor's AI management, such as ISO/IEC 42001 or TrustArc, that covers the vendor or the product. "Narrower scope" means its scope doesn't name the product.</li>
        <li><strong>Rules where you hire.</strong> {len(D.JURIS)} jurisdictions with laws or guidance that bear on hiring scores, each linked to a source. It's orientation, not legal advice.</li>
        <li><strong>ATS integrations.</strong> Listed only when we found them on a marketplace, partner or help page, not from a vendor's "integrates with every ATS" claim.</li>
        <li><strong>Pricing.</strong> We describe how each vendor charges and where costs grow, not list prices, because enterprise prices are negotiated and change.</li>
        <li><strong>Freshness.</strong> Every profile shows when it was verified. We re-verify quarterly and after major vendor or legal news. Spot something out of date? <a href="/about/">Tell us</a> and we'll fix it with a note.</li>
      </ul>
    </div>
  </section>''')

band = re.search(r'(  <section class="section" style="padding-top:0;">\s*<div class="wrap">\s*<div class="news-band">.*?</section>)', tpl, flags=re.S)
if band:
    out.append(band.group(1))

DATA = {"caps": D.CAPS, "cats": D.CATS, "atsn": ATSN, "reqn": REQN, "segn": SEGN, "scn": SCN, "p": D.P,
        "juris": D.JURIS, "uses": D.USES, "obl": D.OBL, "oblask": D.OBL_ASK, "oblcaps": D.OBL_CAPS, "usecaps": D.USE_CAPS,
        "regn": REGN, "verified": D.VERIFIED}
JS = open(os.path.join(HERE, "match.js"), encoding="utf-8").read()
out.append('<div class="ats-tray" id="ats-tray" hidden><div class="wrap"><span id="ats-tray-names"></span><a class="btn btn-primary" href="#compare">Compare</a><button type="button" class="btn btn-ghost" id="ats-clear">Clear</button></div></div>')
out.append('<script type="application/json" id="ats-data">' + json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/") + "</script>")
out.append("<script>\n" + JS + "\n</script>\n")
page = head + "\n".join(out) + "\n" + foot
os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True)
open(sys.argv[2], "w", encoding="utf-8", newline="").write(page)
print("wrote", sys.argv[2], len(page), "bytes")
