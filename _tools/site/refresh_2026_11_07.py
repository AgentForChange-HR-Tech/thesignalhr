"""Site-wide content refresh, November 7, 2026. Run from the repo root:
    python3 -B _tools/site/refresh_2026_11_07.py
Idempotent. Applies the verified updates in editorial/claims/2026-11-07-site-refresh.md through the sources
(data files, build scripts, regional data, watchlist, article data) and edits the hand-maintained pages
(Coverage, the comparison hub, the current Briefing, About, Privacy). Then run, in order:
    python3 -B _tools/regional/build_articles.py insights/eu-ai-act-hr-deadline/index.html
    python3 -B _tools/ats/build_ats.py compare/ats/index.html compare/ats/index.html
    python3 -B _tools/crm/build_crm.py compare/ats/index.html compare/crm/index.html
    python3 -B _tools/match/build_match.py compare/ats/index.html compare/match/index.html
    python3 -B _tools/regional/build_regional.py 2026-11-07
    python3 -B _tools/site/consent.py && python3 -B _tools/site/signup.py && python3 -B _tools/site/frontpage.py
    python3 -B _tools/site/search_index.py && python3 -B _tools/verify/verify.py
"""
import json, os, re, sys
changed = []
TODAY, TODAY_ISO = "November 7, 2026", "2026-11-07"
NB = ' target="_blank" rel="noopener"'

def rw(path, fn):
    s = open(path, encoding="utf-8", newline="").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)

def pairs(items):
    def fn(s):
        for old, new in items:
            if old in s:
                s = s.replace(old, new)
            elif new in s:
                continue
            else:
                sys.exit(f"can't find {old[:100]!r}")
        return s
    return fn

def once(anchor, block, sentinel, before=True):
    def fn(s):
        if sentinel in s:
            return s
        if s.count(anchor) != 1:
            sys.exit(f"anchor not unique or missing: {anchor[:80]!r}")
        return s.replace(anchor, block + anchor if before else anchor + block, 1)
    return fn

# ================================================================ comparison data and builders
for name in ("ats", "crm", "match"):
    rw(f"_tools/{name}/data.py", once('VERIFIED = "October 2026"\n', f'CHECKED = "{TODAY}"   # last check for changes since VERIFIED\n',
                                      "CHECKED = ", before=False))
    rw(f"_tools/{name}/build_{name}.py", lambda s: s if "Checked for changes {E(D.CHECKED)}" in s else
       s.replace("<span>Reviewed {E(D.VERIFIED)}</span>", "<span>Reviewed {E(D.VERIFIED)}</span><span>Checked for changes {E(D.CHECKED)}</span>", 1))
    rw(f"_tools/{name}/build_{name}.py", pairs([
        ('<p class="src">Verified {E(D.VERIFIED)} · Sources: {src}</p>',
         '<p class="src">Verified {E(D.VERIFIED)}{(" · Updated " + E(p["updated"])) if p.get("updated") else ""} · Sources: {src}</p>'),
    ]))
rw("_tools/match/build_match.py", pairs([
    ("reviewed {E(D.VERIFIED)}. Coverage thresholds", "reviewed {E(D.VERIFIED)} and checked for changes {E(D.CHECKED)}. Coverage thresholds"),
    ('"regn": REGN, "verified": D.VERIFIED}', '"regn": REGN, "verified": D.VERIFIED, "checked": D.CHECKED}'),
]))

