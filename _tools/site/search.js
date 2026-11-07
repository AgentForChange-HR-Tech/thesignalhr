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
