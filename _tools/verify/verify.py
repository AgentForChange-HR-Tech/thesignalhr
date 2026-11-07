"""The Signal HR: automated pre-publish validators (Gate 2 in _tools/PUBLISHING.md).
Run from the repo root before every commit and push:
    python3 -B _tools/verify/verify.py              # report to the screen and _tools/verify/last-report.md
    python3 -B _tools/verify/verify.py --today 2026-11-09
Exit code 1 if any ERROR: do not publish until it's fixed. WARNINGs need a human look.
Standard library only. Checks:
  structure    one h1, title, description, canonical = og:url, JSON-LD parses, internal links and sitemap resolve
  sources      every Briefing signal, Insight, platform profile and rules-check place cites a source
  guardrails   no persuading or ranking language in our voice (GUARDRAILS.md section 1); no relative dates
  voice        practitioner to practitioner: no superlatives about ourselves, swipes at others or know-it-all framing (section 2)
  privacy      analytics only through the consent loader, a Cookie settings link on every page, no Google Fonts (section 5)
  dates        stale "Verified" dates, "from <date>" statements whose date has passed, future "Updated" dates
  consistency  platform and place counts quoted on the Hub, homepage and Coverage match the data
  watchlist    time-sensitive facts whose recheck date has arrived (watchlist.json)
  reputation   no employer or internal references, placeholders or stray email addresses
  search       search index matches the published Briefing signals
"""
import argparse, datetime as dt, glob, html, json, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--today", default=dt.date.today().isoformat())
ap.add_argument("--quiet", action="store_true")
args = ap.parse_args()
TODAY = dt.date.fromisoformat(args.today)
HERE = os.path.dirname(os.path.abspath(__file__))
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                       "September", "October", "November", "December"], start=1)}
findings = []  # (level, check, where, message)
def err(check, where, msg): findings.append(("ERROR", check, where, msg))
def warn(check, where, msg): findings.append(("WARNING", check, where, msg))

PAGES = sorted(f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("_", ".")))
RAW = {f: open(f, encoding="utf-8").read() for f in PAGES}
def url_of(path):
    u = "/" + path.replace(os.sep, "/")
    return u[: -len("index.html")] if u.endswith("index.html") else u
def strip(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()
def visible(raw):
    """Text a reader can see, plus string content rendered by inline scripts (labels built in JS)."""
    s = re.sub(r"<style.*?</style>", " ", raw, flags=re.S)
    s = re.sub(r"<script[^>]*src=[^>]*></script>", " ", s)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', " ", s, flags=re.S)
    s = re.sub(r"<(head)\b.*?</\1>", " ", s, flags=re.S)
    return re.sub(r"https?://\S+", " ", strip(s))
def is_archive(f): return "/archive/" in "/" + f.replace(os.sep, "/")
def page_json(raw):
    m = re.search(r'<script type="application/json" id="ats-data">(.*?)</script>', raw, flags=re.S)
    return json.loads(m.group(1).replace("<\\/", "</")) if m else None
def parse_date(s):
    m = re.match(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", s)
    if m and m.group(1) in MONTHS:
        return dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))
    return None

# ---------------------------------------------------------------- structure
for f, raw in RAW.items():
    if f == "404.html":
        continue
    h1 = len(re.findall(r"<h1[\s>]", raw))
    if h1 != 1: err("structure", f, f"{h1} h1 elements (need exactly 1)")
    if not re.search(r"<title>[^<]{5,}</title>", raw): err("structure", f, "missing <title>")
    if not re.search(r'<meta name="description" content="[^"]{20,}"', raw): err("structure", f, "missing meta description")
    can = re.search(r'<link rel="canonical" href="([^"]+)"', raw)
    og = re.search(r'<meta property="og:url" content="([^"]+)"', raw)
    if not can: err("structure", f, "missing canonical link")
    elif og and can.group(1) != og.group(1): err("structure", f, "canonical and og:url differ")
    elif can.group(1) != "https://thesignalhr.com" + url_of(f): err("structure", f, f"canonical {can.group(1)} doesn't match the page's address")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, flags=re.S):
        try: json.loads(block)
        except ValueError as e: err("structure", f, f"JSON-LD doesn't parse: {e}")
    for href in re.findall(r'href="(/[^"#?]*)', raw):
        p = href.lstrip("/")
        if p and not any(os.path.isfile(c) for c in [p, os.path.join(p, "index.html")]):
            err("structure", f, f"internal link {href} goes nowhere")
    if re.search(r'href=""|href="#"(?![^>]*id=)', raw) and "ats-expand" not in raw:
        warn("structure", f, "empty link target")