ICIMS_SRC = '("iCIMS 2026 Fall Release, October 20, 2026","https://www.icims.com/company/newsroom/fallrelease2026/"),'
rw("_tools/ats/data.py", pairs([
    ('"iCIMS Hiring Agent in Microsoft Teams (planned for October 2026)"',
     '"iCIMS Hiring Agent in Microsoft Teams (Fall 2026 release, rolling out from October 26, 2026)"'),
    ('"Two of the three new agents were not yet available at announcement"',
     '"The Interview Scheduling Agent was still expected by the end of 2026 at the October 2026 release"'),
    ('src=[("iCIMS Intelligent Hiring Platform, September 1, 2026"', 'src=[' + ICIMS_SRC + '("iCIMS Intelligent Hiring Platform, September 1, 2026"'),
    # Dayforce: Ribbon closed (HR Brew, November 5, 2026); agentic recruiting announced October 27, 2026
    (' owner_note="Dayforce was taken private by Thoma Bravo for about $12.3B, completed February 4, 2026.",',
     ' owner_note="Dayforce was taken private by Thoma Bravo for about $12.3B, completed February 4, 2026. Closed its purchase of AI interviewer Ribbon in November 2026, per HR Brew.", updated="' + TODAY + '",'),
    (' ai_live=["Content-authoring agent for job descriptions and communications"],\n ai_next=[],',
     ' ai_live=["Content-authoring agent for job descriptions and communications"],\n'
     ' ai_next=["Agentic Recruiting for sourcing, screening, scheduling and candidate engagement (announced October 27, 2026; planned to roll out through 2027)",'
     '"Ribbon conversational voice and video interviews, sourcing and rediscovery in the Talent experience (deal closed November 2026; no integration date)"],'),
    ('"No recruiting-specific AI certification found"],\n ai_live=["Content-authoring',
     '"No recruiting-specific AI certification found","Ribbon\'s AI interviews: ask what bias testing and human review come with them before switching them on"],\n ai_live=["Content-authoring'),
    ('src=[("Thoma Bravo completes Dayforce acquisition"',
     'src=[("Dayforce agentic talent experiences, October 27, 2026","https://www.dayforce.com/who-we-are/newsroom/dayforce-introduces-agentic-talent-experiences-to-transform-how-organizations-hire-and-develop-talen"),'
     '("HR Brew: Dayforce closes Ribbon deal, November 5, 2026","https://www.hr-brew.com/stories/dayforce-closes-deal-to-acquire-ai-interviewing-platform-ribbon"),'
     '("Thoma Bravo completes Dayforce acquisition"'),
]))
# mark the iCIMS ATS profile as updated
rw("_tools/ats/data.py", lambda s: s if 'name="iCIMS", cat="standalone", owner="Private (iCIMS)", updated=' in s else
   s.replace('name="iCIMS", cat="standalone", owner="Private (iCIMS)",', f'name="iCIMS", cat="standalone", owner="Private (iCIMS)", updated="{TODAY}",', 1))
rw("_tools/crm/data.py", pairs([
    ('ai_live=["AI Sourcing Agent in CXM, searching the iCIMS database (Spring 2026 release; reaffirmed September 2026)",',
     'ai_live=["Hiring Agent in Microsoft Teams (Fall 2026 release, rolling out from October 26, 2026)","AI Sourcing Agent in CXM, searching the iCIMS database (Spring 2026 release; reaffirmed September 2026)",'),
    ('ai_next=["Hiring Agent in Microsoft Teams (planned October 2026)","Interview Scheduling Agent (expected by end of 2026)"],',
     'ai_next=["Interview Scheduling Agent (expected by end of 2026)"],'),
]))
def crm_icims(s):
    m = re.search(r'name="iCIMS CRM and CXM"[^\n]*\n', s)
    if not m: sys.exit("crm: iCIMS profile not found")
    i = s.find("src=[", m.end())
    if ICIMS_SRC not in s[i:i + 400]:
        s = s[:i] + "src=[" + ICIMS_SRC + s[i + 5:]
    if f'updated="{TODAY}"' not in s[m.start():m.end()]:
        s = s[:m.start()] + m.group(0).replace('name="iCIMS CRM and CXM",', f'name="iCIMS CRM and CXM", updated="{TODAY}",', 1) + s[m.end():]
    return s
rw("_tools/crm/data.py", crm_icims)

rw("_tools/match/data.py", pairs([
    ("The EEOC plans to rescind the Uniform Guidelines, including the 80% benchmark, from January 2027; Title VII disparate-impact claims remain.",
     "The EEOC sent a final rule rescinding the Uniform Guidelines, including the 80% benchmark, to White House review on October 16, 2026, projecting a January 2027 effective date; Title VII disparate-impact claims remain."),
    ('("Ogletree Deakins", "https://ogletree.com/insights-resources/blog-posts/the-eeocs-regulatory-agenda-10-signs-of-intent/")',
     '("Ogletree Deakins", "https://ogletree.com/insights-resources/blog-posts/eeoc-sends-oira-final-rule-rescinding-uniform-guidelines-on-employee-selection-procedures/")'),
    ("A bill to push the start date to December 1, 2027 is pending in the Senate.",
     "On October 28, 2026 the Senate approved a bill moving the start date to October 15, 2027; it now goes to the Chamber of Deputies, and December 1, 2026 stands until the change is published."),
    ("Draft amendments, open for comment until November 5, 2026, would make automated decisions an explicit assessment trigger.",
     "Draft amendments, whose comment period closed November 5, 2026, would make automated decisions an explicit assessment trigger; they are not yet adopted."),
]))
def match_src(s):
    # Chile: the Senate vote replaces the bill's introduction as the second source; Colorado: add the Attorney General's rulemaking page
    s = s.replace('("Carey on the postponement bill", "https://www.carey.cl/gobierno-ingresa-proyecto-de-ley-que-posterga-en-un-ano-entrada-en-vigor-de-la-ley-sobre-proteccion-de-datos-personales")',
                  '("Garrigues on the Senate vote", "https://www.garrigues.com/es_ES/noticia/senado-chileno-aprueba-proyecto-ley-busca-postergar-15-octubre-2027-entrada-vigencia-nueva")')
    return s
