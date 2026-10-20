"""Site fixes from the October 2026 independent review. Run from the repo root:
    python3 -B _tools/site/fixes_2026_10_20.py
Idempotent: running it twice changes nothing the second time.

1. EU AI Act insight: time-relative headline replaced with absolute dates, with a visible note.
2. Comparison Hub: review date per comparison and a dated change log; comparison pages link to it.
3. Privacy and terms pages; contact email; footer links on every page.
4. Subscribe: the nav button scrolls to the page's embedded signup instead of leaving the site; both paths are measured.
"""
import glob, html, json, os, re

E = lambda s: html.escape(str(s), quote=True)
EMAIL = "alex@thesignalhr.com"
TODAY = "2026-10-20"
changed = []

def rw(path, fn):
    s = open(path, encoding="utf-8", newline="").read()
    t = fn(s)
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)

def once(s, old, new, path=""):
    """Replace old with new exactly once; skip if new is already there."""
    if new in s:
        return s
    assert s.count(old) == 1, f"{path}: expected one match for {old[:70]!r}, found {s.count(old)}"
    return s.replace(old, new)

# ---------------------------------------------------------------- 1. EU AI Act headline
OLD_H = "The EU AI Act's HR deadline is days away — and Brussels just blinked"
NEW_H = "The EU AI Act's HR deadline moved to December 2, 2027. The work didn't."
OLD_T = "EU AI Act: The August 2 HR Deadline, Explained for CHROs — The Signal HR"
NEW_T = "EU AI Act for HR: High-Risk Hiring Rules Apply From December 2, 2027 — The Signal HR"

def eu_article(s):
    p = "insights/eu-ai-act-hr-deadline/index.html"
    s = s.replace(OLD_T, NEW_T)
    s = s.replace(OLD_H.replace("—", "\\u2014"), NEW_H)          # JSON-LD
    s = s.replace('"dateModified":"2026-10-16"', '"dateModified":"%s"' % TODAY)
    s = once(s, "<span>›</span>The EU AI Act's HR deadline is days away</nav>",
             "<span>›</span>The EU AI Act's HR deadline moved to December 2, 2027</nav>", p)
    s = once(s, "<h1>The EU AI Act's HR deadline is days away — and Brussels just <em>blinked</em></h1>",
             "<h1>The EU AI Act's HR deadline moved to December 2, 2027. <em>The work didn't.</em></h1>", p)
    s = once(s, '<div class="article-meta"><span>By Alex Rivera</span><span>July 23, 2026</span><span>6 min read</span></div>',
             '<div class="article-meta"><span>By Alex Rivera</span><span>July 23, 2026</span><span>Updated October 20, 2026</span><span>6 min read</span></div>', p)
    s = once(s, "See <a href=\"https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng\" target=\"_blank\" rel=\"noopener\">the official text</a> and <a href=\"/briefing/\">this week's briefing</a>.</div>",
             "See <a href=\"https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng\" target=\"_blank\" rel=\"noopener\">the official text</a>."
             "<br><br><strong>Headline updated · October 20, 2026 — </strong>It originally read “The EU AI Act’s HR deadline is days away — and Brussels just blinked.” "
             "The analysis below is as written on July 23; the dates above supersede it.</div>", p)
    return s

rw("insights/eu-ai-act-hr-deadline/index.html", eu_article)
rw("insights/index.html", lambda s: s.replace("<h3>%s</h3>" % OLD_H, "<h3>%s</h3>" % NEW_H))

