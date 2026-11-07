(function () {
  // The nav "Subscribe free" button scrolls to this page's signup form; submitting counts an event (never the address).
  var send = function (name, p) { if (typeof gtag === "function") gtag("event", name, p); };
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a.nav-cta");
    var form = document.querySelector("form.signal-sub");
    if (!a || !form) return;
    e.preventDefault();
    e.stopPropagation();
    form.scrollIntoView({ behavior: "smooth", block: "center" });
    form.classList.add("sub-flash");
    setTimeout(function () { form.classList.remove("sub-flash"); }, 1800);
    var input = form.querySelector("input[type=email]");
    if (input) setTimeout(function () { input.focus({ preventScroll: true }); }, 450);
    send("subscribe_cta", { placement: "nav", page_path: location.pathname });
  }, true);
  document.addEventListener("submit", function (e) {
    var f = e.target;
    if (f && f.classList && f.classList.contains("signal-sub")) send("subscribe_submit", { placement: f.getAttribute("data-placement") || "page", page_path: location.pathname });
  });
})();