rw("_tools/match/data.py", match_src)
def colorado(s):
    i = s.find('id="colorado"')
    if i < 0: sys.exit("match: colorado not found")
    j = s.find("\n dict(", i + 10); j = j if j > 0 else s.find("\n]", i)
    blk = s[i:j]
    if "coag.gov/ai" in blk:
        return s
    m = re.search(r'src=\("Epstein Becker Green", "https://www\.ebglaw\.com/workforce-bulletin/inside-colorados-senate-bill-26-189-impacts-and-implications-for-employers"\)', blk)
    if not m: sys.exit("match: colorado src not found")
    blk = (blk[:m.end()] + ', src2=("Colorado Attorney General: rulemaking (hearing October 26, 2026)", "https://coag.gov/ai/"),'
           '\n  watch="The Attorney General held the rulemaking hearing on October 26, 2026; the law requires final rules before January 1, 2027."' + blk[m.end():])
    return s[:i] + blk + s[j:]
rw("_tools/match/data.py", colorado)

# ================================================================ watchlist
def watch(s):
    w = json.loads(s)
    by = {x["id"]: x for x in w}
    upd = {
        "saudi-pdpl-draft": ("Saudi PDPL draft amendments: comment period closed November 5, 2026; not yet adopted. Adopted text may change the automated-decision trigger", None, "2027-01-15"),
        "india-dpdp-timeline": ("India DPDP: consent-manager provisions from November 13, 2026; substantive duties from May 13, 2027. MeitY's January 2026 proposal to shorten the timeline was not notified as of October 8, 2026", "https://theprivacylabs.com/blogs/dpdp-13-november-2026-what-starts", "2026-12-15"),
        "chile-delay-bill": ("Chile Law 21,719 in force from December 1, 2026; the Senate approved on October 28, 2026 a bill moving it to October 15, 2027, now in the Chamber of Deputies", "https://www.garrigues.com/es_ES/noticia/senado-chileno-aprueba-proyecto-ley-busca-postergar-15-octubre-2027-entrada-vigencia-nueva", "2026-11-30"),
        "eeoc-uniform-guidelines": ("EEOC final rule rescinding the Uniform Guidelines at White House (OIRA) review since October 16, 2026; projected effective January 2027; not yet published", "https://ogletree.com/insights-resources/blog-posts/eeoc-sends-oira-final-rule-rescinding-uniform-guidelines-on-employee-selection-procedures/", "2026-11-30"),
        "colorado-rules-stay": ("Colorado SB 26-189 from January 1, 2027; rulemaking hearing held October 26, 2026, final rules due before January 1, 2027; enforcement stayed by a court", "https://coag.gov/ai/", "2026-12-15"),
    }
    for k, (fact, src, when) in upd.items():
        if k in by:
            by[k]["fact"] = fact
            if src: by[k]["source"] = src
            by[k]["recheck_by"] = when
    new = [
        {"id": "dhs-ics-deference", "fact": "DHS proposal to end USCIS deference to prior approvals for H-1B, L-1 and other I-129 extensions (Federal Register October 14, 2026; comments close November 13, 2026); proposal only",
         "where": ["coverage (Mobility & Immigration)", "coverage calendar"], "source": "https://www.duanemorris.com/alerts/dhs_proposes_end_deference_prior_approvals_h1b_l1_other_form_I129_extensions_1026.html", "recheck_by": "2027-01-15", "status": "open"},
        {"id": "uk-pay-in-adverts", "fact": "UK government plans a legal requirement to publish pay in job adverts (announced November 5, 2026); legislation not yet introduced",
         "where": ["coverage (Talent Acquisition)", "coverage radar"], "source": "https://www.gov.uk/government/news/new-say-what-you-pay-law-to-help-young-people-into-work", "recheck_by": "2027-01-15", "status": "open"},
        {"id": "sap-techwolf", "fact": "SAP's acquisition of TechWolf expected to close in Q4 2026", "where": ["coverage (L&D & Skills)"],
         "source": "https://news.sap.com/2026/10/sap-to-acquire-techwolf-evidence-based-work-age-of-ai/", "recheck_by": "2027-01-15", "status": "open"},
        {"id": "dayforce-ribbon", "fact": "Dayforce closed its Ribbon purchase (HR Brew, November 5, 2026); agentic recruiting experiences planned through 2027; no integration date",
         "where": ["compare/ats (Dayforce Recruiting)", "coverage (HR Tech)", "briefing 2026-11-02"], "source": "https://www.hr-brew.com/stories/dayforce-closes-deal-to-acquire-ai-interviewing-platform-ribbon", "recheck_by": "2027-01-15", "status": "open"},
        {"id": "icims-scheduling-agent", "fact": "iCIMS Interview Scheduling Agent expected by the end of 2026", "where": ["compare/ats (iCIMS)", "compare/crm (iCIMS)"],
         "source": "https://www.icims.com/company/newsroom/fallrelease2026/", "recheck_by": "2027-01-15", "status": "open"},
    ]
    for n in new:
        if n["id"] not in by:
            w.append(n)
    w.sort(key=lambda x: x["recheck_by"])
    return json.dumps(w, indent=1, ensure_ascii=False) + "\n"
