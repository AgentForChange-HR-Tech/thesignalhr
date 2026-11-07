"""Voice pass (November 2026): applies GUARDRAILS.md section 2 (practitioner to practitioner) and the AI-assistance
note to the site copy, then rebuilds the comparison pages. Run from the repo root:
    python3 -B _tools/site/voice_2026_11.py
Idempotent. Edits the sources (page copy, build scripts, kits script) so rebuilds keep the changes.
Archived Briefing editions keep their published text; only the shared signup band changes there.
"""
import glob, os, subprocess, sys
changed = []

def rw(path, fn):
    if not os.path.exists(path):
        print("skip (missing):", path); return
    s = open(path, encoding="utf-8", newline="").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)

def pairs(items, required=True):
    def fn(s):
        for old, new in items:
            if old in s:
                s = s.replace(old, new)
            elif new and new in s:
                continue          # already applied
            elif required:
                sys.exit(f"can't find {old[:90]!r}")
        return s
    return fn

def insert_before(anchor, block, sentinel):
    def fn(s):
        if sentinel in s:
            return s
        if anchor not in s:
            sys.exit(f"anchor not found: {anchor[:80]!r}")
        return s.replace(anchor, block + anchor, 1)
    return fn

AI_SPAN = '<span><a href="/about/#ai">AI-assisted</a></span>'

# ---------------------------------------------------------------- signup band on every page (site chrome)
BAND = [
    ("<h2>Walk into Monday <em>already knowing</em>.</h2>", "<h2>Get the signal <em>each week</em>.</h2>"),
    ("The weekly signal: what changed in HR tech, what it means, what to do. Free forever.",
     "The weekly signal: what changed in HR tech, what it may mean, and what to check. Free forever."),
    ("Launch news goes to the newsletter first, along with the weekly signal: what changed in HR tech, what it means, what to do. Free forever.",
     "Launch news goes to the newsletter first, along with the weekly signal: what changed in HR tech, what it may mean, and what to check. Free forever."),
]
for f in sorted(glob.glob("**/*.html", recursive=True)):
    if not f.startswith(("_", ".")):
        rw(f, pairs(BAND, required=False))

# ---------------------------------------------------------------- home
rw("index.html", pairs([
    ("a weekly briefing, honest vendor comparisons where no vendor pays,", "a weekly briefing, sourced vendor comparisons where no vendor pays,"),
    ("Not the news — what the news means, and what to do about it.",
     "What changed in HR tech, what it may mean, and what to check, with every source linked."),
    ("One practitioner-curated briefing across the HR landscape — so you walk into every decision already knowing what changed, what it means, and what to do about it.",
     "One practitioner-curated briefing across the HR landscape: what changed, what it may mean, and the questions worth asking, with every source linked so you can check it yourself."),
    (">Compare HR tech honestly</a>", ">Compare HR tech side by side</a>"),
    ("What changed in HR tech this week, what it means, and the one thing worth doing about it. Every week, free.",
     "What changed in HR tech this week, what it may mean, and what to check. Every week, free."),
    ('<h2>Most "best HR software" lists are affiliate pages in disguise. This isn\'t.</h2>',
     "<h2>HR tech, side by side, with every claim sourced.</h2>"),
    ("<p>Honest, side-by-side HR tech comparisons built by someone who has actually run enterprise migrations — not someone collecting referral fees. No vendor pays",
     "<p>Comparisons that describe what each platform documents, with sources and review dates, from a practitioner who has run enterprise HR migrations. No vendor pays"),
    ("Everything that decides HR's <em>next decade</em>", "Ten areas shaping HR's <em>next decade</em>"),
    ("Curated by a practitioner, <em style=\"color:var(--signal);\">not an algorithm</em>.",
     "Curated by a practitioner, <em style=\"color:var(--signal);\">for practitioners</em>."),
    ("Every item is read, judged, and placed in context before it reaches you. Not the news — what the news <em>means</em>, and what to do about it.",
     "AI tools help with research, drafting and source checks, and Alex reviews and approves every update before it's published "
     "(<a href=\"/about/#ai\">how AI helps</a>). It's one practitioner's read, with the sources linked so you can check them and draw your own conclusions."),
    ("→ <strong>Judgment included</strong> — every story carries a \"so what\" for HR leaders.",
     "→ <strong>Context included</strong> — every story carries a \"so what\": what it may mean in practice and what to check."),
    ("Join HR leaders who get the weekly signal: what changed, what it means, what to do. Free forever.",
     "The weekly signal: what changed, what it may mean, and what to check. Free forever."),
]))

