(function waitForLocalStorage() {
  function initTabMap() {
    // your lazy tab-map loader goes here
    (async function () {
      const CACHE_KEY = "hx_tab_map_v1";
      const CACHE_TTL = 3600 * 24 * 7; // 1 week

      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        try {
          const obj = JSON.parse(cached);
          const age = (Date.now() - obj.timestamp) / 1000;
          if (age < CACHE_TTL) {
            window._tabMap = obj.data;
            console.log("💾 tab-map from cache");
            return;
          }
        } catch (e) {}
      }

      try {
        const res = await fetch("/api/tabs/");
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        window._tabMap = data;
        localStorage.setItem(
          CACHE_KEY,
          JSON.stringify({ data, timestamp: Date.now() })
        );
        console.log("🌐 tab-map fetched & cached");
      } catch (err) {
        console.warn("Tab-map fetch failed:", err);
      }
    })();
  }

  // check every 100 ms until script signals ready
  if (window.localStorageReady || window.localStorage) {
    initTabMap();
  } else {
    setTimeout(waitForLocalStorage, 100);
  }
})();