rw("_tools/verify/watchlist.json", watch)

# ================================================================ regional radar and calendar
GARR = "https://www.garrigues.com/es_ES/noticia/senado-chileno-aprueba-proyecto-ley-busca-postergar-15-octubre-2027-entrada-vigencia-nueva"
OGLE = "https://ogletree.com/insights-resources/blog-posts/eeoc-sends-oira-final-rule-rescinding-uniform-guidelines-on-employee-selection-procedures/"
UKPAY = "https://www.gov.uk/government/news/new-say-what-you-pay-law-to-help-young-people-into-work"
DUANE = "https://www.duanemorris.com/alerts/dhs_proposes_end_deference_prior_approvals_h1b_l1_other_form_I129_extensions_1026.html"
rw("_tools/regional/regional.py", pairs([
    ('UPDATED = "October 16, 2026"', f'UPDATED = "{TODAY}"'),
    ("Federal preemption efforts haven't displaced either.\",",
     "Federal preemption efforts haven't displaced either. Colorado's Attorney General held the rules hearing on October 26, 2026.\","),
    ('[("Epstein Becker Green", "https://www.ebglaw.com/workforce-bulletin/inside-colorados-senate-bill-26-189-impacts-and-implications-for-employers"), ("Bass Berry", "https://bassberry.com/news/ccpa-sept-2025-update/")], "/insights/americas-ai-hiring-notice-2027/"',
     '[("Epstein Becker Green", "https://www.ebglaw.com/workforce-bulletin/inside-colorados-senate-bill-26-189-impacts-and-implications-for-employers"), ("Bass Berry", "https://bassberry.com/news/ccpa-sept-2025-update/"), ("Colorado Attorney General", "https://coag.gov/ai/")], "/insights/americas-ai-hiring-notice-2027/"'),
    ("New Jersey codified disparate-impact rules that cover automated tools in December 2025.\",",
     "New Jersey codified disparate-impact rules that cover automated tools in December 2025. On October 16, 2026 the EEOC sent a final rule rescinding the Uniform Guidelines, including the 80% benchmark, to White House review.\","),
    ('("Morgan Lewis", "https://www.morganlewis.com/pubs/2025/12/new-jersey-codifies-existing-disparate-impact-rules")]',
     f'("Morgan Lewis", "https://www.morganlewis.com/pubs/2025/12/new-jersey-codifies-existing-disparate-impact-rules"), ("Ogletree Deakins", "{OGLE}")]'),
    ("Day-one statutory sick pay arrived April 6, 2026. The duty to prevent sexual harassment, including by third parties, starts October 30. The unfair-dismissal qualifying period drops to six months on January 1, 2027.",
     "Day-one statutory sick pay arrived April 6, 2026, and the duty to prevent sexual harassment, including by third parties, has applied since October 30. The unfair-dismissal qualifying period drops to six months on January 1, 2027. On November 5 the government said it will make publishing pay in job adverts a legal requirement."),
    ('plan-to-make-work-pay-and-employment-rights-act-timeline-update")], None)',
     f'plan-to-make-work-pay-and-employment-rights-act-timeline-update"), ("GOV.UK: say what you pay", "{UKPAY}")], None)'),
]))
rw("_tools/regional/regional.py", once(' ("americas", "Federal agencies stepped back',
    ' ("americas", "Chile\'s data law may slip to October 2027", "On October 28, 2026 Chile\'s Senate approved a bill moving the start of its new data protection law, Law 21,719, from December 1, 2026 to October 15, 2027. The Chamber of Deputies still has to vote; until the change is published, December 1 stands.",\n'
    f'  [("Garrigues", "{GARR}")], None),\n', "Chile's data law may slip"))
