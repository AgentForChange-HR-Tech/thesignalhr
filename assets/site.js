/* The Signal HR — shared behavior (theme, mobile nav, analytics events) */
(function () {
  var root = document.documentElement;

  /* Theme: system preference, overridable, persisted in-page via cookie-free attribute.
     (No localStorage dependency for first paint — set inline in <head> snippet.) */
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("signal-theme", t); } catch (e) {}
    var btn = document.querySelector(".theme-toggle");
    if (btn) btn.textContent = t === "dark" ? "☀ Light" : "◐ Dark";
  }
  window.addEventListener("DOMContentLoaded", function () {
    var saved = null;
    try { saved = localStorage.getItem("signal-theme"); } catch (e) {}
    var prefers = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    setTheme(saved || prefers);

    var btn = document.querySelector(".theme-toggle");
    if (btn) btn.addEventListener("click", function () {
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });

    /* Mobile nav */
    var burger = document.querySelector(".nav-burger");
    var links = document.querySelector(".nav-links");
    if (burger && links) {
      burger.addEventListener("click", function () {
        var open = links.classList.toggle("open");
        burger.setAttribute("aria-expanded", open ? "true" : "false");
      });
      links.addEventListener("click", function (e) {
        if (e.target.tagName === "A") { links.classList.remove("open"); burger.setAttribute("aria-expanded", "false"); }
      });
    }

    /* Lightweight analytics events (GA4 if present) */
    document.querySelectorAll('a[href*="substack.com"]').forEach(function (a) {
      a.addEventListener("click", function () {
        // the nav button scrolls to an on-page form when there is one (see Subscribe below), so it isn't an off-site click
        if (a.classList.contains("nav-cta") && document.querySelector('iframe[src*="substack.com/embed"]')) return;
        if (typeof gtag === "function") {
          gtag("event", "substack_cta_click", { event_category: "conversion", event_label: location.pathname });
        }
      });
    });
  });
})();

/* Region filter (Briefing, Insights, Coverage): All · Americas · EMEA · APAC.
   Items carry data-region="americas emea apac global"; Global items show under every region.
   Items inside [data-region-dim] are dimmed rather than hidden; items inside [data-region-nocount]
   filter but don't count toward the note. Choice is remembered per viewer; ?region= overrides it. */