# ---------------------------------------------------------------- about
rw("about/index.html", pairs([
    ("<h1>Curated by a practitioner, not an <em style=\"color:var(--signal);\">algorithm</em>.</h1>",
     "<h1>Curated by a practitioner, <em style=\"color:var(--signal);\">for practitioners</em>.</h1>"),
    ("The Signal exists because HR leaders don't need more news. They need to know what the news means — from someone with no vendor to please.",
     "The Signal is a resource for HR practitioners: what's changing in HR technology, AI and regulation, with the sources linked and one practitioner's notes on what it may mean."),
    ("running migrations, rescuing broken implementations,", "running migrations, fixing broken implementations,"),
    ("That experience is the filter: every item in The Signal has been read, judged, and placed in context by someone who has sat on the buyer's side of the table.",
     "That experience shapes what gets covered and the questions each item raises. It isn't the final word: every item links its sources so you can check them, "
     "and readers who know more are invited to say so."),
    ("One weekly briefing and occasional deep analysis — not thirty daily alerts competing for your anxiety.",
     "One weekly briefing and occasional longer analysis, not a stream of daily alerts."),
    ("<strong>Judgment included.</strong> Every story carries a \"so what\" for HR leaders. If we can't say why it matters, it doesn't run.",
     "<strong>Context included.</strong> Every story carries a \"so what\": what it may mean in practice and what to check. It's one practitioner's read, labeled as analysis, not the final word."),
    ("Items make the cut on three tests: <em>Is it real</em> (verifiable, sourced, not vendor theater)? <em>Does it change a decision</em> an HR leader has to make? <em>Can we add judgment</em> beyond restating it? Every briefing item links its sources, and every page shows when it was last updated.",
     "Items make the cut on three tests: <em>Can it be verified</em> in a source we've opened? <em>Is it likely to matter</em> to the work HR teams are doing? "
     "<em>Can we add useful context</em> beyond restating it? Every briefing item links its sources, and every page shows when it was last updated. "
     "Each update goes through automated checks and a separate source-by-source fact-check before Alex approves it."),
    ('or <a href="https://www.linkedin.com/in/alexrivera1/" target="_blank" rel="noopener">message on LinkedIn</a>.</p>',
     'or <a href="https://www.linkedin.com/in/alexrivera1/" target="_blank" rel="noopener">message on LinkedIn</a>. '
     "Context and different views from other practitioners are welcome too.</p>"),
]))
rw("about/index.html", insert_before("    <h2>Corrections</h2>",
    '    <h2 id="ai">How AI helps</h2>\n'
    "    <p>AI tools help with the work behind The Signal: scanning sources for updates, drafting first versions of Briefing items, "
    "analysis and comparison profiles, and running a separate check of each claim against its cited source. AI can get things wrong, "
    "so every claim links to a source you can open, and Alex reviews and approves every update before it's published. Nothing publishes automatically.</p>\n",
    'id="ai"'))

# ---------------------------------------------------------------- briefing (the current edition; the writer carries it forward)
rw("briefing/index.html", pairs([
    ("Six signals worth your attention, each with the practitioner's \"so what.\" Read in five minutes; sound informed for a week.",
     "Six signals from the week, each with a practitioner's \"so what.\" About a five-minute read."),
    ("<span>Curated by Alex Rivera</span><span>Updated", "<span>Curated by Alex Rivera</span>" + AI_SPAN + "<span>Updated"),
]))

# ---------------------------------------------------------------- insights
rw("insights/index.html", pairs([
    ("<h1>Not the news. What the news <em style=\"color:var(--signal);\">means</em>.</h1>",
     "<h1>Longer reads on <em style=\"color:var(--signal);\">what's changing</em>.</h1>"),
    ("Longer-form analysis for decisions you can't get wrong — regulation, operating models, and the vendor market — across the Americas, EMEA and Asia-Pacific.",
     "Longer-form analysis of regulation, operating models and the vendor market across the Americas, EMEA and Asia-Pacific. Each piece is one practitioner's read, with every source linked."),
]))
def byline(s):
    by = "<span>By Alex Rivera</span>"
    while by + AI_SPAN in s:          # normalize, so the note appears exactly once
        s = s.replace(by + AI_SPAN, by)
    return s.replace(by + "<span>", by + AI_SPAN + "<span>")
for f in sorted(glob.glob("insights/*/index.html")) + ["_tools/regional/build_articles.py"]:
    rw(f, byline)

# ---------------------------------------------------------------- coverage
rw("coverage/index.html", pairs([
    ("Everything that decides HR's next decade, tracked continuously and filtered through one practitioner's judgment.",
     "Ten areas shaping HR's next decade, tracked weekly from one practitioner's point of view."),
    ("We track vendor claims against deployed reality — which agents complete work, which are chatbots in a trench coat.",
     "We separate what vendors have shipped from what they've announced, including which agents complete work on their own and which assist a person."),
]))