rw("_tools/regional/regional.py", once(' ("2026-12-02", "Dec 2, 2026", "European Union"',
    f' ("2026-11-13", "Nov 13, 2026", "United States", "americas", "Comments close on the DHS proposal to end USCIS deference to earlier approvals for H-1B, L-1 and other I-129 extensions.", "Duane Morris", "{DUANE}"),\n'
    f' ("2026-12-01", "Dec 1, 2026", "Chile", "americas", "Data protection Law 21,719 takes effect, unless the Senate-passed bill moving it to October 15, 2027 is enacted first.", "Garrigues", "{GARR}"),\n',
    "USCIS deference"))

# ================================================================ Coverage: current signal per domain
def sig(text, sources):
    src = " · ".join(f'<a href="{u}"{NB if u.startswith("http") else ""}>{t}</a>' for t, u in sources)
    label = "Sources" if len(sources) > 1 else "Source"
    return f'<strong>Current signal · </strong>{text} <span class="sig-src">{label}: {src}</span>'
SIG = {
 "hr-tech": ("global", sig("Dayforce said on October 27, 2026 that its AI agents are available now and that its new agentic experiences, including recruiting and learning, are planned to roll out through 2027; on November 5 HR Brew reported that Dayforce has closed its purchase of AI interviewer Ribbon. With agents arriving in every suite, a useful question for any vendor is which steps an agent can take without a person's approval, and where that is logged.",
    [("Dayforce", "https://www.dayforce.com/who-we-are/newsroom/dayforce-introduces-agentic-talent-experiences-to-transform-how-organizations-hire-and-develop-talen"), ("HR Brew", "https://www.hr-brew.com/stories/dayforce-closes-deal-to-acquire-ai-interviewing-platform-ribbon")])),
 "talent-acquisition": ("emea", sig("The UK government said on November 5, 2026 that it will make it a legal requirement for employers to publish pay in job adverts, with legislation &ldquo;as soon as possible&rdquo; and details on scope and enforcement to follow. It cites CIPD data that only 41% of employers always publish salary ranges. For UK hiring, it may be worth checking whether job templates, the ATS and job-board feeds can carry a pay range.",
    [("GOV.UK", UKPAY)])),
 "people-analytics": ("americas", sig("The BLS reported on November 6, 2026 that US payrolls rose by 165,000 in October, above the prior 12-month average of 48,000, with unemployment little changed at 4.1%; August and September were revised up by a combined 84,000. Professional and business services added 70,000 and health care 42,000. One month is one data point, so reading your own hiring and attrition trends against the revised series may say more than the first print.",
    [("Bureau of Labor Statistics", "https://www.bls.gov/news.release/empsit.nr0.htm")])),
 "risk-compliance": ("global", sig("The EU's employment-AI duties start December 2, 2027, but nearer dates are elsewhere: Australia's automated-decision disclosure (December 10, 2026), Colorado and California (January 1, 2027) and Korea's high-impact AI rules. Colorado's Attorney General held the rulemaking hearing on October 26, 2026, and the law requires final rules before January 1, 2027. One notice-and-human-review standard may cover much of this.",
    [("Colorado Attorney General", "https://coag.gov/ai/"), ("Regional calendar", "#calendar")])),
 "hr-transformation": ("americas", sig("Challenger's October 2026 report (November 5) counted 43,994 announced US job cuts, down 71% from October 2025. AI was cited for 1,265 of them, bringing 2026 to 121,401, about 20% of all cuts, and October hiring plans reached 444,692, up 57% from a year earlier. Before another AI-linked round, one question worth asking is whether this year's cuts changed how the work gets done.",
    [("Challenger, Gray &amp; Christmas", "https://www.challengergray.com/blog/october-layoffs-at-three-year-low-seasonal-hiring-plans-up-26/")])),
 "future-of-work": ("americas", sig("A Goldman Sachs note reported by Fortune on October 30, 2026 finds that workers displaced from AI-exposed jobs since 2025 took about a month longer to find new work than other displaced workers and were roughly 10 percentage points likelier to be unemployed a year later. No survey asks whether AI caused a job loss, so Goldman built a proxy. Where restructuring is attributed to AI, redeployment and retraining options may matter more than usual, especially for long-tenured staff.",
    [("Fortune", "https://fortune.com/2026/10/30/goldman-sachs-ai-layoffs-displaced-workers-older-workers-past-tech-disruptions")])),
 "learning-skills": ("global", sig("SAP said on October 6, 2026 that it will acquire TechWolf, which keeps an up-to-date picture of the work people do and the skills they hold; the deal is expected to close in Q4 2026, and TechWolf is to stay available to non-SAP customers. It follows Pearson's September 29 agreement to buy Workera, which verifies skills through role-based simulations. A question worth asking of any skills profile: was it assessed, inferred from work, or self-reported?",
    [("SAP", "https://news.sap.com/2026/10/sap-to-acquire-techwolf-evidence-based-work-age-of-ai/"), ("Pearson", "https://www.prnewswire.com/news-releases/pearson-acquires-workera-a-pioneer-in-ai-native-enterprise-assessment-and-skills-verification-302891786.html")])),
 "career-pathways": ("global", sig("Gartner (October 6, 2026): only 35% of employees see a clear career path as AI changes work, and those who do are 3.5 times as likely to be highly engaged. It may be worth checking whether published career paths reflect the roles AI is reshaping.",
    [("Gartner", "https://www.gartner.com/en/newsroom/press-releases/2026-10-6-gartner-hr-symposium-xpo-london-day-1-highlights")])),
 "immigration": ("americas", sig("Two DHS proposals affect sponsored staff. Comments close November 10, 2026 on ending the 60-day grace period for H-1B, L-1, O-1, TN and E workers whose jobs end, and November 13 on ending USCIS deference to earlier approvals when an employer extends an H-1B, L-1 or other I-129 petition (Federal Register, October 14). Both are proposals; current rules apply until a final rule takes effect.",
    [("Federal Register", "https://www.federalregister.gov/documents/2026/09/11/2026-18631/eliminating-the-discretionary-60-day-grace-period"), ("Duane Morris", DUANE)])),
 "comparisons": ("global", '<strong>Current signal · </strong>Checked for changes on November 7, 2026: iCIMS\'s Hiring Agent in Microsoft Teams is rolling out from October 26 in its Fall release, and Dayforce has closed its purchase of AI interviewer Ribbon, with agentic recruiting planned through 2027. The rules check now notes the EEOC\'s Uniform Guidelines rule under White House review and Chile\'s Senate-passed delay bill. Every change is in the <a href="/compare/#changelog">change log</a>. <a href="/compare/ats/">ATS comparison →</a> <a href="/compare/crm/">CRM comparison →</a> <a href="/compare/match/">Match comparison →</a>'),
}
LABEL = {"global": "Global", "americas": "Americas", "emea": "EMEA", "apac": "APAC"}
def coverage(s):
    for did, (reg, html_) in SIG.items():
        m = re.search(r'(<article class="card" id="%s" data-region=")([^"]*)("[^>]*>)(.*?)(</article>)' % re.escape(did), s, flags=re.S)
        if not m: sys.exit(f"coverage: {did} not found")
        body = m.group(4)
        body = re.sub(r'<span class="region-tag">[^<]*</span>', f'<span class="region-tag">{LABEL[reg]}</span>', body, count=1)
        body = re.sub(r'(<div class="so-what">).*?(</div>)', lambda x: x.group(1) + html_ + x.group(2), body, count=1, flags=re.S)
        s = s[:m.start()] + m.group(1) + reg + m.group(3) + body + m.group(5) + s[m.end():]
    s = re.sub(r"<span>Updated [A-Z][a-z]+ \d{1,2}, \d{4}</span><span>Americas · EMEA · APAC</span>",
               f"<span>Updated {TODAY}</span><span>Americas · EMEA · APAC</span>", s, count=1)
    return s