if os.path.exists("sitemap.xml"):
    sm = open("sitemap.xml", encoding="utf-8").read()
    locs = re.findall(r"<loc>https://thesignalhr\.com(/[^<]*)</loc>", sm)
    for loc in locs:
        p = loc.lstrip("/")
        if not any(os.path.isfile(c) for c in [p, os.path.join(p, "index.html")] if c):
            err("structure", "sitemap.xml", f"{loc} is listed but the page doesn't exist")
    for f in RAW:
        if f != "404.html" and url_of(f) not in locs:
            warn("structure", "sitemap.xml", f"{url_of(f)} isn't in the sitemap")

# ---------------------------------------------------------------- sources
for f, raw in RAW.items():
    blocks = re.findall(r'<article class="brief-item"[^>]*>(.*?)</article>', raw, flags=re.S)
    if f.replace(os.sep, "/") == "briefing/archive/index.html":
        blocks = []   # the archive index lists editions, not signals
    for i, block in enumerate(blocks, start=1):
        src = re.search(r'<p class="src">(.*?)</p>', block, flags=re.S)
        if not src or not re.search(r'href="https?://', src.group(1)):
            err("sources", f"{f} signal {i}", "Briefing signal has no source link")
        if not re.search(r'<div class="so-what">', block): err("sources", f"{f} signal {i}", "Briefing signal has no So what")
    if re.match(r"insights/[^/]+/index\.html$", f.replace(os.sep, "/")):
        if not re.search(r'class="sources".*?href="https?://', raw, flags=re.S):
            err("sources", f, "Insight has no Sources list")
    for pid, block in re.findall(r'<details class="profile" id="p-([a-z0-9-]+)">(.*?)</details>', raw, flags=re.S):
        if not re.search(r'Sources?:.*?href="https?://', block, flags=re.S):
            err("sources", f"{f} #p-{pid}", "platform profile has no source link")
    d = page_json(raw)
    if d and d.get("juris"):
        for j in d["juris"]:
            if not (j.get("src") and str(j["src"][1]).startswith("https://")):
                err("sources", f"{f} rules: {j.get('name')}", "rules-check place has no https source")
    for u in re.findall(r'href="(http://[^"]+)"', raw):
        warn("sources", f, f"insecure source link {u}")

# ---------------------------------------------------------------- guardrails language (section 1: inform, don't persuade)
PERSUADE = [
    (r"\bbest for\b", "\"Best for\" ranks products; describe what the vendor says it's designed for"),
    (r"\bnot for:", "\"Not for\" steers readers away; state the documented limitation instead"),
    (r"\bstrong fits?\b", "\"Strong fit\" is a verdict; say \"matches all your filters\""),
    (r"\bpossible fits\b", "\"Possible fits\" is a verdict; say \"matches some of your filters\""),
    (r"\b(top pick|clear winner|clear choice|best-in-class|best in class|market leader)\b", "ranking language in our voice"),
    (r"\bwe (recommend|suggest you (buy|choose))\b", "a product recommendation in our voice"),
    (r"\b(you|teams|buyers|hr leaders) should (buy|choose|pick|select|switch to|avoid|replace)\b", "telling readers which product to choose"),
    (r"\b(likely|probably) worth (evaluating|buying)\b", "a buying verdict"),
    (r"\bbefore you buy\b", "a buying instruction"),
    (r"\bthe (strongest|weakest|best|worst) (published |documented )?(governance|platform|product|option|vendor|choice|package)", "comparative ranking of vendors"),
    (r"\binsist on\b", "pressuring language; say what the rules point to"),
    (r"\bnot a strength\b", "an evaluative rating; say what is or isn't documented"),
]
ATTRIB = re.compile(r"(says|said|claims|named|according to|calls itself|describes)\W+(?:\w+\W+){0,8}$", re.I)
RELATIVE = [r"\bdays away\b", r"\bweeks away\b", r"\bnext month\b", r"\blater this year\b", r"\bearly next year\b"]
for f, raw in RAW.items():
    text = visible(raw)
    for pat, why in PERSUADE:
        for m in re.finditer(pat, text, flags=re.I):
            before = text[max(0, m.start() - 80):m.start()]
            if ATTRIB.search(before):
                continue  # attributed to the vendor or a third party
            where = f"{f}: …{text[max(0, m.start() - 40):m.end() + 40]}…"
            (warn if is_archive(f) else err)("guardrails", where, why)
            break  # one finding per pattern per page is enough; the report shows the count
    if not is_archive(f) and not f.startswith("briefing/"):
        for pat in RELATIVE:
            for m in re.finditer(pat, text, flags=re.I):
                if re.search(r"originally read", text[max(0, m.start() - 120):m.start()]):
                    continue  # a correction note quoting the old wording
                warn("guardrails", f"{f}: …{text[max(0, m.start() - 40):m.end() + 40]}…", "relative date; use an absolute date")
                break
    for m in re.finditer(r"\b(market|category|clear|undisputed) leaders?\b|\b(a|the) leader in\b|\blaggards?\b", text, flags=re.I):
        before = text[max(0, m.start() - 80):m.start()]
        if not re.search(r"(Gartner|Forrester|IDC|Everest|named|says|said|claims|Magic Quadrant)", before, re.I):
            warn("guardrails", f"{f}: …{text[max(0, m.start() - 40):m.end() + 30]}…", "\"leader/laggard\" must be attributed to a named third party")
            break

