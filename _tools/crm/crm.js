(function () {
  var D = JSON.parse(document.getElementById("ats-data").textContent);
  var P = D.p, byId = {};
  P.forEach(function (p) { byId[p.id] = p; });
  var CAPN = {}; D.caps.forEach(function (c) { CAPN[c[0]] = c[1]; });
  var selected = [];
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ga = function (name, params) { if (typeof gtag === "function") gtag("event", name, params); };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  // ---------- Finder ----------
  function state() {
    var f = $("#ats-filters");
    var val = function (n) { var el = f.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : "any"; };
    var vals = function (n) { return $$('input[name="' + n + '"]:checked', f).map(function (i) { return i.value; }); };
    return { size: val("size"), ats: val("ats"), models: vals("model"), musts: vals("must") };
  }
  function evaluate(p, s) {
    var why = [], gaps = [], score = 0;
    if (s.size !== "any" && p.seg.indexOf(s.size) < 0) return { out: "Not built for companies of " + D.segn[s.size] + " employees" };
    if (s.ats !== "any") {
      if (p.req) {
        if (p.req === s.ats) { why.push("Built into your ATS"); score += 4; }
        else if (p.alt && p.alt[s.ats]) { gaps.push(p.alt[s.ats]); }
        else return { out: "Requires " + D.reqn[p.req] };
      } else if (p.ats_int.indexOf(s.ats) >= 0) { why.push("Documented integration with " + D.atsn[s.ats]); score += 3; }
      else if (s.ats !== "other") {
        gaps.push(p.claims_other ? "Says it works with other ATS platforms; none documented for yours" : "No documented integration with " + D.atsn[s.ats]);
        score -= 1;
      }
    }
    if (s.models.length) {
      var hit = s.models.filter(function (m) { return p.models.indexOf(m) >= 0; });
      if (!hit.length) return { out: "Built for " + p.models.map(function (m) { return D.modn[m]; }).join(", ").toLowerCase() + " hiring" };
      hit.forEach(function (m) { why.push("Fits " + D.modn[m].toLowerCase() + " hiring"); score += 2; });
      s.models.filter(function (m) { return p.models.indexOf(m) < 0; }).forEach(function (m) { gaps.push("Not built for " + D.modn[m].toLowerCase()); score -= 1; });
    }
    s.musts.forEach(function (k) {
      var v = p.caps[k];
      if (v === 2) { why.push(k === "gov" ? "AI certification published" : CAPN[k]); score += 2; }
      else if (v === 1) { why.push(CAPN[k] + " (partial)"); score += 1; }
      else { gaps.push(k === "gov" ? "No AI certification found" : "No " + CAPN[k].toLowerCase()); }
    });
    return { why: why, gaps: gaps, score: score };
  }
  function card(p, r) {
    return '<article class="fit-card' + (r.gaps.length ? " partial" : "") + '">' +
      '<div class="top"><span class="tag tag-signal">' + esc(D.cats[p.cat]) + '</span><h4>' + esc(p.name) + '</h4><div class="owner">' + esc(p.owner) + "</div></div>" +
      "<p>" + esc(p.best) + "</p>" +
      (r.why.length ? '<ul class="why">' + r.why.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + "</ul>" : "") +
      (r.gaps.length ? '<ul class="gaps">' + r.gaps.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + "</ul>" : "") +
      '<div class="works">' + esc(p.works) + "</div>" +
      '<div class="timeline">Delivery: <b>' + esc(p.delivery) + "</b></div>" +
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
    if (strong.length) h += '<h3 class="group">Strong fits</h3>' + strong.map(function (x) { return card(x[0], x[1]); }).join("");
    if (partial.length) h += '<h3 class="group">Possible fits, with gaps</h3>' + partial.map(function (x) { return card(x[0], x[1]); }).join("");
    if (!h) h = "<p>No platform matches every filter. Remove a must-have to widen the list.</p>";
    $("#ats-results").innerHTML = h;
    $("#ats-count").textContent = strong.length + " strong " + (strong.length === 1 ? "fit" : "fits") + ", " + partial.length + " with gaps, " + out.length + " filtered out.";
    var wrap = $("#ats-excluded-wrap");
    if (out.length) {
      wrap.hidden = false;
      $("#ats-excluded-sum").textContent = "Why " + out.length + " platform" + (out.length === 1 ? " was" : "s were") + " filtered out";
      $("#ats-excluded").innerHTML = out.map(function (x) { return '<li><a href="#p-' + x[0].id + '" data-open="' + x[0].id + '">' + esc(x[0].name) + "</a>: " + esc(x[1]) + "</li>"; }).join("");
    } else wrap.hidden = true;
    syncChecks();
  }

  // ---------- Compare ----------
  function list(a) { return a && a.length ? "<ul>" + a.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" : "—"; }
  var LV = { 2: "Native", 1: "Partial or add-on", 0: "Not a strength" }, GOVL = { 2: "Certified", 1: "Partial", 0: "None found" };
  function renderCompare() {
    var box = $("#ats-compare");
    if (selected.length < 2) {
      box.innerHTML = '<p class="ats-empty">' + (selected.length === 1 ? "Pick one or two more to compare with <strong>" + esc(byId[selected[0]].name) + "</strong>:" : "Tick <strong>Compare</strong> on two or three platforms in your shortlist, or pick them here:") + "</p>";
      return;
    }
    var ps = selected.map(function (id) { return byId[id]; });
    var row = function (label, fn) { return '<tr><th scope="row">' + label + "</th>" + ps.map(function (p) { return "<td>" + fn(p) + "</td>"; }).join("") + "</tr>"; };
    var grp = function (label) { return '<tr class="group"><th colspan="' + (ps.length + 1) + '">' + label + "</th></tr>"; };
    var h = '<div class="cmp-wrap"><table class="cmp"><thead><tr><th></th>' + ps.map(function (p) { return '<th scope="col">' + esc(p.name) + "</th>"; }).join("") + "</tr></thead><tbody>";
    h += grp("Fit");
    h += row("Category", function (p) { return esc(D.cats[p.cat]); });
    h += row("Owner", function (p) { return esc(p.owner) + '<div class="small">' + esc(p.owner_note) + "</div>"; });
    h += row("Best for", function (p) { return esc(p.best); });
    h += row("Not for", function (p) { return esc(p.notfor); });
    h += row("ATS", function (p) { return esc(p.works); });
    h += grp("Capabilities");
    D.caps.forEach(function (c) { h += row(esc(c[1]), function (p) { var v = p.caps[c[0]]; return '<span class="lv lv-' + v + '"></span>' + (c[0] === "gov" ? GOVL[v] : LV[v]); }); });
    h += grp("AI");
    h += row("In production", function (p) { return list(p.ai_live); });
    h += row("Announced or beta", function (p) { return list(p.ai_next); });
    h += row("Governance evidence", function (p) { return esc(p.gov); });
    h += grp("Cost and effort");
    h += row("How it's priced", function (p) { return esc(p.pricing); });
    h += row("Cost traps", function (p) { return list(p.traps); });
    h += row("Delivery", function (p) { return esc(p.delivery); });
    h += row("What drives the effort", function (p) { return esc(p.impl_note); });
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
    ga("crm_compare_toggle", { event_label: id, value: selected.length });
  }

  // ---------- Step 1: do you need a separate CRM? (no timeline estimates) ----------
  var F = D.factors, FBY = {}, ANS = {}, KIND = {};
  D.groups.forEach(function (g) { KIND[g[0]] = g[3]; });
  F.forEach(function (f) { FBY[f.id] = f; });
  function lvl(id) { return ANS[id] == null ? null : FBY[id].opts[ANS[id]][1]; }
  function kindOf(f) { return KIND[f.group]; }
  function tagText(f, v) { return D.levels[kindOf(f)][v]; }
  function paintDriver(id) {
    var el = document.getElementById("d-" + id), v = lvl(id), tag = $(".dlevel", el), f = FBY[id];
    el.classList.remove("lv-0", "lv-1", "lv-2", "lv-n");
    if (v == null) { tag.hidden = true; return; }
    // need answers aren't good or bad, so they get a neutral colour; risk answers are coloured by size
    var cls = kindOf(f) === "need" ? "n" : String(v);
    el.classList.remove("lv-n"); el.classList.add("lv-" + cls);
    tag.className = "dlevel l" + cls; tag.textContent = tagText(f, v); tag.hidden = false;
    if (v > 0) $(".dhelp", el).open = true;
  }
  function verdict() {
    var needF = F.filter(function (f) { return f.group === "need"; });
    var answered = needF.filter(function (f) { return ANS[f.id] != null; });
    if (answered.length < 2) return null;
    var score = 0; answered.forEach(function (f) { score += lvl(f.id); });
    var pct = score / (2 * answered.length);
    var readyMajors = F.filter(function (f) { return f.group === "ready" && lvl(f.id) === 2; }).length;
    if (ANS.own === 2) return { cls: "v-own", t: "Start with the CRM you already license", d: "Pilot it on one hiring program with a named campaign owner before buying another. Where it falls short, the gaps tell you which capabilities to shortlist on." };
    if (pct < 0.4) return { cls: "v-low", t: "The CRM features in your ATS are probably enough", d: "Talent pools, saved searches and basic email cover occasional pipelining. Revisit when repeat roles, events or hard-to-fill roles grow." };
    if (readyMajors >= 2 || lvl("owner") === 2) return { cls: "v-gaps", t: "A CRM could pay off, but close the gaps first", d: "Without a campaign owner, clean data and a working ATS sync, a CRM becomes an expensive database. Fix the major gaps below before you buy." };
    return { cls: "v-buy", t: "A dedicated CRM is likely worth evaluating", d: "Shortlist in Step 2 with the capabilities below, check the CRM inside your ATS or suite first, and take the questions into demos." };
  }
  function prioCaps() {
    var caps = [];
    Object.keys(D.needcaps).forEach(function (id) {
      if ((lvl(id) || 0) > 0) D.needcaps[id].forEach(function (c) { if (caps.indexOf(c) < 0) caps.push(c); });
    });
    return caps;
  }
  function questionList() {
    return D.aud.map(function (a) {
      var qs = [];
      F.forEach(function (f) {
        var prio = f.id === "own" ? ANS.own != null : (lvl(f.id) || 0) > 0;
        f.ask.forEach(function (x) { if (x[0] === a[0]) qs.push({ q: x[1], f: f, prio: prio }); });
      });
      qs.sort(function (x, y) { return (y.prio ? 1 : 0) - (x.prio ? 1 : 0); });
      return { aud: a, qs: qs };
    }).filter(function (g) { return g.qs.length; });
  }
  function renderSummary() {
    var out = $("#drivers-out");
    if (!out) return;
    var v = verdict(), h = "";
    var answered = F.filter(function (f) { return ANS[f.id] != null; });
    if (!v) {
      h = '<p class="sum-line">Answer at least two questions under "What you need it for" to see a verdict.' + (answered.length ? " " + answered.length + " of " + F.length + " answered." : "") + "</p>";
    } else {
      h = '<div class="verdict ' + v.cls + '"><h4>' + esc(v.t) + "</h4><p>" + esc(v.d) + "</p></div>";
      var caps = prioCaps();
      if (caps.length) h += '<div class="prio-caps"><span>Capabilities to prioritize:</span>' + caps.map(function (c) { return '<span class="cap">' + esc(CAPN[c]) + "</span>"; }).join("") + '<button type="button" class="btn btn-ghost" id="drivers-apply">Apply to the finder</button></div>';
      var risks = F.filter(function (f) { return kindOf(f) === "risk" && (lvl(f.id) || 0) > 0; });
      risks.sort(function (a, b) { return lvl(b.id) - lvl(a.id); });
      if (risks.length) h += '<h4 class="sum-qh">Gaps to close</h4><ul class="sum-list">' + risks.map(function (f) {
        var x = lvl(f.id);
        return '<li class="lv-' + x + '"><b>' + esc(f.name) + '</b> <span class="dlevel l' + x + '">' + esc(tagText(f, x)) + '</span><br><span class="small">' + esc(f.opts[ANS[f.id]][0]) + ".</span> " + esc(f.helps) + "</li>";
      }).join("") + "</ul>";
      var open = F.filter(function (f) { return ANS[f.id] == null; });
      if (open.length) h += '<p class="small">' + open.length + " still unanswered: " + open.map(function (f) { return '<a href="#d-' + f.id + '">' + esc(f.name) + "</a>"; }).join(", ") + ".</p>";
    }
    out.innerHTML = h;
    var ql = questionList(), nprio = 0, ntot = 0;
    ql.forEach(function (g) { g.qs.forEach(function (x) { ntot++; if (x.prio) nprio++; }); });
    $("#drivers-qsum").innerHTML = "Questions to ask, by who answers them (" + ntot + ")" + (nprio ? ' · <span class="prio-n">' + nprio + " priority</span>" : "");
    $("#drivers-qs").innerHTML = ql.map(function (g) {
      return "<div><h5>" + esc(g.aud[1]) + "</h5><ul>" + g.qs.map(function (x) {
        return "<li" + (x.prio ? ' class="is-prio"' : "") + ">" + (x.prio ? '<span class="prio">Priority</span>' : "") + esc(x.q) + ' <span class="qf">' + esc(x.f.name) + "</span></li>";
      }).join("") + "</ul></div>";
    }).join("");
  }
  function onDriver(t) {
    var id = t.name.slice(2);
    ANS[id] = +t.value;
    paintDriver(id); renderSummary();
    ga("crm_driver", { event_label: id + ":" + t.value });
  }
  function applyCaps() {
    var caps = prioCaps();
    $$('#ats-filters input[name="must"]').forEach(function (i) { i.checked = caps.indexOf(i.value) >= 0; });
    render();
    var f = document.getElementById("finder"); if (f && f.scrollIntoView) f.scrollIntoView();
    ga("crm_apply_caps", { event_label: caps.join(",") });
  }
  function copyQuestions() {
    var txt = "Questions to ask before buying a recruiting CRM\nFrom The Signal HR: https://thesignalhr.com/compare/crm/#need\n";
    questionList().forEach(function (g) {
      txt += "\n" + g.aud[1].toUpperCase() + "\n" + g.qs.map(function (x) { return "- " + (x.prio ? "[Priority] " : "") + x.q; }).join("\n") + "\n";
    });
    var note = $("#drivers-copied");
    var done = function (ok) { note.textContent = ok ? "Copied. Paste it into an email or your RFP." : "Couldn't copy here. Select the list and copy it instead."; };
    var fallback = function () {
      try {
        var ta = document.createElement("textarea");
        ta.value = txt; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        var ok = document.execCommand("copy"); document.body.removeChild(ta); done(ok);
      } catch (err) { done(false); }
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(function () { done(true); }, fallback);
      else fallback();
    } catch (err) { fallback(); }
    ga("crm_copy_questions", { value: Object.keys(ANS).length });
  }
  function resetDrivers() {
    ANS = {};
    $$('#drivers input[type="radio"]').forEach(function (i) { i.checked = false; });
    F.forEach(function (f) { paintDriver(f.id); });
    $$("#drivers details.dhelp").forEach(function (d) { d.open = false; });
    $("#drivers-copied").textContent = "";
    renderSummary();
  }

  // ---------- Events ----------
  document.addEventListener("change", function (e) {
    var t = e.target;
    if (t.matches("input[data-cmp]")) toggle(t.getAttribute("data-cmp"), t.checked);
    else if (t.name && t.name.indexOf("f-") === 0) onDriver(t);
    else if (t.closest && t.closest("#ats-filters")) { render(); ga("crm_filter", { event_label: t.name + ":" + t.value }); }
  });
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-open]");
    if (a) { var d = document.getElementById("p-" + a.getAttribute("data-open")); if (d) d.open = true; }
    if (e.target.id === "ats-clear") { selected = []; syncChecks(); renderCompare(); }
    if (e.target.id === "drivers-copy") copyQuestions();
    if (e.target.id === "drivers-reset") resetDrivers();
    if (e.target.id === "drivers-apply") applyCaps();
    if (e.target.id === "ats-expand") {
      e.preventDefault();
      var all = $$("details.profile"), open = all.some(function (d) { return !d.open; });
      all.forEach(function (d) { d.open = open; });
      e.target.textContent = open ? "Collapse all" : "Expand all";
    }
  });
  if (location.hash && location.hash.indexOf("#p-") === 0) { var d = document.querySelector(location.hash); if (d) d.open = true; }
  render(); renderCompare(); renderSummary();
})();