# ---------------------------------------------------------------- 2. Hub review dates + change log
REVIEWED = {"/compare/ats/": "Reviewed October 2026", "/compare/crm/": "Reviewed October 2026", "/compare/match/": "Reviewed October 2026"}
CHANGELOG = [  # newest first: (date, comparison, what changed)
    ("October 19, 2026", "Applicant match", "Rules check goes two-tier: 38 places in 21 countries and the EU, down to US states, Canadian provinces and EU member states."),
    ("October 16, 2026", "Applicant match", "Launched: 16 platforms rated on governance, a rules check for 17 places, shortlist finder and RFP bank."),
    ("October 16, 2026", "Recruiting CRMs", "Launched: 17 platforms, a “do you need a separate CRM?” check, shortlist finder and RFP bank."),
    ("October 16, 2026", "ATS platforms", "Timeline ranges replaced with a go-live drivers check. AI certification ratings corrected for iCIMS, SmartRecruiters, Oracle, Gem, Ashby and SAP."),
    ("October 16, 2026", "ATS platforms", "Rebuilt: 17 platforms (up from 11), shortlist finder, side-by-side compare and a 13-question RFP bank."),
    ("July 24, 2026", "ATS platforms", "First edition: 11 applicant tracking systems."),
]

def changelog_html():
    rows = "".join(f"<tr><td class=\"when\">{E(d)}</td><td>{E(c)}</td><td>{E(w)}</td></tr>" for d, c, w in CHANGELOG)
    return ('\n  <section class="section" id="changelog" style="padding-top:0;scroll-margin-top:80px;">\n    <div class="wrap">\n'
            '      <div class="section-head"><div><span class="kicker">Freshness</span><h2>Change <em>log</em></h2></div></div>\n'
            '      <p style="color:var(--ink-mid);max-width:46em;margin-bottom:1rem;">Every material change to a comparison, newest first. '
            'Platform profiles also carry their own verification date. Spot something out of date? '
            f'<a href="mailto:{EMAIL}">Tell us</a> and we’ll fix it with a note here.</p>\n'
            '      <div class="cal-wrap"><table class="cal"><thead><tr><th scope="col">Date</th><th scope="col">Comparison</th><th scope="col">What changed</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>\n    </div>\n  </section>\n')

def hub(s):
    p = "compare/index.html"
    s = s.replace("<span>Reviewed June 2026</span>", "<span>Updated October 20, 2026 · <a href=\"#changelog\">Change log</a></span>")
    for href, label in REVIEWED.items():
        card = re.search(r'(<a class="card" href="%s">.*?)(<span class="arrow">)' % re.escape(href), s, flags=re.S)
        assert card, f"{p}: no card for {href}"
        if 'class="card-meta"' not in card.group(1):
            s = s[:card.start(2)] + f'<span class="card-meta">{label}</span>\n          ' + s[card.start(2):]
    block = changelog_html()
    if "<!-- changelog -->" in s:
        s = re.sub(r"<!-- changelog -->.*?<!-- /changelog -->", lambda m: "<!-- changelog -->" + block + "<!-- /changelog -->", s, flags=re.S)
    else:
        # place it after the cards/method section, before the newsletter band
        anchor = '  <section class="section" style="padding-top:0;">\n    <div class="wrap">\n      <div class="news-band">'
        assert s.count(anchor) == 1, f"{p}: newsletter band anchor not found"
        s = s.replace(anchor, "<!-- changelog -->" + block + "<!-- /changelog -->\n" + anchor)
    return s

rw("compare/index.html", hub)

FRESH_OLD = 'Spot something out of date? <a href="/about/">Tell us</a> and we\'ll fix it with a note.</li>'
FRESH_NEW = (f'Spot something out of date? <a href="mailto:{EMAIL}">Tell us</a> and we\'ll fix it with a note. '
             'Every material change is in the <a href="/compare/#changelog">change log</a>.</li>')
for f in ["compare/ats/index.html", "compare/crm/index.html", "compare/match/index.html",
          "_tools/ats/build_ats.py", "_tools/crm/build_crm.py", "_tools/match/build_match.py"]:
    if os.path.exists(f):
        rw(f, lambda s, f=f: once(s, FRESH_OLD, FRESH_NEW, f))

