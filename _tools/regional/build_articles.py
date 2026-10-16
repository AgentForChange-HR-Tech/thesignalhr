"""Write the regional insight articles from articles.py using an existing insight page as the template.
Usage (repo root): python3 -B _tools/regional/build_articles.py insights/eu-ai-act-hr-deadline/index.html
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from articles import ARTICLES
E = lambda s: html.escape(s, quote=True)
LABEL = {"americas": "Americas", "emea": "EMEA", "apac": "APAC", "global": "Global"}
tpl = open(sys.argv[1], encoding="utf-8").read()
head0 = tpl[:tpl.index("<main")]
tail = tpl[tpl.index('  <section class="section" style="padding-top:0;">\n    <div class="wrap">\n      <div class="news-band">'):]
for a in ARTICLES:
    url = f"https://thesignalhr.com/insights/{a['slug']}/"
    h = head0
    h = re.sub(r"<title>.*?</title>", f"<title>{E(a['seo_title'])}</title>", h, flags=re.S)
    for attr in ['name="description"', 'property="og:description"', 'name="twitter:description"']:
        h = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(a["desc"]) + m.group(2), h)
    for attr in ['property="og:title"', 'name="twitter:title"']:
        h = re.sub(r'(<meta %s content=")[^"]*(">)' % re.escape(attr), lambda m: m.group(1) + E(a["seo_title"]) + m.group(2), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + url + m.group(2), h)
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
          "datePublished": "2026-10-16", "dateModified": "2026-10-16",
          "author": {"@type": "Person", "name": "Alex Rivera", "url": "https://thesignalhr.com/about/"},
          "publisher": {"@type": "Organization", "name": "The Signal HR", "url": "https://thesignalhr.com/"},
          "mainEntityOfPage": url, "about": LABEL[a["region"]]}
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld) + "</script>", h, flags=re.S)
    src = "".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a></li>' for t, u in a["sources"])
    main = f'''<main id="main">
<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">The Signal</a><span>›</span><a href="/insights/">Insights</a><span>›</span>{E(a["crumb"])}</nav></div>

  <section class="article-header">
    <div class="prose-wrap">
      <span class="tag {a["tag"][1]}">{a["tag"][0]}</span> <span class="region-tag">{LABEL[a["region"]]}</span>
      <h1>{a["h1"]}</h1>
      <p class="standfirst">{E(a["standfirst"])}</p>
      <div class="article-meta"><span>By Alex Rivera</span><span>October 16, 2026</span><span>{a["minutes"]} min read</span></div>
    </div>
  </section>
  <div class="prose-wrap prose">{a["body"]}
    <p><a href="/coverage/#calendar">See every upcoming date in the regional calendar →</a></p>
    <div class="sources"><strong>Sources</strong><ul>{src}</ul></div>
  </div>
'''
    os.makedirs(f"insights/{a['slug']}", exist_ok=True)
    open(f"insights/{a['slug']}/index.html", "w", encoding="utf-8", newline="").write(h + main + tail)
    words = len(re.sub(r"<[^>]+>", " ", a["body"]).split())
    print("wrote", a["slug"], words, "words")
