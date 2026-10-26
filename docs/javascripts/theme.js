/* Keep the reader's choice across pages, visits, and open tabs. */
(() => {
  "use strict";

  const storageKey = "virtus-optio-theme";
  const root = document.documentElement;
  const toggles = document.querySelectorAll("[data-theme-toggle]");

  function setTheme(theme, remember = false) {
    const dark = theme === "dark";
    root.dataset.theme = dark ? "dark" : "light";
    toggles.forEach((button) => {
      const label = dark ? "Switch to light theme" : "Switch to dark theme";
      button.setAttribute("aria-pressed", String(dark));
      button.setAttribute("aria-label", label);
      button.setAttribute("title", label);
    });

    if (remember) {
      try {
        localStorage.setItem(storageKey, root.dataset.theme);
      } catch (_) {
        // The switch still works when the browser blocks persistent storage.
      }
    }
  }

  setTheme(root.dataset.theme);
  toggles.forEach((button) => {
    button.addEventListener("click", () => {
      setTheme(root.dataset.theme === "dark" ? "light" : "dark", true);
    });
  });

  window.addEventListener("storage", (event) => {
    if (event.key === storageKey || event.key === null) {
      setTheme(event.newValue);
    }
  });
})();