# ---------------------------------------------------------------- voice (section 2: practitioner to practitioner)
VOICE = [
    (r"\b(the )?most (reliable|trusted|accurate|authoritative)\b", "a superlative about ourselves; show reliability with sources, dates and corrections"),
    (r"\bdefinitive\b(?! (merger |purchase |acquisition |sale )?agreement)|\bauthoritative\b", "claims authority; The Signal is one practitioner's read"),
    (r"\bthe (benchmark|gold standard|go-to (source|resource|site))\b", "claims authority"),
    (r"\bzero (mistakes|errors)\b|\b100% (accurate|reliable|correct)\b", "promises perfection; say how errors are caught and corrected"),
    (r"\beverything you need\b|\ball you need to know\b", "over-claims completeness"),
    (r"\bin disguise\b|\b(vendor|demo) theat(er|re)\b|\btrench coat\b|\breferral fees\b", "a swipe at others; describe what we do, not what others get wrong"),
    (r"\bcompared honestly\b|\bhonest(,)? (side-by-side )?(vendor )?comparisons?\b|\bhr tech honestly\b", "implies others are dishonest"),
    (r"\bnot an algorithm\b|\bno ai (is |was )?used\b|\bwritten without ai\b|\b100% human\b|\bhuman-written\b", "AI helps with this site; the About page says how"),
    (r"\bcan't get wrong\b|\balready knowing\b|\bsound informed\b|\bwhat to do about it\b|\bdiscomfort is diagnostic\b", "know-it-all framing; offer what it may mean and what to check"),
]
VOICE_WARN = [
    (r"\b(obviously|of course|make no mistake|needless to say|simply put|the truth is|everyone knows)\b", "talks down to readers"),
    (r"\bwhat most (people|teams|hr leaders|buyers|companies) (get wrong|miss|don't know)\b", "talks down to readers"),
    (r"\byou (must|need to) (decide|act|move|buy|choose)\b|\bbefore a vendor decides\b", "an order to readers; offer it as a question or a check"),
]
for f, raw in RAW.items():
    if is_archive(f):
        continue  # archived editions stay as published
    text = visible(raw)
    for pats, report in ((VOICE, err), (VOICE_WARN, warn)):
        for pat, why in pats:
            for m in re.finditer(pat, text, flags=re.I):
                before = text[max(0, m.start() - 80):m.start()]
                if ATTRIB.search(before) or re.search(r"[\"\u201c]\S*$", before):
                    continue  # attributed or quoted
                report("voice", f"{f}: …{text[max(0, m.start() - 40):m.end() + 40]}…", why)
                break

# ---------------------------------------------------------------- privacy (section 5: analytics only with consent)
try:
    CONSENT_JS = open(os.path.join(HERE, "..", "site", "consent_head.js"), encoding="utf-8").read().strip("\n")
except OSError:
    CONSENT_JS = None