rw("coverage/index.html", coverage)

# ================================================================ comparison hub: change log, dates
LOG = [
    (TODAY, "Applicant match", "Rules check updated: the EEOC's Uniform Guidelines rescission at White House review (October 16), Chile's Senate-passed delay to October 15, 2027, Saudi draft comment period closed, and Colorado's rules hearing (October 26)."),
    (TODAY, "ATS platforms, Recruiting CRMs", "Checked for changes: iCIMS Hiring Agent marked as rolling out from October 26 (Fall release); Dayforce adds the Ribbon acquisition and agentic recruiting planned through 2027."),
    ("November 6, 2026", "All comparisons", "Neutral-language pass: profiles describe typical use instead of who a platform is for, finders list full matches alphabetically, ratings say what is or isn't documented, and the CRM check summarizes your answers instead of giving a verdict."),
]
def hub(s):
    rows = ""
    for d, c, w in LOG:
        row = f'<tr><td class="when">{d}</td><td>{c}</td><td>{w}</td></tr>'
        if w[:60] not in s:
            rows += row
    if rows:
        s = s.replace("<tbody><tr><td class=\"when\">", "<tbody>" + rows + "<tr><td class=\"when\">", 1)
    s = re.sub(r"<span>Updated [A-Z][a-z]+ \d{1,2}, \d{4} · <a href=\"#changelog\">", f"<span>Updated {TODAY} · <a href=\"#changelog\">", s, count=1)
    s = s.replace('<span class="card-meta">Reviewed October 2026</span>', f'<span class="card-meta">Reviewed October 2026 · checked {TODAY}</span>')
    return s
