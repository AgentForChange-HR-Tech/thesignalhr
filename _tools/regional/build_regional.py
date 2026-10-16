"""Inject the regional radar and calendar into /coverage/ and the next dates into /briefing/.
Usage (repo root): python3 -B _tools/regional/build_regional.py [YYYY-MM-DD]
The optional date is "today" for the Briefing's "Dates to watch" (defaults to the system date).
Pages must contain the marker pairs <!-- regional:radar -->…<!-- /regional:radar -->,
<!-- regional:calendar -->…<!-- /regional:calendar --> (coverage) and <!-- regional:dates -->…<!-- /regional:dates --> (briefing).
"""
import datetime, html, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import regional as R

E = lambda s: html.escape(str(s), quote=True)
LABEL = {"americas": "Americas", "emea": "EMEA", "apac": "APAC", "global": "Global"}
today = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()

def cal_rows(rows):
    out = []
    for iso, when, where, reg, what, st, su in rows:
        out.append(f'<tr data-region="{reg}"><td class="when">{E(when)}</td><td class="where">{E(where)} <span class="region-tag">{LABEL[reg]}</span></td>'
                   f'<td>{E(what)} <a href="{E(su)}" target="_blank" rel="noopener">{E(st)}</a></td></tr>')
    return "".join(out)

def table(rows):
    return ('<div class="cal-wrap"><table class="cal"><thead><tr><th scope="col">Date</th><th scope="col">Where</th><th scope="col">What changes</th></tr></thead>'
            f'<tbody>{cal_rows(rows)}</tbody></table></div>')

def radar():
    cols = []
    for reg, title in (("americas", "Americas"), ("emea", "Europe, Middle East &amp; Africa"), ("apac", "Asia-Pacific")):
        items = []
        for r, h, t, srcs, link in [x for x in R.RADAR if x[0] == reg]:
            more = f' <a href="{link}">Read the analysis →</a>' if link else ""
            src = " · ".join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(n)}</a>' for n, u in srcs)
            items.append(f'<article class="radar-item" data-region="{r}"><h4>{E(h)}</h4><p>{E(t)}{more}</p><p class="src">Sources: {src}</p></article>')
        cols.append(f'<div class="radar-col" data-region-group><h3>{title}</h3>{"".join(items)}</div>')
    return f'<div class="radar">{"".join(cols)}</div>'

def inject(path, name, content):
    s = open(path, encoding="utf-8").read()
    pat = re.compile(r"(<!-- regional:%s -->).*?(<!-- /regional:%s -->)" % (name, name), re.S)
    assert pat.search(s), f"{path}: missing markers for {name}"
    s = pat.sub(lambda m: m.group(1) + content + m.group(2), s)
    open(path, "w", encoding="utf-8", newline="").write(s)

cal = sorted(R.CALENDAR, key=lambda x: x[0])
upcoming = [c for c in cal if c[0] >= today]
inject("coverage/index.html", "radar", radar())
inject("coverage/index.html", "calendar", table(upcoming))
inject("briefing/index.html", "dates", table(upcoming[:6]))
print(f"radar {len(R.RADAR)} items; calendar {len(upcoming)} upcoming from {today}; briefing shows {min(6, len(upcoming))}")