# ---------------------------------------------------------------- 3. Contact + footer links on every page
def footer(s):
    i = s.find("<footer")
    if i < 0:
        return s
    head, foot = s[:i], s[i:]
    if f'href="mailto:{EMAIL}">Contact</a>' not in foot:
        foot = re.sub(r'(\n([ \t]*)<li><a href="/about/">About</a></li>)',
                      lambda m: m.group(1) + "\n" + m.group(2) + f'<li><a href="mailto:{EMAIL}">Contact</a></li>', foot, count=1)
    foot = foot.replace("<span>© 2026 The Signal HR · Curated by Alex Rivera</span>",
                        '<span>© 2026 The Signal HR · Curated by Alex Rivera · <a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a></span>')
    return head + foot

PAGES = sorted(f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("_", ".")))
for f in PAGES:
    rw(f, footer)
rw("about/index.html", lambda s: once(s,
    'Spot an error? <a href="https://www.linkedin.com/in/alexrivera1/" target="_blank" rel="noopener">Tell us.</a></p>',
    f'Spot an error? Email <a href="mailto:{EMAIL}">{EMAIL}</a> or <a href="https://www.linkedin.com/in/alexrivera1/" target="_blank" rel="noopener">message on LinkedIn</a>.</p>', "about"))

# ---------------------------------------------------------------- 3b. Privacy and terms pages (built from the About page)
PRIVACY = f"""
    <p><strong>The short version:</strong> we count visits so we know what's useful. We don't run ads, we don't sell your information, and we never share it with HR-tech vendors. The newsletter signup is handled by Substack.</p>
    <h2>Who we are</h2>
    <p>The Signal HR (thesignalhr.com) is an independent publication run by Alex Rivera. Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    <h2>What we collect, and why</h2>
    <ul>
      <li><strong>Analytics.</strong> Google Analytics 4 tells us which pages and tools get used: pages viewed, approximate location (country or city), device and browser, how you arrived, and interactions such as filter choices on comparison pages. It sets cookies (named <code>_ga</code>) to tell visits apart. We use it only to improve the site.</li>
      <li><strong>Newsletter.</strong> If you subscribe, Substack collects your email address and sends the newsletter, under <a href="https://substack.com/privacy" target="_blank" rel="noopener">Substack's privacy policy</a>. The signup form on our pages is Substack's own embedded form.</li>
      <li><strong>Email.</strong> If you write to us, we keep your message and address so we can reply.</li>
      <li><strong>Settings in your browser.</strong> The site remembers your light or dark theme and your region filter in your browser's local storage (<code>signal-theme</code>, <code>signal-region</code>). They stay on your device, and clearing your browser data removes them.</li>
      <li><strong>Tools on comparison pages.</strong> Answers you give in the checks and finders run in your browser. We don't store them. Which options people pick may be counted in analytics, without identifying you.</li>
    </ul>
    <h2>Services that handle data for us</h2>
    <ul>
      <li><strong>Google Analytics</strong> (Google): visit statistics.</li>
      <li><strong>Google Fonts</strong> (Google): the site's fonts load from Google's servers, which receive your IP address.</li>
      <li><strong>Substack</strong>: newsletter signup and delivery.</li>
      <li><strong>GitHub Pages</strong> (GitHub): hosting, which keeps standard server logs.</li>
      <li><strong>Cloudflare</strong>: domain name services.</li>
      <li><strong>Google Workspace</strong> (Google): email.</li>
    </ul>
    <p>These providers may process data in the United States and other countries.</p>
    <h2>What we don't do</h2>
    <ul>
      <li>No advertising, and no selling of personal information.</li>
      <li>No sharing with HR-tech vendors, and no paid placements of any kind.</li>
      <li>No tracking you across other websites for advertising.</li>
    </ul>
    <h2>How long we keep it</h2>
    <p>Analytics data is kept for the retention period set in Google Analytics, no longer than 14 months. Emails are kept as long as needed to handle the conversation. Substack keeps your subscription until you unsubscribe.</p>
    <h2>Your choices and rights</h2>
    <ul>
      <li>Block or delete cookies in your browser, or use <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Google's opt-out add-on</a> for Google Analytics.</li>
      <li>Unsubscribe from the newsletter with the link in any issue.</li>
      <li>Ask us what personal information we hold about you, or ask us to correct or delete it, by emailing <a href="mailto:{EMAIL}">{EMAIL}</a>.</li>
    </ul>
    <p>Depending on where you live, for example in the EU, the UK or California, you may have further rights, including the right to complain to your data protection authority.</p>
    <h2>Children</h2>
    <p>The site is written for working professionals. It isn't directed to children under 16, and we don't knowingly collect their information.</p>
    <h2>Changes</h2>
    <p>If this policy changes, we'll update this page and its effective date.</p>
"""
TERMS = f"""
    <p><strong>The short version:</strong> read and use the site freely. It's information, not legal or procurement advice. Check what matters with your own counsel and with vendors before you decide.</p>
    <h2>Information, not advice</h2>
    <p>Everything here is general information for HR and technology professionals. It isn't legal, financial or procurement advice, and it doesn't create an advisory relationship. The “rules where you hire” check on the applicant match comparison is orientation only: confirm what applies with counsel in each place you hire.</p>
    <h2>Accuracy and dates</h2>
    <p>We work to keep content accurate, dated and sourced, and we correct errors with a note. Products, pricing and laws change, so we can't promise that everything is complete or current. Platform ratings reflect public documentation at the review date shown, not testing of the product. Every material change to a comparison is listed in the <a href="/compare/#changelog">change log</a>.</p>
    <h2>Independence</h2>
    <p>No vendor pays to appear, to rank higher or to be described favorably. There are no sponsorships or affiliate links. Product names and trademarks belong to their owners and are used only to identify products; their use doesn't imply endorsement.</p>
    <h2>Using our material</h2>
    <ul>
      <li>You may use the RFP questions, checklists and copied question lists inside your organization, including in vendor evaluations.</li>
      <li>Short quotes with a link back are welcome.</li>
      <li>Please don't republish articles, comparisons or ratings in bulk, or present them as your own.</li>
    </ul>
    <h2>Other websites</h2>
    <p>We link to sources and vendor sites so you can check our work. We don't control those sites and aren't responsible for their content or practices.</p>
    <h2>No warranty</h2>
    <p>The site is provided as is. As far as the law allows, The Signal HR and Alex Rivera aren't liable for losses that come from relying on it.</p>
    <h2>Changes and contact</h2>
    <p>We may update these terms; the effective date above shows the latest version. Questions: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
"""
NEWPAGES = [
    ("privacy", "Privacy policy", "Privacy Policy — The Signal HR",
     "How The Signal HR handles your information: what analytics we use, how the Substack newsletter signup works, and what we never do with your data.",
     "Privacy", "Privacy, in <em style=\"color:var(--signal);\">plain words</em>.", PRIVACY),
    ("terms", "Terms of use", "Terms of Use — The Signal HR",
     "The terms for using The Signal HR: information, not advice; how ratings are dated and sourced; and how you may reuse our checklists and RFP questions.",
     "Terms", "Terms of <em style=\"color:var(--signal);\">use</em>.", TERMS),
]

