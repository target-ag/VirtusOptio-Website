/* Footer popup and standalone settings share the same functional preference. */
(() => {
  "use strict";

  const key = "virtus-optio-theme";
  const panels = Array.from(document.querySelectorAll("[data-cookie-settings]"), (element) => ({
    output: element.querySelector("[data-saved-theme]"),
    feedback: element.querySelector("[data-cookie-feedback]"),
    button: element.querySelector("[data-clear-theme]"),
  }));

  function refresh() {
    panels.forEach(({ output, feedback, button }) => {
      try {
        const theme = localStorage.getItem(key);
        output.textContent = theme === "dark" ? "Dark" : theme === "light" ? "Light" : "No theme saved";
        button.disabled = false;
      } catch (_) {
        output.textContent = "Browser storage is unavailable";
        button.disabled = true;
        feedback.textContent = "Use your browser's site-data settings to manage stored preferences.";
      }
    });
  }

  panels.forEach(({ button, feedback }) => {
    button.hidden = false;
    button.addEventListener("click", () => {
      try {
        const hadPreference = localStorage.getItem(key) !== null;
        localStorage.removeItem(key);
        window.dispatchEvent(new CustomEvent("virtus-optio-theme-reset"));
        refresh();
        feedback.textContent = hadPreference
          ? "Saved theme cleared. Light mode is now active."
          : "No saved theme to clear. Light mode is active.";
      } catch (_) {
        feedback.textContent = "The browser could not clear this preference. Use its site-data settings instead.";
      }
    });
  });
  refresh();
  window.addEventListener("virtus-optio-theme-changed", () => {
    panels.forEach(({ feedback }) => { feedback.textContent = ""; });
    refresh();
  });

  const dialog = document.getElementById("cookie-dialog");
  if (!dialog || typeof dialog.showModal !== "function") return;
  let opener;
  document.querySelectorAll("[data-cookie-open]").forEach((link) => {
    link.setAttribute("aria-haspopup", "dialog");
    link.setAttribute("aria-controls", dialog.id);
    link.addEventListener("click", (event) => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      refresh();
      dialog.showModal();
      document.documentElement.classList.add("cookie-dialog-open");
    });
  });
  dialog.querySelectorAll("[data-cookie-close]").forEach((button) => {
    button.addEventListener("click", () => dialog.close());
  });
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener("close", () => {
    document.documentElement.classList.remove("cookie-dialog-open");
    if (opener?.isConnected) opener.focus();
  });
})();
