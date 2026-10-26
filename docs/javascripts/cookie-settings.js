/* Manage only the functional theme preference; no tracking consent is collected. */
(() => {
  "use strict";

  const key = "virtus-optio-theme";
  const output = document.getElementById("saved-theme-status");
  const feedback = document.getElementById("cookie-settings-feedback");
  const button = document.querySelector("[data-clear-theme]");
  if (!output || !feedback || !button) return;

  function refresh() {
    try {
      const theme = localStorage.getItem(key);
      output.textContent = theme === "dark" ? "Dark" : theme === "light" ? "Light" : "No theme saved";
      button.disabled = theme === null;
    } catch (_) {
      output.textContent = "Browser storage is unavailable";
      button.disabled = true;
      feedback.textContent = "Use your browser's site-data settings to manage stored preferences.";
    }
  }

  button.hidden = false;
  refresh();
  button.addEventListener("click", () => {
    try {
      localStorage.removeItem(key);
      window.dispatchEvent(new CustomEvent("virtus-optio-theme-reset"));
      refresh();
      feedback.textContent = "Saved theme cleared. Light mode is now active.";
    } catch (_) {
      feedback.textContent = "The browser could not clear this preference. Use its site-data settings instead.";
    }
  });
  window.addEventListener("virtus-optio-theme-changed", () => {
    feedback.textContent = "";
    refresh();
  });
  window.addEventListener("storage", (event) => {
    if (event.key === key || event.key === null) refresh();
  });
})();