# ---------------------------------------------------------------- comparison hub
rw("compare/index.html", pairs([
    ("Honest, side-by-side HR technology comparisons built by a practitioner, not an affiliate site. ATS platforms live now; HRIS/HCM, payroll, and L&D to follow.",
     "Side-by-side HR technology comparisons built by a practitioner, with every claim sourced. ATS platforms, recruiting CRMs and applicant match scores are live; HRIS/HCM, payroll, and L&D to follow."),
    ("HR tech, compared <em style=\"color:var(--signal);\">honestly</em>.", "HR tech, compared <em style=\"color:var(--signal);\">side by side</em>."),
    ("Most \"best HR software\" lists are affiliate pages in disguise. This isn't. A practitioner's buyer's lens — built by someone who has run enterprise migrations, not someone collecting referral fees.",
     "Each comparison describes what platforms document, with sources and review dates, so you can check every claim and weigh it against your own requirements."),
    ("check what will really set your go-live date,", "check what tends to set a go-live date,"),
    ("compared on what actually drives cost and lock-in.", "compared on cost and lock-in."),
    ("drawn from hands-on enterprise systems experience, cross-checked against current analyst and review sources.",
     "drawn from hands-on enterprise systems experience, with every claim linked to its source."),
    ("because stale advice is worse than none.", "because products and rules change."),
]))

# ---------------------------------------------------------------- comparison builders (pages are rebuilt below)
rw("_tools/ats/build_ats.py", pairs([
    ("and check what will really set your go-live date. No vendor pays.", "and check what tends to set a go-live date. No vendor pays."),
    ("ATS platforms, compared for the decision you're <em style=\"color:var(--signal);\">actually</em> making.",
     "ATS platforms, compared for <em style=\"color:var(--signal);\">the decision you're making</em>."),
    ("and check what will really set your go-live date, from vendor selection onward.", "and check what tends to set a go-live date, from vendor selection onward."),
    ("Questions that separate demo theater from deployed reality. Ask them in this order; the discomfort is diagnostic.",
     "Questions to take into demos, to see how a platform works in production as well as in the demo."),
    ("<span>Independent · unsponsored</span></div>", "<span>Independent · unsponsored</span>" + AI_SPAN + "</div>"),
]))
rw("_tools/crm/build_crm.py", pairs([
    ("Most ATS platforms and HCM suites now include a CRM, and many teams already pay for one they barely use.",
     "Many ATS platforms and HCM suites now include CRM features, so a team may already license one."),
    ("Questions that separate a demo's best campaign from what your recruiters will do on a Tuesday. The discomfort is diagnostic.",
     "Questions to see how campaigns would run day to day, not only in a demo."),
    ("<span>Independent · unsponsored</span></div>", "<span>Independent · unsponsored</span>" + AI_SPAN + "</div>"),
]))
rw("_tools/match/build_match.py", pairs([
    ("A match score is the AI feature most often switched on without a review, and the one hiring-AI rules are written about.",
     "A match score can arrive in a product release without a separate purchase or review, and many hiring-AI rules are written with scores like these in mind."),
    ("Scores are now in most recruiting stacks, often switched on in a release rather than bought.",
     "Scores are now common in recruiting platforms, and they can be switched on in a release rather than bought."),
    ("If the vendor can't answer them, you won't be able to either.", "A vendor's answers show how much of a score you'd be able to explain yourself."),
    ("<span>Independent · unsponsored</span></div>", "<span>Independent · unsponsored</span>" + AI_SPAN + "</div>"),
]))

# ---------------------------------------------------------------- kits (page and the script that builds it)
KITS = [("A monthly update: what changed where you hire, and what to do", "A monthly update: what changed where you hire, and what to check")]
rw("kits/index.html", pairs(KITS))
rw("_tools/site/kits.py", pairs(KITS + [
    ('replace("<h2>Walk into Monday <em>already knowing</em>.</h2>",', 'replace("<h2>Get the signal <em>each week</em>.</h2>",'),
    ("along with the weekly signal: what changed in HR tech, what it means, what to do. Free forever.",
     "along with the weekly signal: what changed in HR tech, what it may mean, and what to check. Free forever."),
]))
rw("_tools/site/search_index.py", pairs([("_tools/GUARDRAILS.md, section 6).", "_tools/GUARDRAILS.md, section 7).")], required=False))

# ---------------------------------------------------------------- rebuild the comparison pages from their sources
def run(cmd):
    r = subprocess.run([sys.executable, "-B"] + cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    return r.stdout.strip()
print(run(["_tools/ats/build_ats.py", "compare/ats/index.html", "compare/ats/index.html"]))
print(run(["_tools/crm/build_crm.py", "compare/ats/index.html", "compare/crm/index.html"]))
print(run(["_tools/match/build_match.py", "compare/ats/index.html", "compare/match/index.html"]))
print(f"{len(changed)} source files changed", *changed, sep="\n  ")