rw("compare/index.html", hub)
def fixes_log(s):
    if "CHANGELOG = [  # newest first" not in s: sys.exit("fixes: CHANGELOG not found")
    add = "".join(f"    ({json.dumps(d)}, {json.dumps(c)}, {json.dumps(w, ensure_ascii=False)}),\n" for d, c, w in LOG if w[:60] not in s)
    return s.replace("CHANGELOG = [  # newest first: (date, comparison, what changed)\n", "CHANGELOG = [  # newest first: (date, comparison, what changed)\n" + add, 1) if add else s
rw("_tools/site/fixes_2026_10_20.py", fixes_log)
rw("_tools/site/fixes_2026_10_20.py", lambda s: s.replace('"/compare/ats/": "Reviewed October 2026", "/compare/crm/": "Reviewed October 2026", "/compare/match/": "Reviewed October 2026"',
    f'"/compare/ats/": "Reviewed October 2026 · checked {TODAY}", "/compare/crm/": "Reviewed October 2026 · checked {TODAY}", "/compare/match/": "Reviewed October 2026 · checked {TODAY}"'))

# ================================================================ the current Briefing (week of November 2)
SHORT = ["Dayforce buys AI interviewer Ribbon AI; Gap rolls out an AI hiring guide",
         "Gartner: 3% of organizations beat their AI cost-savings goals through productivity",
         "Gartner: one in four candidates may be represented by an AI agent by 2029",
         "Goldman: workers displaced from AI-exposed jobs take about a month longer to find work",
         "PwC confirms a vendor breach exposed employee learning records",
         "Colorado's AI rules still pending; California's 2027 workplace-AI laws read as one checklist"]
def briefing(s):
    n = [0]
    def tag(m):
        i = n[0]; n[0] += 1
        if "data-short=" in m.group(0) or i >= len(SHORT): return m.group(0)
        return m.group(0)[:-1] + f' data-short="{SHORT[i]}">'
    s = re.sub(r'<article class="brief-item"[^>]*>', tag, s)
    s = pairs([
        ("so decide your position before a vendor decides it for you.", "so it may be worth settling your position before a vendor release settles it for you."),
        ('<a href="https://www.hrdive.com/news/gap-ai-hiring-tool-bridgette/873179/" target="_blank" rel="noopener">HR Dive (Gap)</a></p>',
         '<a href="https://www.hrdive.com/news/gap-ai-hiring-tool-bridgette/873179/" target="_blank" rel="noopener">HR Dive (Gap)</a> · '
         '<a href="https://www.hr-brew.com/stories/dayforce-closes-deal-to-acquire-ai-interviewing-platform-ribbon" target="_blank" rel="noopener">HR Brew (closing)</a></p>'),
    ])(s)
    note = ('<p class="update-note"><strong>Update, November 7, 2026:</strong> HR Brew reported on November 5 that Dayforce has closed the Ribbon acquisition; '
            'terms and the closing date were not disclosed.</p>\n          ')
    if "update-note" not in s:
        anchor = "The article describes no bias testing or formal human-review safeguards.</p>\n          "
        if s.count(anchor) != 1: sys.exit("briefing: update anchor not found")
        s = s.replace(anchor, anchor + note, 1)
    s = re.sub(r"<span>Updated November \d{1,2}, 2026</span><span>Refreshed weekly</span>", f"<span>Updated {TODAY}</span><span>Refreshed weekly</span>", s, count=1)
    return s
