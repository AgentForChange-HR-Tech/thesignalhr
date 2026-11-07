(function () {
  var C = window.SignalConsent;
  if (!C) return;
  var box = null;
  function close() { if (box) { box.remove(); box = null; } }
  function show(fromSettings) {
    close();
    var optin = C.tier === "optin", on = C.on(), msg, yes, no;
    if (fromSettings) {
      msg = "Analytics is " + (on ? "on" : "off") +
        (!on && C.gpc && C.choice() !== "denied" ? ", because your browser sends a privacy signal (Global Privacy Control or Do Not Track)" : "") +
        ". We use Google Analytics cookies only to count visits and see which pages are useful. No ads, and we don't sell your information.";
      yes = "Allow analytics"; no = "No analytics";
    } else if (optin) {
      msg = "May we count your visit? We'd like to use Google Analytics cookies to see which pages are useful. No ads, and we don't sell your information. Analytics stays off unless you allow it.";
      yes = "Allow analytics"; no = "No thanks";
    } else {
      msg = "We use Google Analytics cookies to count visits and see which pages are useful. No ads, and we don't sell your information.";
      yes = "OK"; no = "Turn off analytics";
    }
    box = document.createElement("div");
    box.className = "consent";
    box.setAttribute("role", "region");
    box.setAttribute("aria-label", "Cookie choice");
    var p = document.createElement("p");
    p.textContent = msg + " ";
    var a = document.createElement("a");
    a.href = "/privacy/#cookies";
    a.textContent = "How this works";
    p.appendChild(a);
    var btns = document.createElement("div");
    btns.className = "consent-btns";
    [[yes, function () { C.allow(); }], [no, function () { C.deny(); }]].forEach(function (b) {
      var el = document.createElement("button");
      el.type = "button";
      el.textContent = b[0];
      el.addEventListener("click", function () { b[1](); close(); });
      btns.appendChild(el);
    });
    box.appendChild(p);
    box.appendChild(btns);
    document.body.appendChild(box);
    if (fromSettings) btns.firstChild.focus();
    else C.noticed();
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest && e.target.closest("[data-consent-open]");
    if (t) { e.preventDefault(); show(true); }
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && box && box.contains(document.activeElement)) close(); });
  function init() { if (C.needsBanner()) show(false); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
