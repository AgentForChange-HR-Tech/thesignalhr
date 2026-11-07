(function () {
  // Cookie consent by location. Managed by _tools/site/consent.py: edit this file, then rerun it.
  var ID = "G-MGQ5MSQM2W", KEY = "signal-consent", DAY = 864e5;
  // Google consent mode: analytics cookies off by default where Google places the visitor's IP
  var OPTIN_REGIONS = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV",
    "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO", "GB", "CH", "BR", "CA-QC"];
  // The browser's time zone picks the default, on the device; nothing is sent. Unknown or UTC counts as opt-in.
  var OPTIN_TZ = new RegExp("^(Europe/|Arctic/|Brazil/|Etc/" +
    "|Atlantic/(Reykjavik|Canary|Madeira|Azores|Faroe|Faeroe)$" +
    "|Asia/(Nicosia|Famagusta)$|Africa/Ceuta$|Indian/(Reunion|Mayotte)$|Canada/Eastern$" +
    "|America/(Toronto|Montreal|Nipigon|Thunder_Bay|Blanc-Sablon|Guadeloupe|Martinique|Cayenne|Marigot|St_Barthelemy" +
    "|Sao_Paulo|Bahia|Fortaleza|Recife|Maceio|Belem|Araguaina|Santarem|Manaus|Boa_Vista|Porto_Velho|Rio_Branco" +
    "|Eirunepe|Cuiaba|Campo_Grande|Noronha)$" +
    "|(GB|GB-Eire|Eire|Iceland|Poland|Portugal|CET|EET|MET|WET|UTC|UCT|GMT|Universal|Zulu)$)");
  var tz = "";
  try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  var tier = (!tz || OPTIN_TZ.test(tz)) ? "optin" : "notice";
  var gpc = navigator.globalPrivacyControl === true || navigator.doNotTrack === "1" || window.doNotTrack === "1";

  function read() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || "null");
      var keep = v && (v.c === "denied" ? 182 : 365) * DAY;
      if (v && v.c && Date.now() - v.t < keep) return v.c;
    } catch (e) {}
    return "";
  }
  function save(c) { try { localStorage.setItem(KEY, JSON.stringify({ c: c, t: Date.now() })); } catch (e) {} }

  var choice = read(), loaded = false;
  var noop = function () {};
  var push = function () { window.dataLayer.push(arguments); };
  window.dataLayer = window.dataLayer || [];
  window.gtag = noop;                         // nothing is queued or sent until analytics may run

  function consent(a) {
    return { analytics_storage: a, ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" };
  }
  function load(granted) {
    window["ga-disable-" + ID] = false;
    window.gtag = push;
    if (loaded) { push("consent", "update", { analytics_storage: "granted" }); return; }
    loaded = true;
    if (!granted) { var r = consent("denied"); r.region = OPTIN_REGIONS; push("consent", "default", r); }
    push("consent", "default", consent("granted"));   // the region default above wins where it applies
    push("set", "ads_data_redaction", true);
    push("js", new Date());
    push("config", ID, { cookie_expires: 33696000, allow_google_signals: false, allow_ad_personalization_signals: false });
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
    document.head.appendChild(s);
  }
  function clearCookies() {
    var host = location.hostname, parts = host.split("."), doms = ["", host, "." + host];
    if (parts.length > 2) doms.push("." + parts.slice(-2).join("."));
    document.cookie.split(";").forEach(function (p) {
      var n = p.split("=")[0].trim();
      if (/^_ga/.test(n) || n === "_gid") {
        doms.forEach(function (d) { document.cookie = n + "=; Max-Age=0; path=/" + (d ? "; domain=" + d : ""); });
      }
    });
  }
  function allow() { choice = "granted"; save(choice); load(true); }
  function deny() {
    choice = "denied"; save(choice);
    if (loaded) push("consent", "update", { analytics_storage: "denied" });
    window["ga-disable-" + ID] = true;
    window.gtag = noop;
    clearCookies();
  }
  function on() { return choice === "granted" || (tier === "notice" && !gpc && choice !== "denied"); }

  if (choice === "granted") load(true);
  else if (on()) load(false);

  window.SignalConsent = {
    tier: tier, gpc: gpc, allow: allow, deny: deny, on: on,
    choice: function () { return choice; },
    needsBanner: function () { return !gpc && (choice === "" || (choice === "noticed" && tier === "optin")); },
    noticed: function () { if (tier === "notice" && choice === "") { choice = "noticed"; save(choice); } }
  };
})();
