"""Briefing as cards: a three-column grid of signals (headline + the first line of the "So what"),
each opening to the full signal across the row, with a "Respond to this signal" email link.
Run from the repo root:
    python3 -B _tools/site/briefing_cards.py
Idempotent. Keeps a managed block in assets/site.css and assets/site.js between
">>> briefing-cards" and "<<< briefing-cards" markers, replacing it when briefing_cards.css/.js change.
The JS rebuilds the existing Briefing markup in the browser, so weekly editions and the archive need
no changes, and without JavaScript the full list still shows.
"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
START, END = "/* >>> briefing-cards (managed by _tools/site/briefing_cards.py) */", "/* <<< briefing-cards */"
LEGACY = {"assets/site.css": "/* Briefing as cards: each signal shows", "assets/site.js": "/* Briefing as cards (see site.css"}
changed = []

def put(path, src):
    s = open(path, encoding="utf-8", newline="").read()
    block = START + "\n" + open(os.path.join(HERE, src), encoding="utf-8").read().strip("\n") + "\n" + END
    if START in s:
        t = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, s, count=1, flags=re.S)
    elif LEGACY[path] in s:
        i = s.index(LEGACY[path])
        tail = s[i:]
        # the unmarked first version was appended last and has a single block comment
        assert tail.count("/*") == 1, f"{path}: unexpected content after the old briefing-cards block"
        t = s[:i] + block + "\n"
    else:
        t = s.rstrip("\n") + "\n\n" + block + "\n"
    if t != s:
        open(path, "w", encoding="utf-8", newline="").write(t)
        changed.append(path)

put("assets/site.css", "briefing_cards.css")
put("assets/site.js", "briefing_cards.js")
print(f"{len(changed)} files changed", *changed)
