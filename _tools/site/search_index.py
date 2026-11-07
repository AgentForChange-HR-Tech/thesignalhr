"""Site search for The Signal HR: builds assets/search-index.json from the published pages and keeps
the search box (search.css / search.js) installed in assets/site.css and assets/site.js.
Run from the repo root after any content change:
    python3 -B _tools/site/search_index.py
Idempotent. No server and no third party: the index is a static file and the search runs in the
reader's browser. Results are ordered only by how well they match the reader's words (see
_tools/GUARDRAILS.md, section 6).
What gets indexed: Briefing signals (current and archive, each linking to #signal-N), Insights,
Coverage, the comparison pages, every platform profile (linking to #p-<id>), every place in the
applicant match rules check, and the other pages.
"""
import glob, html, json, os, re
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "assets/search-index.json"
SKIP_PAGES = {"404.html"}
SKIP_TAGS = {"script", "style", "nav", "header", "footer", "noscript", "iframe", "svg", "button", "select", "form"}
SKIP_CLASSES = {"news-band", "region-bar", "crumbs", "kits-thanks", "ats-tray"}
INLINE = {"a", "em", "strong", "b", "i", "code", "mark", "small", "sup", "sub", "abbr"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

class Text(HTMLParser):
    """Visible text of a fragment, skipping navigation, scripts and the newsletter band."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.stack = [], []
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        cls = set((dict(attrs).get("class") or "").split())
        skip = tag in SKIP_TAGS or bool(cls & SKIP_CLASSES) or (self.stack and self.stack[-1])
        self.stack.append(bool(skip))
        if tag not in INLINE:
            self.parts.append(" ")
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack:
            self.stack.pop()
        if tag not in INLINE:
            self.parts.append(" ")
    def handle_data(self, d):
        if not (self.stack and self.stack[-1]):
            self.parts.append(d)
    def text(self):
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()

def text_of(fragment):
    p = Text(); p.feed(fragment); p.close()
    return p.text()

def first(pattern, s, default=""):
    m = re.search(pattern, s, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else default

def url_of(path):
    u = "/" + path.replace(os.sep, "/")
    return u[: -len("index.html")] if u.endswith("index.html") else u

def clip(s, n):
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"

changed = []
# ---------------------------------------------------------------- privacy page: say what search records
PRIV = "privacy/index.html"
LINE = ("      <li><strong>Site search.</strong> Search runs in your browser. The words you search for may be counted in analytics, "
        "without identifying you, so we can see what people look for and what's missing. Please don't type personal information into it.</li>\n")
if os.path.exists(PRIV):
    ps = open(PRIV, encoding="utf-8", newline="").read()
    if "<strong>Site search.</strong>" not in ps:
        m = re.search(r"(\n[ \t]*<li><strong>Tools on comparison pages\.</strong>.*?</li>\n)", ps, flags=re.S)
        assert m, "privacy page: tools bullet not found"
        ps = ps[:m.end()] + LINE + ps[m.end():]
        open(PRIV, "w", encoding="utf-8", newline="").write(ps)
        changed.append(PRIV)

entries = []
def add(kind, title, url, summary, text, date=""):
    entries.append({"k": kind, "t": title, "u": url, "s": clip(summary, 220), "x": clip(text, 4000), "d": date})

PROFILE_KIND = {"ats": "ATS profile", "crm": "CRM profile", "match": "Match score profile"}

for path in sorted(glob.glob("**/index.html", recursive=True)):
    if path.startswith(("_", ".")) or path in SKIP_PAGES or not os.path.exists(path):
        continue
    raw = open(path, encoding="utf-8").read()
    url = url_of(path)
    mm = re.search(r'<main id="main">(.*?)</main>', raw, flags=re.S)
    if not mm:
        continue
    main = mm.group(1)
    h1 = first(r"<h1[^>]*>(.*?)</h1>", main)
    tab = re.sub(r"\s+—\s+The Signal HR$", "", first(r"<title>(.*?)</title>", raw))
    title = h1 if url.startswith("/insights/") and url != "/insights/" else (tab or h1)
    desc = html.unescape(first(r'<meta name="description" content="([^"]*)"', raw))
    kicker = first(r'<span class="kicker">(.*?)</span>', main)

    # Briefing editions: index each signal, not the page
    if url.startswith("/briefing/") and "brief-item" in main:
        edition = kicker.replace("· Archived", "").strip(" ·")
        for i, block in enumerate(re.findall(r'<article class="brief-item"[^>]*>(.*?)</article>', main, flags=re.S), start=1):
            head = first(r"<h3[^>]*>(.*?)</h3>", block)
            so = first(r'<div class="so-what">(.*?)</div>', block).replace("So what ·", "").strip()
            add("Briefing signal", head, f"{url}#signal-{i}", so, text_of(block), edition)
        continue

    # Comparison pages: one entry for the page, one per platform profile
    m = re.match(r"/compare/(ats|crm|match)/$", url)
    if m:
        kind = PROFILE_KIND[m.group(1)]
        for pid, block in re.findall(r'<details class="profile" id="p-([a-z0-9-]+)">(.*?)</details>', main, flags=re.S):
            name = first(r'<span class="pname">(.*?)</span>', block)
            cat = first(r'<span class="tag[^"]*">(.*?)</span>', block)
            best = first(r'<p class="pbest">(.*?)</p>', block)
            add(kind, name, f"{url}#p-{pid}", f"{cat}. {best}" if cat else best, text_of(block), first(r"Verified ([A-Z][a-z]+ \d{4})", block))
        page_text = text_of(re.sub(r'<details class="profile".*?</details>', " ", main, flags=re.S))
        add("Comparison", title, url, desc, page_text)
        if m.group(1) == "match":
            data = re.search(r'<script type="application/json" id="ats-data">(.*?)</script>', raw, flags=re.S)
            if data:
                d = json.loads(data.group(1).replace("<\\/", "</"))
                names = {j["id"]: j["name"] for j in d.get("juris", [])}
                for j in d.get("juris", []):
                    where = j["name"] if not j.get("parent") else f'{j["name"]}, {names.get(j["parent"], "")}'
                    must = " ".join(t for _, t in j.get("must", []))
                    add("Hiring-AI rules", f"{where}: {j['law']}", "/compare/match/#rules",
                        f"{j['status']}. {j['when']}", f"{where} {j['law']} {j['status']} {j['when']} {must} {j.get('watch', '')}")
        continue

    kind = ("Insight" if url.startswith("/insights/") and url != "/insights/" else
            "Coverage" if url.startswith("/coverage/") else
            "Comparison" if url.startswith("/compare/") else "Page")
    date = first(r'<div class="article-meta">.*?<span>([A-Z][a-z]+ \d{1,2}, \d{4})</span>', main)
    add(kind, title, url, desc, text_of(main), date)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
payload = json.dumps({"v": 1, "items": entries}, ensure_ascii=False, separators=(",", ":"))
old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
if old != payload:
    open(OUT, "w", encoding="utf-8", newline="").write(payload)
    changed.append(OUT)

# ---------------------------------------------------------------- install the search box (managed blocks)
START, END = "/* >>> site-search (managed by _tools/site/search_index.py) */", "/* <<< site-search */"
def put(path, src):
    s = open(path, encoding="utf-8", newline="").read()
    block = START + "\n" + open(os.path.join(HERE, src), encoding="utf-8").read().strip("\n") + "\n" + END
    t = (re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, s, count=1, flags=re.S)
         if START in s else s.rstrip("\n") + "\n\n" + block + "\n")
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)
put("assets/site.css", "search.css")
put("assets/site.js", "search.js")

kinds = {}
for e in entries:
    kinds[e["k"]] = kinds.get(e["k"], 0) + 1
print(f"{len(entries)} entries ({', '.join(f'{v} {k}' for k, v in sorted(kinds.items()))}); "
      f"{len(payload) // 1024} KB; {len(changed)} files changed", *changed)