(function () {
  var KEY = "signal-region", NAMES = { all: "All regions", americas: "Americas", emea: "EMEA", apac: "APAC" };
  function init() {
    var bars = Array.prototype.slice.call(document.querySelectorAll("[data-region-bar]"));
    if (!bars.length) return;
    var q = null, saved = null;
    try { q = new URLSearchParams(location.search).get("region"); } catch (e) {}
    try { saved = localStorage.getItem(KEY); } catch (e) {}
    function apply(r, byUser) {
      try { localStorage.setItem(KEY, r); } catch (e) {}
      var shown = 0, total = 0, specific = 0;
      Array.prototype.forEach.call(document.querySelectorAll("[data-region]"), function (el) {
        var regs = (el.getAttribute("data-region") || "").split(/\s+/);
        var match = r === "all" || regs.indexOf(r) >= 0 || regs.indexOf("global") >= 0;
        var dim = !!(el.closest && el.closest("[data-region-dim]"));
        var nocount = !!(el.closest && el.closest("[data-region-nocount]"));
        el.classList.remove("region-hidden", "region-dim");
        if (!match) el.classList.add(dim ? "region-dim" : "region-hidden");
        if (!dim && !nocount) { total++; if (match) shown++; if (r !== "all" && regs.indexOf(r) >= 0) specific++; }
      });
      Array.prototype.forEach.call(document.querySelectorAll("[data-region-group]"), function (g) {
        var kids = g.querySelectorAll("[data-region]"), any = false;
        Array.prototype.forEach.call(kids, function (k) { if (!k.classList.contains("region-hidden")) any = true; });
        g.hidden = kids.length > 0 && !any;
      });
      bars.forEach(function (bar) {
        Array.prototype.forEach.call(bar.querySelectorAll("button[data-r]"), function (b) {
          b.setAttribute("aria-pressed", b.getAttribute("data-r") === r ? "true" : "false");
        });
        var note = bar.querySelector(".region-note");
        if (note) note.textContent = r === "all" ? "" : specific
          ? "Showing " + shown + " of " + total + ": " + NAMES[r] + " plus items marked Global."
          : "Nothing " + NAMES[r] + "-specific here yet, so items marked Global are shown.";
      });
      if (byUser && typeof gtag === "function") gtag("event", "region_filter", { event_label: r, page_path: location.pathname });
    }
    bars.forEach(function (bar) {
      bar.hidden = false;
      bar.addEventListener("click", function (e) {
        var b = e.target.closest && e.target.closest("button[data-r]");
        if (b) apply(b.getAttribute("data-r"), true);
      });
    });
    apply(NAMES[q] ? q : (NAMES[saved] ? saved : "all"), false);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();

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

/* >>> briefing-cards (managed by _tools/site/briefing_cards.py) */
/* Briefing as cards (see site.css "Briefing as cards"). Progressive: without JS the full list shows. */
(function () {
  var items = Array.prototype.slice.call(document.querySelectorAll("article.brief-item"));
  if (items.length < 3 || document.querySelector(".brief-cards")) return;
  var host = items[0].parentNode;
  if (!items.every(function (it) { return it.parentNode === host; })) return;
  // the list lives in a narrow reading column; cards get the full page width
  if (host.style && host.style.maxWidth) host.style.maxWidth = "";
  var grid = document.createElement("div");
  grid.className = "brief-cards";
  host.insertBefore(grid, items[0]);
  var first = function (t) { var m = String(t).replace(/\s+/g, " ").trim().match(/^.*?[.!?](?=\s+[A-Z"“(]|$)/); return m ? m[0] : String(t).trim(); };
  var send = function (name, p) { if (typeof gtag === "function") gtag("event", name, p); };
  var EMAIL = "alex@thesignalhr.com";
  var kicker = document.querySelector(".article-header .kicker");
  var EDITION = kicker ? kicker.textContent.replace(/\s+/g, " ").trim() : "The Briefing";
  function setOpen(it, open) {
    it.classList.toggle("is-open", open);
    it.querySelector(".b-more").hidden = !open;
    var b = it.querySelector(".b-open");
    b.textContent = open ? "Show less" : "Read the signal →";
    b.setAttribute("aria-expanded", String(open));
  }
  items.forEach(function (it, i) {
    if (!it.id) it.id = "signal-" + (i + 1);
    var h = it.querySelector("h3"), body = h ? h.parentNode : null, sw = it.querySelector(".so-what");
    if (!body) return;
    var more = document.createElement("div");
    more.className = "b-more"; more.hidden = true; more.id = it.id + "-more";
    Array.prototype.slice.call(body.children).forEach(function (el) { if (el !== h) more.appendChild(el); });
    if (sw) {   // so-what first: it's the point of each signal
      more.insertBefore(sw, more.firstChild);
    }
    // respond by email: one reader, one signal, straight to the inbox (no public comments)
    var respond = document.createElement("p");
    respond.className = "b-respond";
    var a = document.createElement("a");
    a.href = "mailto:" + EMAIL + "?subject=" + encodeURIComponent("Re: " + (h.textContent || "").replace(/\s+/g, " ").trim()) +
      "&body=" + encodeURIComponent("On this signal from " + EDITION + ":\n\n");
    a.textContent = "Respond to this signal →";
    a.addEventListener("click", function () { send("briefing_respond", { item: i + 1, page_path: location.pathname }); });
    respond.appendChild(a);
    respond.appendChild(document.createTextNode(" Replies go to Alex, not a public thread."));
    more.appendChild(respond);
    var take = document.createElement("p");
    take.className = "b-take";
    take.textContent = sw ? first(sw.textContent.replace(/^\s*So what\s*·\s*/i, "")) : "";
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "b-open"; btn.setAttribute("aria-controls", more.id);
    body.appendChild(take); body.appendChild(more);
    it.appendChild(btn);
    setOpen(it, false);
    btn.addEventListener("click", function () {
      var open = !it.classList.contains("is-open");
      setOpen(it, open);
      if (open) { it.scrollIntoView({ block: "start", behavior: "smooth" }); send("briefing_open", { item: i + 1, page_path: location.pathname }); }
    });
  });
  items.forEach(function (it) { grid.appendChild(it); });
  var tools = document.createElement("div");
  tools.className = "brief-tools";
  tools.innerHTML = '<button type="button" aria-expanded="false">Expand all</button>';
  host.insertBefore(tools, grid);
  tools.firstChild.addEventListener("click", function () {
    var open = this.getAttribute("aria-expanded") !== "true";
    items.forEach(function (it) { setOpen(it, open); });
    this.setAttribute("aria-expanded", String(open));
    this.textContent = open ? "Collapse all" : "Expand all";
  });
  var openHash = function () { var t = location.hash && document.getElementById(location.hash.slice(1)); if (t && t.classList.contains("brief-item")) setOpen(t, true); };
  window.addEventListener("hashchange", openHash); openHash();
})();
/* <<< briefing-cards */

/* >>> site-search (managed by _tools/site/search_index.py) */
/* Site search (see site.css "Site search"). Opens from the header button, "/" or Ctrl/Cmd+K.
   Results are ordered only by how well they match the reader's words; ties go alphabetically. */
(function () {
  var INDEX_URL = "/assets/search-index.json";
  var ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m20 20-3.5-3.5"></path></svg>';
  var STOP = { the: 1, a: 1, an: 1, of: 1, and: 1, or: 1, to: 1, in: 1, for: 1, on: 1, with: 1, is: 1, are: 1, what: 1, how: 1, does: 1, do: 1, about: 1 };
  var items = null, loading = null, overlay, input, list, msg, sel = -1, lastLogged = "", logTimer;
  var send = function (name, p) { if (typeof gtag === "function") gtag("event", name, p); };
  var norm = function (s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };

  function load() {
    if (items) return Promise.resolve(items);
    if (!loading) loading = fetch(INDEX_URL).then(function (r) { return r.json(); }).then(function (d) {
      items = d.items.map(function (e) { e._t = norm(e.t); e._s = norm(e.s); e._x = norm(e.x); return e; });
      return items;
    });
    return loading;
  }
  function terms(q) {
    return norm(q).split(/[^a-z0-9]+/).filter(function (t) { return t && !STOP[t]; });
  }
  function wordHits(hay, t) {   // matches at the start of a word
    var re = new RegExp("(^|[^a-z0-9])" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g"), n = 0;
    while (re.exec(hay) && n < 5) n++;
    return n;
  }
  function score(e, ts, phrase) {
    var total = 0;
    for (var i = 0; i < ts.length; i++) {
      var t = ts[i], ti = wordHits(e._t, t), si = wordHits(e._s, t), xi = wordHits(e._x, t);
      if (!ti && !si && !xi) return 0;   // every word must appear
      total += ti * 8 + si * 3 + xi;
    }
    if (phrase.length > 3) { if (e._t.indexOf(phrase) >= 0) total += 12; else if (e._x.indexOf(phrase) >= 0) total += 4; }
    return total;
  }
  function snippet(e, ts) {
    var src = e.x || e.s, low = norm(src), at = -1;
    ts.forEach(function (t) { var i = low.search(new RegExp("(^|[^a-z0-9])" + t)); if (i >= 0 && (at < 0 || i < at)) at = i; });
    var start = Math.max(0, at - 60), out = (start > 0 ? "…" : "") + src.slice(start, start + 190) + (src.length > start + 190 ? "…" : "");
    if (at < 0) out = e.s || src.slice(0, 190);
    var h = esc(out);
    ts.forEach(function (t) { h = h.replace(new RegExp("(^|[^A-Za-z0-9])(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "[a-z0-9]*)", "gi"), "$1<mark>$2</mark>"); });
    return h;
  }
  function render() {
    var q = input.value.trim(), ts = terms(q);
    sel = -1;
    if (!ts.length) { list.innerHTML = ""; msg.textContent = "Search the Briefing, Insights, comparisons, platform profiles and hiring-AI rules."; msg.hidden = false; return; }
    load().then(function (all) {
      if (input.value.trim() !== q) return;
      var phrase = norm(q).replace(/\s+/g, " ");
      var hits = all.map(function (e) { return [score(e, ts, phrase), e]; }).filter(function (x) { return x[0] > 0; });
      hits.sort(function (a, b) { return b[0] - a[0] || a[1].t.localeCompare(b[1].t); });
      var top = hits.slice(0, 15);
      msg.hidden = !!top.length;
      if (!top.length) msg.textContent = "No matches for “" + q + "”. Try fewer or different words.";
      list.innerHTML = top.map(function (x, i) {
        var e = x[1];
        return '<a href="' + esc(e.u) + '" role="option" id="s-opt-' + i + '" data-i="' + i + '"><span class="s-kind">' + esc(e.k) + (e.d ? "<span>" + esc(e.d) + "</span>" : "") + '</span><span class="s-title">' + esc(e.t) + '</span><span class="s-snip">' + snippet(e, ts) + "</span></a>";
      }).join("");
      clearTimeout(logTimer);
      logTimer = setTimeout(function () {
        if (q.length >= 3 && q !== lastLogged) { lastLogged = q; send("search", { search_term: q.slice(0, 100), results: hits.length }); }
      }, 1200);
    }, function () { msg.textContent = "Search isn't available right now."; msg.hidden = false; });
  }
  function move(d) {
    var opts = list.querySelectorAll("a");
    if (!opts.length) return;
    sel = (sel + d + opts.length) % opts.length;
    opts.forEach(function (o, i) { o.setAttribute("aria-selected", String(i === sel)); });
    opts[sel].scrollIntoView({ block: "nearest" });
    input.setAttribute("aria-activedescendant", opts[sel].id);
  }
  function open() {
    overlay.hidden = false;
    document.documentElement.style.overflow = "hidden";
    input.focus(); input.select();
    load(); render();
  }
  function close() {
    overlay.hidden = true;
    document.documentElement.style.overflow = "";
  }
  function build() {
    overlay = document.createElement("div");
    overlay.className = "search-overlay"; overlay.hidden = true;
    overlay.innerHTML = '<div class="search-panel" role="dialog" aria-modal="true" aria-label="Search The Signal HR">' +
      '<div class="search-bar">' + ICON + '<input type="search" placeholder="Search The Signal HR" aria-label="Search The Signal HR" aria-controls="search-results" autocomplete="off" spellcheck="false"><button type="button" class="s-close">Esc</button></div>' +
      '<p class="search-msg" aria-live="polite"></p><div class="search-results" id="search-results" role="listbox"></div>' +
      '<p class="search-foot">Results are ordered only by how well they match your words.</p></div>';
    document.body.appendChild(overlay);
    input = overlay.querySelector("input"); list = overlay.querySelector(".search-results"); msg = overlay.querySelector(".search-msg");
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") { var o = list.querySelectorAll("a")[sel < 0 ? 0 : sel]; if (o) { e.preventDefault(); o.click(); } }
    });
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay || (e.target.closest && e.target.closest(".s-close"))) close();
      var a = e.target.closest && e.target.closest(".search-results a");
      if (a) {
        send("search_click", { search_term: input.value.trim().slice(0, 100), link_url: a.getAttribute("href") });
        var here = location.pathname, dest = a.getAttribute("href");
        close();
        // same page: let the hash change open the right signal or profile
        if (dest.split("#")[0] === here && dest.indexOf("#") > 0) { e.preventDefault(); location.hash = dest.split("#")[1]; var t = document.getElementById(dest.split("#")[1]); if (t) { if (t.tagName === "DETAILS") t.open = true; t.scrollIntoView(); } }
      }
    });
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "search-toggle"; btn.setAttribute("aria-label", "Search");
    btn.innerHTML = ICON + '<span class="s-label">Search</span>';
    btn.addEventListener("click", open);
    var theme = document.querySelector(".theme-toggle");
    if (theme && theme.parentNode) theme.parentNode.insertBefore(btn, theme);
    else { var hi = document.querySelector(".header-inner"); if (hi) hi.appendChild(btn); }
    document.addEventListener("keydown", function (e) {
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test((document.activeElement || {}).tagName || "") || (document.activeElement && document.activeElement.isContentEditable);
      if (e.key === "Escape" && !overlay.hidden) { close(); btn.focus(); }
      else if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) { e.preventDefault(); overlay.hidden ? open() : close(); }
      else if (e.key === "/" && !typing && overlay.hidden) { e.preventDefault(); open(); }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build); else build();
})();
/* <<< site-search */