for f, raw in RAW.items():
    if not re.search(r"<head>", raw):
        continue
    raw_tag = re.search(r'<script[^>]+src="https://www\.googletagmanager\.com/', raw)
    if raw_tag:
        err("privacy", f, "analytics tag loads without the consent check: run python3 -B _tools/site/consent.py")
    m = re.search(r"<!-- >>> consent .*?<script>\n(.*?)\n</script>\n<!-- <<< consent -->", raw, flags=re.S)
    if not m and not raw_tag:
        warn("privacy", f, "no consent loader (and so no analytics): run consent.py if this page should count visits")
    elif CONSENT_JS is not None and m.group(1) != CONSENT_JS:
        err("privacy", f, "consent loader is out of date: rerun python3 -B _tools/site/consent.py")
    if "<footer" in raw and "data-consent-open" not in raw:
        err("privacy", f, "footer has no Cookie settings link: run consent.py")
    if re.search(r"fonts\.(googleapis|gstatic)\.com", raw):
        err("privacy", f, "Google Fonts sends visitors' IP addresses to Google; fonts are self-hosted in /assets/fonts")
if "privacy/index.html" in RAW and 'id="cookies"' not in RAW["privacy/index.html"]:
    err("privacy", "privacy/index.html", "the Cookies and your choice section is missing")
for css in ("assets/site.css",):
    if os.path.exists(css) and re.search(r"fonts\.(googleapis|gstatic)\.com", open(css, encoding="utf-8").read()):
        err("privacy", css, "Google Fonts import in the stylesheet")

# ---------------------------------------------------------------- dates
for f, raw in RAW.items():
    if is_archive(f):
        continue
    for mon, yr in set(re.findall(r"Verified ([A-Z][a-z]+) (\d{4})", raw)):
        if mon in MONTHS:
            age = (TODAY - dt.date(int(yr), MONTHS[mon], 1)).days
            if age > 150: err("dates", f, f"\"Verified {mon} {yr}\" is {age} days old: re-verify before publishing")
            elif age > 100: warn("dates", f, f"\"Verified {mon} {yr}\" is {age} days old: quarterly re-verification is due")
    for m in re.finditer(r"Updated ([A-Z][a-z]+ \d{1,2}, \d{4})", raw):
        d = parse_date(m.group(1))
        if d and d > TODAY + dt.timedelta(days=1): err("dates", f, f"\"Updated {m.group(1)}\" is in the future")
    d = page_json(raw)
    if d and d.get("juris"):
        for j in d["juris"]:
            for m in re.finditer(r"\b(?:from|starts?|takes effect|applies from)\s+([A-Z][a-z]+ \d{1,2}, \d{4})", j.get("status", ""), flags=re.I):
                when = parse_date(m.group(1))
                if when and when <= TODAY:
                    warn("dates", f"{f} rules: {j['name']}", f"status says \"{m.group(0)}\" but that date has passed: update to \"in force since\"")
    if f.startswith("coverage/") or f == "briefing/index.html":
        for m in re.finditer(r'<td class="when">([A-Z][a-z]{2}) (\d{1,2}), (\d{4})</td>', raw):
            mon = {k[:3]: v for k, v in MONTHS.items()}.get(m.group(1))
            if mon and dt.date(int(m.group(3)), mon, int(m.group(2))) < TODAY:
                warn("dates", f, f"calendar still lists {m.group(1)} {m.group(2)}, {m.group(3)}: rerun build_regional.py with today's date")
                break

# ---------------------------------------------------------------- consistency (numbers quoted across pages)
counts = {}
for name in ("ats", "crm", "match"):
    f = f"compare/{name}/index.html"
    if f in RAW:
        d = page_json(RAW[f]) or {}
        counts[name] = len(d.get("p", []))
        if name == "match":
            counts["places"] = len(d.get("juris", []))
hub = visible(RAW.get("compare/index.html", ""))
for name, label in (("ats", "ATS"), ("crm", "recruiting CRMs"), ("match", "tools that score or rank")):
    n = counts.get(name)
    if n is None:
        continue
    card = re.search(r'href="/compare/%s/">.*?</a>' % name, RAW.get("compare/index.html", ""), flags=re.S)
    if card:
        nums = [int(x) for x in re.findall(r"\b(\d{1,3}) (?:ATS|recruiting|tools|platforms)", strip(card.group(0)))]
        if nums and nums[0] != n:
            err("consistency", "compare/index.html", f"{name} card says {nums[0]} but the comparison has {n}")
