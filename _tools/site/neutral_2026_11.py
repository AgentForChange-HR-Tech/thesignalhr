"""Neutral-language pass (November 2026): applies GUARDRAILS.md section 1 (inform, don't persuade) to the
comparison tools and site copy, then rebuilds the comparison pages. Run from the repo root:
    python3 -B _tools/site/neutral_2026_11.py
Idempotent. Edits the sources (build scripts, tool scripts, data) so rebuilds keep the changes.
"""
import os, re, subprocess, sys
changed = []

def edit(path, pairs):
    if not os.path.exists(path):
        print("skip (missing):", path); return
    s = open(path, encoding="utf-8", newline="").read()
    t = s
    for old, new in pairs:
        if new and new in t and old not in t:
            continue            # already applied
        if old not in t:
            sys.exit(f"{path}: can't find {old[:80]!r}")
        t = t.replace(old, new)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)

NO_RECS = ('<li><strong>No recommendations.</strong> We describe what each platform documents. We don\'t rank platforms or tell you '
           'which to choose: the finder only shows which platforms match the filters you pick.</li>')
def add_no_recs(path):
    s = open(path, encoding="utf-8", newline="").read()
    if "No recommendations.</strong>" in s:
        return
    m = re.search(r'(<li><strong>No vendor pays\.</strong>.*?</li>)', s, flags=re.S)
    if not m:
        sys.exit(f"{path}: method list not found")
    s = s[:m.end()] + "\n        " + NO_RECS + s[m.end():]
    open(path, "w", encoding="utf-8", newline="").write(s)
    changed.append(path)

PBEST_OLD = '<p class="pbest"><strong>Best for:</strong> {E(p["best"])} <strong>Not for:</strong> {E(p["notfor"])}</p>'
PBEST_NEW = '<p class="pbest"><strong>Typical use:</strong> {E(p["best"])}</p>'
SORT_OLD = """    var byScore = function (a, b) { return b[1].score - a[1].score || a[0].name.localeCompare(b[0].name); };
    strong.sort(byScore); partial.sort(byScore);"""
SORT_NEW = """    // no ranking: full matches alphabetically; partial matches by fewest gaps, then alphabetically
    var alpha = function (a, b) { return a[0].name.localeCompare(b[0].name); };
    strong.sort(alpha); partial.sort(function (a, b) { return a[1].gaps.length - b[1].gaps.length || alpha(a, b); });"""
GROUPS = [("<h3 class=\"group\">Strong fits</h3>", "<h3 class=\"group\">Matches all your filters</h3>"),
          ("<h3 class=\"group\">Possible fits, with gaps</h3>", "<h3 class=\"group\">Matches some of your filters</h3>")]
ROWS = [('    h += row("Best for", function (p) { return esc(p.best); });\n    h += row("Not for", function (p) { return esc(p.notfor); });\n',
         '    h += row("Typical use", function (p) { return esc(p.best); });\n')]

# ---------------- ATS
edit("_tools/ats/build_ats.py", [
    ('0: ("Not a strength", "lv-0")', '0: ("Not documented", "lv-0")'),
    (PBEST_OLD, PBEST_NEW),
    ('"not a strength" means we found no strong evidence, so ask.', '"not documented" means we found no published evidence, so ask: it may exist.'),
])
add_no_recs("_tools/ats/build_ats.py")
edit("_tools/ats/ats.js", [('0: "Not a strength" }', '0: "Not documented" }'), (SORT_OLD, SORT_NEW)] + GROUPS + ROWS)

