/**
 * hyperx-events.js
 * ────────────────────────────────────────────────
 * Global event listeners for HyperX declarative system.
 * Handles dataset uploads, AI schema events, and UI feedback.
 */

document.addEventListener("DOMContentLoaded", () => {
  console.log("⚡ HyperX Events Initialized");

  // 🔹 React to dataset uploads
  document.body.addEventListener("dataset:uploaded", (e) => {
    const data = e.detail || {};
    console.log("📦 New dataset uploaded:", data.filename);

    // Refresh dataset dashboards if present
    const container = document.querySelector("#intel-container, #dataset-panel");
    if (container && window.htmx) {
      htmx.ajax("GET", "/lti/admin/course_table_view/", {
        target: container,
        swap: "innerHTML",
      });
    }

    // Bootstrap toast notification
    const toast = document.createElement("div");
    toast.className = "position-fixed top-0 end-0 p-3";
    toast.style.zIndex = 9999;
    toast.innerHTML = `
      <div class="toast align-items-center text-bg-success show border-0 shadow-lg" role="alert">
        <div class="d-flex">
          <div class="toast-body">
            ✅ Dataset <b>${data.filename}</b> uploaded successfully!
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
  });
});