rw("briefing/index.html", briefing)
rw("assets/site.css", lambda s: s if ".update-note" in s else s.rstrip("\n") + "\n.update-note { border-left: 3px solid var(--amber); padding: .5rem .8rem; background: var(--amber-soft); font-size: var(--text-sm); margin: .6rem 0; }\n")

# ================================================================ Insights (article data and builder)
rw("_tools/regional/articles.py", pairs([
    ("cover calendar-year 2026, which ends in eleven weeks.", "cover calendar-year 2026, which ends on December 31, 2026."),
    ("Greece followed, with its main provisions taking effect on November 1.", "Greece followed; its main provisions took effect on November 1, 2026."),
]))
AMER_NOTE = ("<strong>Update, November 7, 2026:</strong> On October 16, 2026 the EEOC sent a final rule rescinding the Uniform Guidelines, "
             "including the 80% benchmark, to White House review, projecting a January 2027 effective date. Colorado's Attorney General held "
             "the rulemaking hearing on October 26, 2026; the law requires final rules before January 1, 2027.")
EU_NOTE = ("<strong>Update, November 7, 2026:</strong> Greece's main provisions took effect on November 1, 2026, and the standfirst now gives "
           "the end of the reporting year as a date (December 31, 2026) instead of a countdown.")
def articles(s):
    for slug, note, srcs in (("americas-ai-hiring-notice-2027", AMER_NOTE, [("Ogletree Deakins: EEOC sends Uniform Guidelines rescission to OIRA", OGLE), ("Colorado Attorney General: rulemaking", "https://coag.gov/ai/")]),
                             ("eu-pay-transparency-2026-payroll", EU_NOTE, [])):
        i = s.find(f'slug="{slug}"')
        if i < 0: sys.exit(f"articles: {slug} not found")
        if f'updated="{TODAY}"' in s[i:i + 200]:
            continue
        s = s[:i] + f'slug="{slug}", updated="{TODAY}", note={json.dumps(note)},' + s[i + len(f'slug="{slug}",'):]
        if srcs:
            j = s.find("sources=[", i)
            add = "".join(f"({json.dumps(t)}, {json.dumps(u)}), " for t, u in srcs)
            s = s[:j + len("sources=[")] + add + s[j + len("sources=["):]
    return s
rw("_tools/regional/articles.py", articles)
rw("_tools/regional/build_articles.py", pairs([
    ('"datePublished": "2026-10-16", "dateModified": "2026-10-16",',
     '"datePublished": "2026-10-16", "dateModified": a.get("updated_iso", "2026-10-16") if a.get("updated") else "2026-10-16",'),
    ('<span>October 16, 2026</span><span>{a["minutes"]} min read</span></div>',
     '<span>October 16, 2026</span>{(\'<span>Updated \' + a["updated"] + \'</span>\') if a.get("updated") else ""}<span>{a["minutes"]} min read</span></div>'),
    ('<div class="prose-wrap prose">{a["body"]}',
     '<div class="prose-wrap prose">{(chr(10) + \'    <p class="update-note">\' + a["note"] + \'</p>\') if a.get("note") else ""}{a["body"]}'),
]))
rw("_tools/regional/articles.py", lambda s: s.replace(f'updated="{TODAY}", note=', f'updated="{TODAY}", updated_iso="{TODAY_ISO}", note=') if "updated_iso" not in s else s)

# ================================================================ About anchor, Privacy date
rw("about/index.html", lambda s: s.replace("    <h2>The method</h2>", '    <h2 id="method">The method</h2>', 1))
rw("privacy/index.html", lambda s: re.sub(r"<span>Updated November \d{1,2}, 2026</span>", f"<span>Updated {TODAY}</span>", s, count=1))

print(f"{len(changed)} files changed", *sorted(set(changed)), sep="\n  ")
