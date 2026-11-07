(function () {
  // Page feedback: a Yes/No usefulness count (analytics, only if the cookie choice allows it; no text, nothing identifying)
  // and an email link with the page filled in. Added to every page with a <main>, after its content.
  var main = document.querySelector("main");
  if (!main || document.querySelector(".page-feedback") || location.pathname === "/404.html") return;
  var title = (document.title || "").replace(/\s+—\s+The Signal HR$/, "");
  var subject = "Feedback: " + title;
  var body = "Page: " + location.href.split("#")[0] + "\n\nWhat should change, and a source if you have one:\n\n";
  var mail = "mailto:alex@thesignalhr.com?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  var box = document.createElement("section");
  box.className = "page-feedback";
  box.setAttribute("aria-label", "Page feedback");
  box.innerHTML = '<div class="wrap"><div class="pf-row">' +
    '<span class="pf-q">Was this page useful?</span>' +
    '<button type="button" data-v="yes">Yes</button><button type="button" data-v="no">No</button>' +
    '<span class="pf-thanks" aria-live="polite"></span>' +
    '<a class="pf-mail" href="' + mail + '">Suggest a fix or add context →</a></div></div>';
  var band = main.querySelector(".news-band, .fp-close");
  var anchor = band ? band.closest("section") : null;
  if (anchor && anchor.parentNode === main) main.insertBefore(box, anchor); else main.appendChild(box);
  box.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-v]");
    if (!b) return;
    box.querySelectorAll("button[data-v]").forEach(function (x) { x.disabled = true; x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    box.querySelector(".pf-thanks").textContent = b.getAttribute("data-v") === "yes" ? "Thanks." : "Thanks. What would make it better?";
    if (typeof gtag === "function") gtag("event", "page_useful", { value: b.getAttribute("data-v"), page_path: location.pathname });
  });
  box.querySelector(".pf-mail").addEventListener("click", function () {
    if (typeof gtag === "function") gtag("event", "feedback_email", { page_path: location.pathname });
  });
})();
