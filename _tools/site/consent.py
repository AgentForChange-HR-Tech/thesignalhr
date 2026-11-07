"""Cookie consent by location, self-hosted fonts, and the privacy page that describes them (November 2026).
Run from the repo root, and again after adding pages or changing a page template:
    python3 -B _tools/site/consent.py
Idempotent. Sources: consent_head.js (inlined in every page's <head>), consent.js and consent.css (managed
blocks in assets/site.js and assets/site.css), and the font files in assets/fonts/.

How it works (orientation, not legal advice; /privacy/#cookies describes it for readers):
- Opt-in places: Google Analytics doesn't load at all until the visitor chooses "Allow analytics". The browser's
  time-zone setting decides, on the device; nothing is sent. Opt-in time zones: Europe (EU/EEA, UK, Switzerland
  and the rest of Europe), EU outermost regions, Cyprus, Brazil, and Canada's Eastern zone (Quebec shares it
  with Ontario). An unknown or UTC time zone counts as opt-in.
- Everywhere else: analytics loads, and a one-time notice offers "OK" or "Turn off analytics".
- Belt and braces: Google consent mode keeps analytics cookies off by default wherever Google places the
  visitor's IP address in the EEA, UK, Switzerland, Brazil or Quebec, even if the time zone says otherwise.
- Global Privacy Control or Do Not Track keeps analytics off, with no banner. Advertising storage is always
  denied, Google signals and ad personalization are off, and analytics cookies expire after 13 months.
- The choice is kept in local storage (signal-consent): 12 months for "allow", 6 months for "no".
  "Cookie settings" in every footer reopens it.
- Fonts are served from /assets/fonts/ instead of Google Fonts, so pages make no font requests to Google.
"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
changed = []

def src(name):
    return open(os.path.join(HERE, name), encoding="utf-8").read().strip("\n")

def rw(path, fn):
    s = open(path, encoding="utf-8", newline="").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)

def managed(s, name, body):
    """Replace or append a block between >>> name / <<< name markers (CSS-style comments work in both files)."""
    start = f"/* >>> {name} (managed by _tools/site/consent.py) */"
    end = f"/* <<< {name} */"
    block = f"{start}\n{body}\n{end}"
    m = re.search(re.escape(f"/* >>> {name} ") + r".*?" + re.escape(end), s, flags=re.S)
    if m:
        return s[:m.start()] + block + s[m.end():]
    return s.rstrip("\n") + "\n\n" + block + "\n"

# ---------------------------------------------------------------- 1. the consent loader in every page head
HEAD_START = "<!-- >>> consent (managed by _tools/site/consent.py) -->"
HEAD_END = "<!-- <<< consent -->"
HEAD = f"{HEAD_START}\n<script>\n{src('consent_head.js')}\n</script>\n{HEAD_END}\n"
RAW_GA = re.compile(r'(?:<!-- Google tag \(gtag\.js\) -->\s*)?<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-[A-Z0-9]+"></script>\s*'
                    r"<script>\s*window\.dataLayer = window\.dataLayer \|\| \[\];.*?</script>\n?", re.S)
BLOCK = re.compile(re.escape(HEAD_START) + r".*?" + re.escape(HEAD_END) + r"\n?", re.S)
GFONTS = re.compile(r'[ \t]*<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>\n?')
FOOT_OLD = '<a href="/terms/">Terms</a></span>'
FOOT_NEW = '<a href="/terms/">Terms</a> · <button type="button" class="cookie-link" data-consent-open>Cookie settings</button></span>'
no_ga = []

def page(s):
    if BLOCK.search(s):
        s = BLOCK.sub(lambda m: HEAD, s, count=1)
    elif RAW_GA.search(s):
        s = RAW_GA.sub(lambda m: HEAD, s, count=1)
    elif "<head>" in s:
        no_ga.append(1)      # page without analytics: leave it without
    s = GFONTS.sub("", s)
    if "data-consent-open" not in s.split("<footer", 1)[-1] and FOOT_OLD in s:
        s = s.replace(FOOT_OLD, FOOT_NEW, 1)
    return s

PAGES = sorted(f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("_", ".")))
for f in PAGES:
    before = len(no_ga)
    rw(f, page)
    if len(no_ga) > before:
        print("note: no analytics tag on", f)

# ---------------------------------------------------------------- 2. banner script, styles and self-hosted fonts
FONT_FILES = ["dm-sans-latin-ext-%s-normal.woff2", "dm-sans-latin-%s-normal.woff2"]
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,"
         "U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
LATIN_EXT = ("U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,"
             "U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF")
faces = ["/* DM Sans and DM Serif Display, SIL Open Font License 1.1 (assets/fonts/OFL.txt), via Fontsource 5.3.0 */"]
need = []
for family, slug, styles in (("DM Sans", "dm-sans", [("normal", w) for w in (300, 400, 500, 700)]),
                             ("DM Serif Display", "dm-serif-display", [("normal", 400), ("italic", 400)])):
    for style, weight in styles:
        for sub, rng in (("latin-ext", LATIN_EXT), ("latin", LATIN)):
            fn = f"{slug}-{sub}-{weight}-{style}.woff2"
            need.append(fn)
            faces.append(f"@font-face {{ font-family: '{family}'; font-style: {style}; font-weight: {weight}; font-display: swap; "
                         f"src: url(/assets/fonts/{fn}) format('woff2'); unicode-range: {rng}; }}")
missing = [n for n in need + ["OFL.txt"] if not os.path.exists(os.path.join("assets", "fonts", n))]
if missing:
    sys.exit("missing font files in assets/fonts/: " + ", ".join(missing))

rw("assets/site.js", lambda s: managed(s, "consent-ui", src("consent.js")))
rw("assets/site.css", lambda s: managed(managed(s, "fonts", "\n".join(faces)), "consent-ui", src("consent.css")))

# ---------------------------------------------------------------- 3. privacy page (and the October script that first built it)
COOKIES = (
    '    <h2 id="cookies">Cookies and your choice</h2>\n'
    "    <p>The only cookies this site sets are Google Analytics cookies. Which default you get depends on where you are:</p>\n"
    "    <ul>\n"
    "      <li><strong>Europe (including the EU, the UK and Switzerland), Brazil, and Canada's Eastern time zone, which includes Quebec:</strong> "
    "analytics stays off unless you choose \"Allow analytics\".</li>\n"
    "      <li><strong>Everywhere else:</strong> analytics is on, and a notice on your first visit lets you turn it off.</li>\n"
    "      <li><strong>Privacy signals:</strong> if your browser sends Global Privacy Control or Do Not Track, analytics stays off unless you turn it on.</li>\n"
    "    </ul>\n"
    "    <p>To pick the default, the site reads your device's time-zone setting in your browser; it isn't sent to us or anyone else. "
    "If the time zone can't be read, analytics stays off until you choose. Google may also use the region of your IP address to keep "
    "analytics cookies off by default in the EU, the UK, Switzerland, Brazil and Quebec. Your choice is kept in your browser for up to "
    "12 months (6 months if you say no). You can change it any time with <strong>Cookie settings</strong> at the bottom of every page, "
    'or here: <button type="button" class="cookie-link" data-consent-open>Cookie settings</button>.</p>\n'
    "    <p>Nothing from Substack loads until you press Subscribe; then Substack's page opens and its privacy policy applies. "
    "The site's fonts are served from this site, not from Google.</p>\n")
PRIV_PAIRS = [
    ("we count visits so we know what's useful. We don't run ads,",
     "we count visits so we know what's useful, and where the law asks for consent first, only if you allow it. We don't run ads,"),
    ("It sets cookies (named <code>_ga</code>) to tell visits apart. We use it only to improve the site.</li>",
     "It sets cookies (named <code>_ga</code>, kept for up to 13 months) to tell visits apart, only when your cookie choice allows it "
     '(see <a href="#cookies">Cookies and your choice</a>). Google signals and advertising features are off. We use it only to improve the site.</li>'),
    ("The site remembers your light or dark theme and your region filter in your browser's local storage (<code>signal-theme</code>, <code>signal-region</code>).",
     "The site remembers your light or dark theme, your region filter and your cookie choice in your browser's local storage "
     "(<code>signal-theme</code>, <code>signal-region</code>, <code>signal-consent</code>)."),
    ("      <li><strong>Google Fonts</strong> (Google): the site's fonts load from Google's servers, which receive your IP address.</li>\n", ""),
]
CHOICE = "      <li>Change your analytics choice any time with <strong>Cookie settings</strong> at the bottom of every page.</li>\n"

def privacy(s, page=True):
    for old, new in PRIV_PAIRS:
        if old in s:
            s = s.replace(old, new)
        elif new and new not in s:
            sys.exit(f"privacy: can't find {old[:80]!r}")
    if 'id="cookies"' not in s:
        anchor = "    <h2>What we don't do</h2>"
        if anchor not in s: sys.exit("privacy: section anchor not found")
        s = s.replace(anchor, COOKIES + anchor, 1)
    if "Change your analytics choice" not in s:
        anchor = "      <li>Block or delete cookies in your browser,"
        if anchor not in s: sys.exit("privacy: choices list not found")
        s = s.replace(anchor, CHOICE + anchor, 1)
    if page:
        s = s.replace('<div class="article-meta"><span>Effective October 20, 2026</span></div>',
                      '<div class="article-meta"><span>Effective October 20, 2026</span><span>Updated November 6, 2026</span></div>')
    return s
rw("privacy/index.html", privacy)
rw("_tools/site/fixes_2026_10_20.py", lambda s: privacy(s, page=False))

print(f"{len(changed)} files changed")
for c in changed:
    print(" ", c)
