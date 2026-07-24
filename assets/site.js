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
        if (typeof gtag === "function") {
          gtag("event", "substack_cta_click", { event_category: "conversion", event_label: location.pathname });
        }
      });
    });
  });
})();