if "places" in counts:
    for page in ("compare/index.html", "index.html", "coverage/index.html", "compare/match/index.html"):
        current = re.sub(r"<!-- changelog -->.*?<!-- /changelog -->", " ", RAW.get(page, ""), flags=re.S)
        for m in re.finditer(r"\b(\d{1,3}) (places|jurisdictions)\b", visible(current)):
            if int(m.group(1)) not in (counts["places"],) and not is_archive(page):
                err("consistency", page, f"says {m.group(0)} but the rules check has {counts['places']}")

# ---------------------------------------------------------------- watchlist
wl_path = os.path.join(HERE, "watchlist.json")
if os.path.exists(wl_path):
    for w in json.load(open(wl_path, encoding="utf-8")):
        due = dt.date.fromisoformat(w["recheck_by"])
        if w.get("status") == "closed":
            continue
        late = (TODAY - due).days
        if late > 14: err("watchlist", w["id"], f"recheck overdue by {late} days: {w['fact']} (on {', '.join(w['where'])})")
        elif late >= 0: warn("watchlist", w["id"], f"recheck due: {w['fact']} (on {', '.join(w['where'])})")
else:
    warn("watchlist", "_tools/verify/watchlist.json", "no watchlist found")

# ---------------------------------------------------------------- reputation
# private-terms.txt (one term per line) lists names that must never appear on the site, such as employers.
# It stays on Alex's computer: .gitignore keeps it out of the public repo.
PT = os.path.join(HERE, "private-terms.txt")
PRIVATE_TERMS = [t.strip() for t in open(PT, encoding="utf-8").read().splitlines() if t.strip() and not t.startswith("#")] if os.path.exists(PT) else []
if not PRIVATE_TERMS:
    warn("reputation", "_tools/verify/private-terms.txt", "no private terms configured on this computer")
for f, raw in RAW.items():
    text = visible(raw)
    for term in PRIVATE_TERMS:
        if re.search(r"\b%s\b" % re.escape(term), raw, flags=re.I):
            err("reputation", f, f"mentions a private term ({term[:2]}…): keep employers and internal matters off the site")
    for pat in (r"\bTODO\b", r"\bTBD\b", r"\blorem ipsum\b", r"\bXXX\b", r"\bFIXME\b", r"\binternal only\b", r"\bconfidential\b"):
        if re.search(pat, text, flags=re.I):
            err("reputation", f, f"placeholder or sensitive marker: {pat.strip(chr(92)+'b')}")
    for e in set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)):
        if e.lower() != "alex@thesignalhr.com":
            warn("reputation", f, f"email address on page: {e}")

# ---------------------------------------------------------------- search index freshness
idx = "assets/search-index.json"
if os.path.exists(idx):
    items = json.load(open(idx, encoding="utf-8")).get("items", [])
    in_index = sum(1 for e in items if e.get("k") == "Briefing signal")
    on_site = sum(len([b for b in re.findall(r'<article class="brief-item"[^>]*>(.*?)</article>', raw, flags=re.S) if 'class="so-what"' in b])
                  for f, raw in RAW.items() if f.startswith("briefing/"))
    if in_index != on_site:
        err("search", idx, f"index has {in_index} Briefing signals, the site has {on_site}: run python3 -B _tools/site/search_index.py")
else:
    warn("search", idx, "no search index: run python3 -B _tools/site/search_index.py")

# ---------------------------------------------------------------- report
errors = [x for x in findings if x[0] == "ERROR"]
warnings = [x for x in findings if x[0] == "WARNING"]
lines = [f"# Verification report: {TODAY.isoformat()}", "",
         f"**{'BLOCKED' if errors else 'PASS'}**: {len(errors)} errors, {len(warnings)} warnings across {len(PAGES)} pages.",
         "Errors must be fixed before publishing. Warnings need a human look.", ""]
for level in ("ERROR", "WARNING"):
    rows = [x for x in findings if x[0] == level]
    if not rows:
        continue
    lines += [f"## {level.title()}s ({len(rows)})", ""]
    for check in sorted({x[1] for x in rows}):
        lines.append(f"### {check}")
        lines += [f"- {w}: {m}" for _, c, w, m in rows if c == check]
        lines.append("")
report = "\n".join(lines)
open(os.path.join(HERE, "last-report.md"), "w", encoding="utf-8", newline="").write(report + "\n")
if not args.quiet:
    print(report)
sys.exit(1 if errors else 0)