def build_page(slug, name, title, desc, kicker, h1, body):
    tpl = open("about/index.html", encoding="utf-8").read()
    url = f"https://thesignalhr.com/{slug}/"
    head = tpl[:tpl.index('<main id="main">')]
    foot = tpl[tpl.index("</main>"):]
    head = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", head, flags=re.S)
    for attr in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
        head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(desc) + m.group(2), head)
    for attr in ['property="og:title"', 'name="twitter:title"']:
        head = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(title) + m.group(2), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), head)
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": name, "url": url, "dateModified": TODAY,
          "publisher": {"@type": "Organization", "name": "The Signal HR", "url": "https://thesignalhr.com/"}}
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", head, flags=re.S)
    head = head.replace('aria-current="page"', "")
    main = (f'<main id="main">\n<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">The Signal</a><span>›</span>{E(kicker)}</nav></div>\n\n'
            f'  <section class="article-header">\n    <div class="prose-wrap">\n      <span class="kicker">{E(kicker)}</span>\n      <h1>{h1}</h1>\n'
            f'      <div class="article-meta"><span>Effective October 20, 2026</span></div>\n    </div>\n  </section>\n'
            f'  <div class="prose-wrap prose">{body}  </div>\n')
    assert f'<link rel="canonical" href="{url}">' in head, "canonical not set"
    return head + main + foot

