(function () {
  var D = JSON.parse(document.getElementById("ats-data").textContent);
  var P = D.p, byId = {};
  P.forEach(function (p) { byId[p.id] = p; });
  var CAPN = {}; D.caps.forEach(function (c) { CAPN[c[0]] = c[1]; });
  var OBLN = {}; D.obl.forEach(function (o) { OBLN[o[0]] = o[1]; });
  var USEN = {}; D.uses.forEach(function (u) { USEN[u[0]] = u[1]; });
  var JBY = {}; D.juris.forEach(function (j) { JBY[j.id] = j; });
  var selected = [];
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ga = function (name, params) { if (typeof gtag === "function") gtag("event", name, params); };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  var LV = { 2: "Documented", 1: "Partial", 0: "Not documented" };
  var AUDL = { 2: "Recent, public", 1: "Older or narrower", 0: "None found" };
  var CERTL = { 2: "Covers the product", 1: "Narrower scope", 0: "None found" };
  function lvLabel(k, v) { return k === "audit" ? AUDL[v] : k === "cert" ? CERTL[v] : LV[v]; }

  // ---------- Finder ----------
  function state() {
    var f = $("#ats-filters");
    var val = function (n) { var el = f.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : "any"; };
    var vals = function (n) { return $$('input[name="' + n + '"]:checked', f).map(function (i) { return i.value; }); };
    return { size: val("size"), ats: val("ats"), scores: vals("score"), musts: vals("must") };
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
    if (s.scores.length) {
      var hit = s.scores.filter(function (m) { return p.scores.indexOf(m) >= 0; });
      if (!hit.length) return { out: "Scores " + p.scores.map(function (m) { return D.scn[m].toLowerCase(); }).join(", ") + " only" };
      hit.forEach(function (m) { why.push("Scores " + D.scn[m].toLowerCase()); score += 2; });
      s.scores.filter(function (m) { return p.scores.indexOf(m) < 0; }).forEach(function (m) { gaps.push("Doesn't score " + D.scn[m].toLowerCase()); score -= 1; });
    }
    s.musts.forEach(function (k) {
      var v = p.caps[k];
      if (k === "audit") {
        if (v === 2) { why.push("Recent public bias audit"); score += 2; }
        else if (v === 1) { why.push("Older or narrower bias audit"); score += 1; }
        else gaps.push("No published bias audit");
      } else if (k === "cert") {
        if (v === 2) { why.push("AI certification"); score += 2; }
        else if (v === 1) { why.push("AI certification, narrower scope"); score += 1; }
        else gaps.push("No AI certification found");
      } else {
        if (v === 2) { why.push(CAPN[k]); score += 2; }
        else if (v === 1) { why.push(CAPN[k] + " (partial)"); score += 1; }
        else gaps.push(CAPN[k] + ": not documented");
      }
    });
    return { why: why, gaps: gaps, score: score };
  }
  function card(p, r) {
    return '<article class="fit-card' + (r.gaps.length ? " partial" : "") + '">' +
      '<div class="top"><span class="tag tag-signal">' + esc(D.cats[p.cat]) + '</span><h4>' + esc(p.name) + '</h4><div class="owner">' + esc(p.owner) + "</div></div>" +
      "<p>" + esc(p.best) + "</p>" +
      (r.why.length ? '<ul class="why">' + r.why.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + "</ul>" : "") +
      (r.gaps.length ? '<ul class="gaps">' + r.gaps.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("") + "</ul>" : "") +
      '<div class="shows"><b>Recruiters see:</b> ' + esc(p.output) + "</div>" +
      '<div class="works">' + esc(p.works) + "</div>" +
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
    h += row("Owner", function (p) { return esc(p.owner); });
    h += row("Best for", function (p) { return esc(p.best); });
    h += row("Not for", function (p) { return esc(p.notfor); });
    h += row("ATS", function (p) { return esc(p.works); });
    h += row("Scores", function (p) { return esc(p.scores.map(function (m) { return D.scn[m]; }).join(", ")); });
    h += grp("How the score works");
    h += row("What recruiters see", function (p) { return esc(p.output); });
    h += row("How it's set", function (p) { return esc(p.how); });
    h += row("Automatic actions", function (p) { return esc(p.auto); });
    h += grp("Governance");
    D.caps.forEach(function (c) { h += row(esc(c[1]), function (p) { var v = p.caps[c[0]]; return '<span class="lv lv-' + v + '"></span>' + lvLabel(c[0], v); }); });
    h += row("Evidence", function (p) { return esc(p.gov); });
    h += grp("Cost and due diligence");
    h += row("How it's priced", function (p) { return esc(p.pricing); });
    h += row("Strengths", function (p) { return list(p.strengths); });
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
    ga("match_compare_toggle", { event_label: id, value: selected.length });
  }

  // ---------- Step 1: the rules where you hire (orientation, not legal advice) ----------
  var USES_ORDER = ["rank", "filter", "auto"];
  function rulesState() {
    var f = $("#rules-form");
    var u = f.querySelector('input[name="use"]:checked');
    return { jur: $$('input[name="jur"]:checked', f).map(function (i) { return i.value; }), use: u ? u.value : "rank" };
  }
  // notes that apply at the chosen use and every lower-risk use above "rank"
  function heightened(j, use) {
    var n = [], upto = USES_ORDER.indexOf(use);
    USES_ORDER.forEach(function (u, i) { if (i > 0 && i <= upto && j.heightened[u]) n.push(j.heightened[u]); });
    return n;
  }
  function useVerdict(use, js) {
    var hot = js.filter(function (j) { return heightened(j, use).length; });
    var where = hot.length ? " Extra weight in " + hot.map(function (j) { return j.name; }).join(", ") + "." : "";
    if (use === "auto") return { cls: "v-gaps", t: "Automatic rejection or advancement carries the most obligations", d: "Where a score acts without a person, rules add rights to an explanation, a human review or a refusal." + where + " Most platforms here say their score doesn't reject anyone on its own, but workflows and automations can act on it: map every automatic step before go-live." };
    if (use === "filter") return { cls: "v-gaps", t: "Filtering on a score makes it part of the decision", d: "Hiding or prioritizing candidates by score is what most rules mean by a score that 'substantially assists' or 'materially influences' a decision." + where + " Plan notice, testing and a person who reviews below the line." };
    return { cls: "v-buy", t: "Ranking is the lowest-risk use, not a no-risk one", d: "Several rules apply whenever AI is used to screen, assess or rank applicants, even when recruiters review everyone. Notice and testing are the usual starting points." };
  }
  function prioCaps(s, js) {
    var caps = [];
    var add = function (c) { if (caps.indexOf(c) < 0) caps.push(c); };
    js.forEach(function (j) { j.must.forEach(function (m) { (D.oblcaps[m[0]] || []).forEach(add); }); });
    (D.usecaps[s.use] || []).forEach(add);
    if (js.length > 1) add("switch");
    return D.caps.map(function (c) { return c[0]; }).filter(function (c) { return caps.indexOf(c) >= 0; });
  }
  function oblCounts(js) {
    var n = {};
    js.forEach(function (j) { var seen = {}; j.must.forEach(function (m) { if (!seen[m[0]]) { seen[m[0]] = 1; n[m[0]] = (n[m[0]] || 0) + 1; } }); });
    return D.obl.filter(function (o) { return n[o[0]]; }).map(function (o) { return [o[0], o[1], n[o[0]]]; }).sort(function (a, b) { return b[2] - a[2]; });
  }
  function renderRules() {
    var s = rulesState(), outEl = $("#rules-out");
    var js = D.juris.filter(function (j) { return s.jur.indexOf(j.id) >= 0; });
    $("#rules-actions").hidden = !js.length;
    if (!js.length) { outEl.innerHTML = '<p class="sum-line">Pick at least one place you hire.</p>'; return; }
    var v = useVerdict(s.use, js), counts = oblCounts(js), caps = prioCaps(s, js);
    var h = '<div class="verdict ' + v.cls + '"><h4>' + esc(v.t) + "</h4><p>" + esc(v.d) + "</p></div>";
    h += '<div class="obl-sum"><span>Across ' + js.length + " " + (js.length === 1 ? "place" : "places") + ":</span>" + counts.map(function (c) { return '<span class="obl o-' + c[0] + '">' + esc(c[1]) + " <b>" + c[2] + "</b></span>"; }).join("") + "</div>";
    if (caps.length) h += '<div class="prio-caps"><span>Capabilities to insist on:</span>' + caps.map(function (c) { return '<span class="cap">' + esc(CAPN[c]) + "</span>"; }).join("") + '<button type="button" class="btn btn-ghost" id="rules-apply">Apply to the finder</button></div>';
    h += '<div class="jcards">' + js.map(function (j) {
      var hn = heightened(j, s.use);
      return '<article class="jcard">' +
        '<div class="jtop"><h4>' + esc(j.name) + '</h4><span class="region-tag">' + esc(D.regn[j.region]) + "</span></div>" +
        '<p class="jlaw">' + esc(j.law) + '</p><p class="jstatus">' + esc(j.status) + "</p>" +
        '<p class="jwhen"><b>Applies when:</b> ' + esc(j.when) + "</p>" +
        '<ul class="jmust">' + j.must.map(function (m) { return '<li><span class="obl o-' + m[0] + '">' + esc(OBLN[m[0]]) + "</span> " + esc(m[1]) + "</li>"; }).join("") + "</ul>" +
        hn.map(function (t) { return '<p class="jhot"><b>For how you\'ll use it:</b> ' + esc(t) + "</p>"; }).join("") +
        '<p class="src">Source: <a href="' + esc(j.src[1]) + '" target="_blank" rel="noopener">' + esc(j.src[0]) + "</a></p></article>";
    }).join("") + "</div>";
    h += '<h4 class="sum-qh">Ask your vendor</h4><ul class="sum-plat">' + counts.map(function (c) { return "<li><b>" + esc(c[1]) + ".</b> " + esc(D.oblask[c[0]]) + "</li>"; }).join("") + "</ul>";
    outEl.innerHTML = h;
  }
  function checklist() {
    var s = rulesState();
    var js = D.juris.filter(function (j) { return s.jur.indexOf(j.id) >= 0; });
    var txt = "Before we switch on an applicant match score: rules where we hire\nFrom The Signal HR (reviewed " + D.verified + "): https://thesignalhr.com/compare/match/#rules\nOrientation, not legal advice. Confirm with counsel.\n\nHow we'll use the score: " + USEN[s.use] + "\n";
    js.forEach(function (j) {
      txt += "\n" + j.name.toUpperCase() + " (" + j.law + "; " + j.status + ")\nApplies when: " + j.when + "\n";
      j.must.forEach(function (m) { txt += "[ ] " + OBLN[m[0]] + ": " + m[1] + "\n"; });
      heightened(j, s.use).forEach(function (t) { txt += "! " + t + "\n"; });
      txt += "Source: " + j.src[1] + "\n";
    });
    txt += "\nASK THE VENDOR\n" + oblCounts(js).map(function (c) { return "- " + D.oblask[c[0]]; }).join("\n") + "\n";
    return txt;
  }
  function copyChecklist() {
    var txt = checklist(), note = $("#rules-copied");
    var done = function (ok) { note.textContent = ok ? "Copied. Paste it into an email or your rollout plan." : "Couldn't copy here. Select the text and copy it instead."; };
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
    ga("match_copy_checklist", { value: rulesState().jur.length });
  }
  function applyCaps() {
    var s = rulesState(), js = D.juris.filter(function (j) { return s.jur.indexOf(j.id) >= 0; }), caps = prioCaps(s, js);
    $$('#ats-filters input[name="must"]').forEach(function (i) { i.checked = caps.indexOf(i.value) >= 0; });
    render();
    var f = document.getElementById("finder"); if (f && f.scrollIntoView) f.scrollIntoView();
    ga("match_apply_caps", { event_label: caps.join(",") });
  }
  function selectRegion(reg) {
    var boxes = D.juris.filter(function (j) { return j.region === reg; }).map(function (j) { return $('#rules-form input[name="jur"][value="' + j.id + '"]'); });
    var all = boxes.every(function (b) { return b.checked; });
    boxes.forEach(function (b) { b.checked = !all; });
    syncRegionButtons(); renderRules();
    ga("match_rules", { event_label: (all ? "clear:" : "all:") + reg });
  }
  function syncRegionButtons() {
    $$("#rules-form [data-all]").forEach(function (btn) {
      var reg = btn.getAttribute("data-all");
      var js = D.juris.filter(function (j) { return j.region === reg; });
      var all = js.every(function (j) { return $('#rules-form input[name="jur"][value="' + j.id + '"]').checked; });
      btn.textContent = all ? "Clear" : "Select all " + js.length;
    });
  }
  function resetRules() {
    $$('#rules-form input[name="jur"]').forEach(function (i) { i.checked = false; });
    var r = $('#rules-form input[name="use"][value="rank"]'); if (r) r.checked = true;
    $("#rules-copied").textContent = "";
    syncRegionButtons(); renderRules();
  }

  // ---------- Events ----------
  document.addEventListener("change", function (e) {
    var t = e.target;
    if (t.matches("input[data-cmp]")) toggle(t.getAttribute("data-cmp"), t.checked);
    else if (t.closest && t.closest("#rules-form")) { syncRegionButtons(); renderRules(); ga("match_rules", { event_label: t.name + ":" + t.value }); }
    else if (t.closest && t.closest("#ats-filters")) { render(); ga("match_filter", { event_label: t.name + ":" + t.value }); }
  });
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-open]");
    if (a) { var d = document.getElementById("p-" + a.getAttribute("data-open")); if (d) d.open = true; }
    var all = e.target.closest && e.target.closest("[data-all]");
    if (all) selectRegion(all.getAttribute("data-all"));
    if (e.target.id === "ats-clear") { selected = []; syncChecks(); renderCompare(); }
    if (e.target.id === "rules-copy") copyChecklist();
    if (e.target.id === "rules-reset") resetRules();
    if (e.target.id === "rules-apply") applyCaps();
    if (e.target.id === "ats-expand") {
      e.preventDefault();
      var ds = $$("details.profile"), open = ds.some(function (d) { return !d.open; });
      ds.forEach(function (d) { d.open = open; });
      e.target.textContent = open ? "Collapse all" : "Expand all";
    }
  });
  if (location.hash && location.hash.indexOf("#p-") === 0) { var d = document.querySelector(location.hash); if (d) d.open = true; }
  render(); renderCompare(); renderRules();
})();
