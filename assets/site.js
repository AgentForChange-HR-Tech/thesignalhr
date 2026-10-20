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
