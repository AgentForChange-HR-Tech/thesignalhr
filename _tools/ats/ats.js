(function () {
  var D = JSON.parse(document.getElementById("ats-data").textContent);
  var P = D.p, byId = {};
  P.forEach(function (p) { byId[p.id] = p; });
  var CAPN = {}; D.caps.forEach(function (c) { CAPN[c[0]] = c[1]; });
  var selected = [];
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function state() {
    var f = $("#ats-filters");
    var val = function (n) { var el = f.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : "any"; };
    var vals = function (n) { return $$('input[name="' + n + '"]:checked', f).map(function (i) { return i.value; }); };
    return { size: val("size"), hris: val("hris"), models: vals("model"), musts: vals("must") };
  }
  var SCEN_FOR = { smb: "A", mid: "B", ent: "C", any: "B" };
  function evaluate(p, s) {
    var why = [], gaps = [], score = 0;
    if (s.size !== "any" && p.seg.indexOf(s.size) < 0) return { out: "Not built for companies of " + D.segn[s.size] + " employees" };
    if (s.hris !== "any") {
      if (p.hris !== "any" && p.hris !== s.hris) return { out: D.hrisn[p.hris] };
      if (p.hris === s.hris) { why.push("Same suite as your HRIS"); score += 4; }
      else if (p.owned_by === s.hris) { why.push("Owned by your HRIS vendor"); score += 1; }
    }
    if (s.models.length) {
      var hit = s.models.filter(function (m) { return p.models.indexOf(m) >= 0; });
      if (!hit.length) return { out: "Built for " + p.models.map(function (m) { return D.modn[m]; }).join(", ").toLowerCase() + " hiring" };
      hit.forEach(function (m) { why.push("Fits " + D.modn[m].toLowerCase() + " hiring"); score += 2; });
      var miss = s.models.filter(function (m) { return p.models.indexOf(m) < 0; });
      miss.forEach(function (m) { gaps.push("Not built for " + D.modn[m].toLowerCase()); score -= 1; });
    }
    s.musts.forEach(function (k) {
      var v = p.caps[k];
      if (v === 2) { why.push(k === "gov" ? "AI certification published" : CAPN[k]); score += 2; }
      else if (v === 1) { why.push(CAPN[k] + " (partial)"); score += 1; }
      else { gaps.push(k === "gov" ? "No AI certification found" : "No " + CAPN[k].toLowerCase()); }
    });
    var impl = p.impl[SCEN_FOR[s.size]];
    if (s.size !== "any" && /Not a typical/.test(impl)) { gaps.push("Unusual at this size"); score -= 1; }
    return { why: why, gaps: gaps, score: score, impl: impl };
  }
  function card(p, r, s) {
    var sc = SCEN_FOR[s.size];
    return '<article class="fit-card' + (r.gaps.length ? " partial" : "") + '">' +
      '<div class="top"><span class="tag tag-signal">' + esc(D.cats[p.cat]) + '</span><h4>' + esc(p.name) + '</h4><div class="owner">' + esc(p.owner) + "</div></div>" +
      "<p>" + esc(p.best) + "</p>" +
      (r.why.length ? '<ul class="why">' + r.why.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + "</ul>" : "") +
      (r.gaps.length ? '<ul class="gaps">' + r.gaps.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + "</ul>" : "") +
      '<div class="timeline">Typical implementation, scenario ' + sc + " (" + esc(D.scen[sc].name) + "): <b>" + esc(r.impl) + "</b></div>" +
      '<div class="actions"><a href="#p-' + p.id + '" data-open="' + p.id + '">Full profile →</a><label><input type="checkbox" data-cmp="' + p.id + '"' + (selected.indexOf(p.id) >= 0 ? " checked" : "") + "> Compare</label></div></article>";
  }
  function render() {
    var s = state(), strong = [], partial = [], out = [];
    P.forEach(function (p) {
      var r = evaluate(p, s);
      if (r.out) out.push([p, r.out]); else (r.gaps.length ? partial : strong).push([p, r]);
    });
    var byScore = function (a, b) { return b[1].score - a[1].score || a[0].name.localeCompare(b[0].name); };
    strong.sort(byScore); partial.sort(byScore);
    var h = "";
    if (strong.length) h += '<h3 class="group">Strong fits</h3>' + strong.map(function (x) { return card(x[0], x[1], s); }).join("");
    if (partial.length) h += '<h3 class="group">Possible fits, with gaps</h3>' + partial.map(function (x) { return card(x[0], x[1], s); }).join("");
    if (!h) h = "<p>No platform matches every filter. Remove a must-have to widen the list.</p>";
    $("#ats-results").innerHTML = h;
    $("#ats-count").textContent = strong.length + " strong " + (strong.length === 1 ? "fit" : "fits") + ", " + partial.length + " with gaps, " + out.length + " filtered out.";
    var wrap = $("#ats-excluded-wrap");
    if (out.length) {
      wrap.hidden = false;
      $("#ats-excluded-sum").textContent = "Why " + out.length + " platform" + (out.length === 1 ? " was" : "s were") + " filtered out";
      $("#ats-excluded").innerHTML = out.map(function (x) { return "<li><a href=\"#p-" + x[0].id + "\" data-open=\"" + x[0].id + "\">" + esc(x[0].name) + "</a>: " + esc(x[1]) + "</li>"; }).join("");
    } else wrap.hidden = true;
    syncChecks();
  }
  function list(a) { return a && a.length ? "<ul>" + a.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" : "—"; }
  var LV = { 2: "Native", 1: "Partial or add-on", 0: "Not a strength" }, GOVL = { 2: "Certified", 1: "Partial", 0: "None found" };
  function renderCompare() {
    var box = $("#ats-compare");
    if (selected.length < 2) {
      box.innerHTML = '<p class="ats-empty">' + (selected.length === 1 ? "Pick one or two more to compare with <strong>" + esc(byId[selected[0]].name) + "</strong>:" : "Tick <strong>Compare</strong> on two or three platforms in your shortlist, or pick them here:") + "</p>";
      return;
    }
    var ps = selected.map(function (id) { return byId[id]; });
    var row = function (label, fn) { return "<tr><th scope=\"row\">" + label + "</th>" + ps.map(function (p) { return "<td>" + fn(p) + "</td>"; }).join("") + "</tr>"; };
    var grp = function (label) { return '<tr class="group"><th colspan="' + (ps.length + 1) + '">' + label + "</th></tr>"; };
    var h = '<div class="cmp-wrap"><table class="cmp"><thead><tr><th></th>' + ps.map(function (p) { return '<th scope="col">' + esc(p.name) + "</th>"; }).join("") + "</tr></thead><tbody>";
    h += grp("Fit");
    h += row("Category", function (p) { return esc(D.cats[p.cat]); });
    h += row("Owner", function (p) { return esc(p.owner) + '<div class="small">' + esc(p.owner_note) + "</div>"; });
    h += row("Best for", function (p) { return esc(p.best); });
    h += row("Not for", function (p) { return esc(p.notfor); });
    h += row("HRIS", function (p) { return esc(D.hrisn[p.hris]); });
    h += grp("Capabilities");
    D.caps.forEach(function (c) { h += row(esc(c[1]), function (p) { var v = p.caps[c[0]]; return '<span class="lv lv-' + v + '"></span>' + (c[0] === "gov" ? GOVL[v] : LV[v]); }); });
    h += grp("AI");
    h += row("In production", function (p) { return list(p.ai_live); });
    h += row("Announced or beta", function (p) { return list(p.ai_next); });
    h += row("Governance evidence", function (p) { return esc(p.gov); });
    h += grp("Cost and effort");
    h += row("How it's priced", function (p) { return esc(p.pricing); });
    h += row("Cost traps", function (p) { return list(p.traps); });
    ["A", "B", "C"].forEach(function (k) { h += row("Implementation " + k + " · " + esc(D.scen[k].name), function (p) { return esc(p.impl[k]); }); });
    h += grp("Due diligence");
    h += row("Watch-outs", function (p) { return list(p.watch); });
    h += row("Ask in the demo", function (p) { return list(p.ask); });
    h += "</tbody></table></div>";
    box.innerHTML = h;
  }
  function syncChecks() {
    $$("input[data-cmp]").forEach(function (i) { i.checked = selected.indexOf(i.getAttribute("data-cmp")) >= 0; });
    var tray = $("#ats-tray");
    tray.hidden = selected.length === 0;
    $("#ats-tray-names").textContent = selected.length ? "Comparing: " + selected.map(function (id) { return byId[id].name; }).join(", ") + (selected.length < 2 ? " (pick one more)" : "") : "";
  }
  function toggle(id, on) {
    var i = selected.indexOf(id);
    if (on && i < 0) { if (selected.length >= 3) selected.shift(); selected.push(id); }
    if (!on && i >= 0) selected.splice(i, 1);
    syncChecks(); renderCompare();
    if (typeof gtag === "function") gtag("event", "ats_compare_toggle", { event_label: id, value: selected.length });
  }
  document.addEventListener("change", function (e) {
    var t = e.target;
    if (t.matches("input[data-cmp]")) toggle(t.getAttribute("data-cmp"), t.checked);
    else if (t.closest && t.closest("#ats-filters")) {
      render();
      if (typeof gtag === "function") gtag("event", "ats_filter", { event_label: t.name + ":" + t.value });
    }
  });
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-open]");
    if (a) { var d = document.getElementById("p-" + a.getAttribute("data-open")); if (d) d.open = true; }
    if (e.target.id === "ats-clear") { selected = []; syncChecks(); renderCompare(); }
    if (e.target.id === "ats-expand") {
      e.preventDefault();
      var all = $$("details.profile"), open = all.some(function (d) { return !d.open; });
      all.forEach(function (d) { d.open = open; });
      e.target.textContent = open ? "Collapse all" : "Expand all";
    }
  });
  if (location.hash && location.hash.indexOf("#p-") === 0) { var d = document.querySelector(location.hash); if (d) d.open = true; }
  render(); renderCompare();
})();
