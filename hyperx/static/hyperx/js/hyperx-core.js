/**
 * hyperx-core.js
 * Core runtime for HyperX declarative and TabX-powered HTMX integration.
 * No CSRF logic (handled by middleware automatically).
 */

document.addEventListener("DOMContentLoaded", () => {
  console.log("🧩 HyperX Core initialized");
  document.body.dispatchEvent(new CustomEvent("hyperx:ready"));

  // HTMX lifecycle diagnostics
  if (window.htmx) {
    htmx.on("htmx:beforeRequest", (evt) => {
      const headers = evt.detail.headers;
      if (window.HYPERX_DEBUG)
        console.debug("🔹 [HyperX] Before Request", evt.detail.path, headers);
    });

    htmx.on("htmx:afterSwap", (evt) => {
      if (window.HYPERX_DEBUG)
        console.debug("🔸 [HyperX] Swapped", evt.detail.target);
    });

    htmx.on("htmx:afterRequest", (evt) => {
      const dur = evt.detail.xhr.getResponseHeader("X-HyperX-Duration");
      if (dur) console.log(`⏱️ [HyperX] Roundtrip: ${dur}`);
    });

    htmx.on("htmx:responseError", (evt) => {
      console.warn("⚠️ [HyperX] HTMX error:", evt.detail.xhr.status, evt.detail.xhr.responseText);
    });
  }
});
