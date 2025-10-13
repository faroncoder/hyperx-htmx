// hyperx-events.js
(() => {
  console.log("⚡ HyperX Events Initialized");

  const HX_SESSION_PAIR = window.HX_PAIR || null;

  function verifyPair(el) {
    const pair = el.getAttribute("hx-pair");
    if (!pair || pair !== HX_SESSION_PAIR) {
      console.warn("❌ HX Pair verification failed", { pair, expected: HX_SESSION_PAIR });
      return false;
    }
    return true;
  }

  function handleHxFetch(el) {
    if (!verifyPair(el)) return; // 🔒 kill unverified hxjs
    const url = el.getAttribute("hx-url");
    const method = el.getAttribute("hx-method") || "GET";
    const thenSel = el.getAttribute("hx-then");
    const action = el.getAttribute("hx-action") || "render";

    if (!url) return;

    fetch(url, { method })
      .then(r => r.text())
      .then(html => {
        if (action === "render" && thenSel) {
          const tgt = document.querySelector(thenSel);
          if (tgt) tgt.innerHTML = html;
        }
      })
      .catch(err => console.error("HX Fetch error:", err));
  }

  function attachHxEvents() {
    document.querySelectorAll("[hx-on]").forEach(el => {
      const evt = el.getAttribute("hx-on") || "click";
      el.addEventListener(evt, e => handleHxFetch(el));
    });
  }

  attachHxEvents();

  // Observe DOM for new HX elements
  const observer = new MutationObserver(attachHxEvents);
  observer.observe(document.body, { childList: true, subtree: true });

})();
