"""Newsletter signup without a Substack frame (November 2026). Run from the repo root:
    python3 -B _tools/site/signup.py
Idempotent. Replaces the embedded Substack frame on every page with an on-site form (signup_form.html) that sends
the address to Substack only when the reader submits, installs signup.css and signup.js as managed blocks, and
updates the privacy page to match. The form posts to the same Substack endpoint its embed uses.
"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
changed = []
def src(name): return open(os.path.join(HERE, name), encoding="utf-8").read().strip("\n")
def rw(path, fn):
    s = open(path, encoding="utf-8", newline="").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)
def managed(s, name, body):
    start, end = f"/* >>> {name} (managed by _tools/site/signup.py) */", f"/* <<< {name} */"
    block = f"{start}\n{body}\n{end}"
    m = re.search(re.escape(f"/* >>> {name} ") + r".*?" + re.escape(end), s, flags=re.S)
    return s[:m.start()] + block + s[m.end():] if m else s.rstrip("\n") + "\n\n" + block + "\n"

FORM = src("signup_form.html")
def form(fid, placement, indent=""):
    return "\n".join(indent + line for line in FORM.format(id=fid, placement=placement).split("\n")).lstrip()

FRAME = re.compile(r'([ \t]*)<iframe src="https://thesignalhr\.substack\.com/embed"[^>]*></iframe>')
def page(s):
    n = [0]
    def sub(m):
        n[0] += 1
        return m.group(1) + form("sub-band" if n[0] == 1 else f"sub-band-{n[0]}", "band", m.group(1))
    s = FRAME.sub(sub, s)
    # the micro line under the old frame repeats what the form now says
    s = re.sub(r'(</form>)\s*<p class="micro">No spam\. Unsubscribe anytime\.</p>', r"\1", s)
    return s

if __name__ == "__main__":
    for f in sorted(f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("_", "."))):
        rw(f, page)
    rw("assets/site.css", lambda s: managed(s, "signup", src("signup.css")))
    rw("assets/site.js", lambda s: managed(s, "signup", src("signup.js")))

    PRIV = [
        ("The signup form on our pages is Substack's own embedded form.",
         "The signup form on our pages sends your email address straight to Substack when you press Subscribe; we don't store it."),
        ("The newsletter signup form is Substack's own embedded form, covered by Substack's privacy policy.",
         "Nothing from Substack loads until you press Subscribe; then Substack's page opens and its privacy policy applies."),
    ]
    def priv(s):
        for old, new in PRIV:
            if old in s:
                s = s.replace(old, new)
            elif new not in s:
                sys.exit(f"privacy: can't find {old[:70]!r}")
        return s
    rw("privacy/index.html", priv)
    rw("_tools/site/fixes_2026_10_20.py", lambda s: s.replace(PRIV[0][0], PRIV[0][1]))
    rw("_tools/site/consent.py", lambda s: s.replace(PRIV[1][0], PRIV[1][1]))
    left = [f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("_", ".")) and "substack.com/embed" in open(f, encoding="utf-8").read()]
    if left:
        sys.exit("Substack frame still on: " + ", ".join(left))
    print(f"{len(changed)} files changed", *changed, sep="\n  ")