for args in NEWPAGES:
    path = f"{args[0]}/index.html"
    page = build_page(*args)
    os.makedirs(args[0], exist_ok=True)
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != page:
        open(path, "w", encoding="utf-8", newline="").write(page)
        changed.append(path)

# ---------------------------------------------------------------- 4. Subscribe: stay on the page, measure both paths
SUBJS = r"""
/* Subscribe: the nav button scrolls to this page's embedded signup instead of leaving the site.
   Measured in GA4: subscribe_cta (nav button scrolled to the form), subscribe_embed_focus (clicked into the
   embedded form), and the existing substack_cta_click (left for Substack). Completed signups: Substack > Subscribers > source. */
(function () {
  var frame = document.querySelector('iframe[src*="substack.com/embed"]');
  var send = function (name, params) { if (typeof gtag === "function") gtag("event", name, params); };
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href*="substack.com"]');
    if (!a) return;
    var where = a.classList.contains("nav-cta") ? "nav" : "other";
    if (frame && where === "nav") {
      e.preventDefault();
      var box = frame.closest(".sub-card, .news-band") || frame;
      box.scrollIntoView({ behavior: "smooth", block: "center" });
      box.classList.add("sub-flash");
      setTimeout(function () { box.classList.remove("sub-flash"); }, 1800);
      send("subscribe_cta", { placement: where, page_path: location.pathname });
    }
  });
  // The form is in a cross-origin frame, so count the moment focus moves into it.
  if (frame) window.addEventListener("blur", function () {
    setTimeout(function () {
      var el = document.activeElement;
      if (el && el.tagName === "IFRAME" && /substack\.com\/embed/.test(el.src) && !el.getAttribute("data-counted")) {
        el.setAttribute("data-counted", "1");
        send("subscribe_embed_focus", { page_path: location.pathname });
      }
    }, 0);
  });
})();
"""
SUBCSS = "\n/* subscribe: brief highlight when the nav button scrolls to the embedded form */\n.sub-flash { box-shadow: 0 0 0 3px var(--signal); transition: box-shadow .3s ease; }\n.footer-bottom a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }\n.footer-bottom a:hover { color: var(--signal); }\n"
EXIST_OLD = ('      a.addEventListener("click", function () {\n'
             '        if (typeof gtag === "function") {\n'
             '          gtag("event", "substack_cta_click"')
EXIST_NEW = ('      a.addEventListener("click", function () {\n'
             "        // the nav button scrolls to an on-page form when there is one (see Subscribe below), so it isn't an off-site click\n"
             '        if (a.classList.contains("nav-cta") && document.querySelector(\'iframe[src*="substack.com/embed"]\')) return;\n'
             '        if (typeof gtag === "function") {\n'
             '          gtag("event", "substack_cta_click"')
def sitejs(s):
    s = once(s, EXIST_OLD, EXIST_NEW, "assets/site.js")
    return s if "subscribe_embed_focus" in s else s.rstrip("\n") + "\n" + SUBJS
rw("assets/site.js", sitejs)
rw("assets/site.css", lambda s: s if ".sub-flash" in s else s.rstrip("\n") + "\n" + SUBCSS)

# ---------------------------------------------------------------- sitemap
def sitemap(s):
    for path in ["privacy/", "terms/"]:
        loc = f"https://thesignalhr.com/{path}"
        if loc not in s:
            s = s.replace("</urlset>", f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>")
    for path in ["compare/", "insights/", "insights/eu-ai-act-hr-deadline/", "about/"]:
        s = re.sub(r"(<loc>https://thesignalhr\.com/%s</loc><lastmod>)[^<]*(</lastmod>)" % re.escape(path), lambda m: m.group(1) + TODAY + m.group(2), s)
    return s
rw("sitemap.xml", sitemap)

print(f"{len(changed)} files changed")
for c in changed:
    print(" ", c)
