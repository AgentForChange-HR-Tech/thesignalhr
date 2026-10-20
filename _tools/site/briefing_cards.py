"""Briefing as cards: a three-column grid of signals (headline + the first line of the "So what"),
each opening to the full signal across the row. Run from the repo root:
    python3 -B _tools/site/briefing_cards.py
Idempotent. Adds CSS to assets/site.css and JS to assets/site.js. The JS rebuilds the existing
Briefing markup in the browser, so weekly editions and the archive need no changes, and without
JavaScript the full list still shows.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, "briefing_cards.css"), encoding="utf-8").read()
JS = open(os.path.join(HERE, "briefing_cards.js"), encoding="utf-8").read()
changed = []
def add(path, block, marker):
    s = open(path, encoding="utf-8", newline="").read()
    if marker in s:
        return
    open(path, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n\n" + block.strip("\n") + "\n")
    changed.append(path)
add("assets/site.css", CSS, "Briefing as cards")
add("assets/site.js", JS, "Briefing as cards")
print(f"{len(changed)} files changed", *changed)