# ---------------- CRM
edit("_tools/crm/build_crm.py", [
    ('0: ("Not a strength", "lv-0")', '0: ("Not documented", "lv-0")'),
    (PBEST_OLD, PBEST_NEW),
    ('"not a strength" means we found no strong evidence, so ask.', '"not documented" means we found no published evidence, so ask: it may exist.'),
    ("A separate CRM pays off when there is enough pipeline work to do and someone to do it. Answer what you know; the verdict, the capabilities to prioritize and your question list build below.",
     "Whether a separate CRM adds anything depends on how much pipeline work there is and who would run it. Answer what you know; a summary of your answers, the capabilities they point to and your question list build below."),
    ("<h3>Your verdict</h3>", "<h3>What your answers show</h3>"),
    ('to see a verdict.</p></div>', 'to see a summary.</p></div>'),
])
add_no_recs("_tools/crm/build_crm.py")
edit("_tools/crm/crm.js", [
    ('0: "Not a strength" }', '0: "Not documented" }'), (SORT_OLD, SORT_NEW),
    ('to see a verdict.', 'to see a summary.'),
    ("Capabilities to prioritize:", "Capabilities your answers point to:"),
    ('{ cls: "v-own", t: "Start with the CRM you already license", d: "Pilot it on one hiring program with a named campaign owner before buying another. Where it falls short, the gaps tell you which capabilities to shortlist on." }',
     '{ cls: "v-own", t: "You already license CRM features", d: "Your answers say your ATS or suite includes CRM features. Comparing what they cover with the capabilities below shows where any gaps are." }'),
    ('{ cls: "v-low", t: "The CRM features in your ATS are probably enough", d: "Talent pools, saved searches and basic email cover occasional pipelining. Revisit when repeat roles, events or hard-to-fill roles grow." }',
     '{ cls: "v-low", t: "Your answers describe occasional pipeline needs", d: "Talent pools, saved searches and basic email in most ATS platforms cover occasional pipelining. Needs grow with repeat roles, events and hard-to-fill roles." }'),
    ('{ cls: "v-gaps", t: "A CRM could pay off, but close the gaps first", d: "Without a campaign owner, clean data and a working ATS sync, a CRM becomes an expensive database. Fix the major gaps below before you buy." }',
     '{ cls: "v-gaps", t: "Your answers show readiness gaps", d: "Any CRM depends on a campaign owner, clean data and a working ATS sync. The gaps below are the ones your answers flagged." }'),
    ('{ cls: "v-buy", t: "A dedicated CRM is likely worth evaluating", d: "Shortlist in Step 2 with the capabilities below, check the CRM inside your ATS or suite first, and take the questions into demos." }',
     '{ cls: "v-buy", t: "Your answers describe sustained pipeline needs", d: "The capabilities below match the needs you described. Step 2 filters platforms by them, including the CRM inside your ATS or suite, and the questions are there for demos." }'),
] + GROUPS + ROWS)
edit("_tools/crm/data.py", [("The strongest published governance package here: ISO/IEC 42001", "Published governance evidence: ISO/IEC 42001")])

# ---------------- applicant match
edit("_tools/match/build_match.py", [
    (PBEST_OLD, PBEST_NEW),
    ("the capabilities to insist on and the questions for your vendor build below.", "the capabilities these rules point to and the questions for your vendor build below."),
])
add_no_recs("_tools/match/build_match.py")
edit("_tools/match/match.js", [(SORT_OLD, SORT_NEW), ("Capabilities to insist on:", "Capabilities these rules point to:")] + GROUPS + ROWS)

# ---------------- site copy
edit("about/index.html", [
    ("No sponsorships, no affiliate links, no pay-to-rank. If a comparison says a platform is heavy and costly to change, that's because it is.</li>",
     "No sponsorships, no affiliate links, no pay-to-rank. Comparisons describe what each platform documents, including what's costly to change, and every claim links to its source.</li>\n"
     "      <li><strong>Inform, never persuade.</strong> We explain what changed and what each platform documents. We don't rank vendors or tell you which product to buy; that decision is yours.</li>"),
])
for f in ("insights/apac-automated-hiring-clock/index.html", "_tools/regional/articles.py"):
    edit(f, [("and the first date is eight weeks away.", "and the first date is December 10, 2026.")])

# ---------------- rebuild the comparison pages from their sources
def run(cmd):
    r = subprocess.run([sys.executable, "-B"] + cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    return r.stdout.strip()
print(run(["_tools/ats/build_ats.py", "compare/ats/index.html", "compare/ats/index.html"]))
print(run(["_tools/crm/build_crm.py", "compare/ats/index.html", "compare/crm/index.html"]))
print(run(["_tools/match/build_match.py", "compare/ats/index.html", "compare/match/index.html"]))
print(f"{len(changed)} source files changed", *changed)
