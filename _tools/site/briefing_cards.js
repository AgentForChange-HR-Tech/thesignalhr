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
