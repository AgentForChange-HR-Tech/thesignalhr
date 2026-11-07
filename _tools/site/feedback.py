"""Reader feedback on every page (November 2026). Run from the repo root:
    python3 -B _tools/site/feedback.py
Idempotent. Installs feedback.js and feedback.css as managed blocks in assets/site.js and assets/site.css: a
"Was this page useful? Yes / No" count (analytics only, when the cookie choice allows it; no text, nothing that
identifies the reader) and a "Suggest a fix or add context" email link with the page filled in. Updates the privacy
page (and the October script that first built it) to say so. Emails are triaged by the weekly feedback task into
editorial/feedback/ (see _tools/PUBLISHING.md).
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
changed = []
def src(n): return open(os.path.join(HERE, n), encoding="utf-8").read().strip("\n")
def rw(path, fn):
    s = open(path, encoding="utf-8", newline="").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)
def managed(s, name, body):
    start, end = f"/* >>> {name} (managed by _tools/site/feedback.py) */", f"/* <<< {name} */"
    block = f"{start}\n{body}\n{end}"
    m = re.search(re.escape(f"/* >>> {name} ") + r".*?" + re.escape(end), s, flags=re.S)
    return s[:m.start()] + block + s[m.end():] if m else s.rstrip("\n") + "\n\n" + block + "\n"
rw("assets/site.js", lambda s: managed(s, "feedback", src("feedback.js")))
rw("assets/site.css", lambda s: managed(s, "feedback", src("feedback.css")))
LINE = ("      <li><strong>Page feedback.</strong> The \"Was this page useful?\" buttons are counted in analytics, only if your cookie "
        "choice allows it, without any text or anything that identifies you. Suggestions you send by email are read by Alex and sorted "
        "with AI help into corrections, ideas and questions; we don't publish what you write without your permission.</li>\n")
def priv(s):
    if "<strong>Page feedback.</strong>" in s:
        return s
    m = re.search(r"(\n[ \t]*<li><strong>Email\.</strong>.*?</li>\n)", s, flags=re.S)
    if not m: sys.exit("privacy: Email bullet not found")
    return s[:m.end()] + LINE + s[m.end():]
rw("privacy/index.html", priv)
rw("_tools/site/fixes_2026_10_20.py", priv)
print(f"{len(changed)} files changed", *changed)
