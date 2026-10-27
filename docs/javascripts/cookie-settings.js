/* Functional preferences and a notice acknowledgement, never tracking consent. */
(() => {
  "use strict";

  const key = "virtus-optio-theme";
  const noticeKey = "virtus-optio-cookie-notice";
  const noticeVersion = 1;
  const noticeLifetime = 180 * 24 * 60 * 60 * 1000;
  const notice = document.getElementById("cookie-notice");
  const dialog = document.getElementById("cookie-dialog");
  let focusNoticeAfterClose = false;
  let noticeReturnTarget;
  let opener;
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

  function hasCurrentAcknowledgement() {
    try {
      const saved = JSON.parse(localStorage.getItem(noticeKey));
      const age = saved && Date.now() - saved.acknowledgedAt;
      return !!saved && saved.version === noticeVersion && Number.isFinite(saved.acknowledgedAt)
        && age >= 0 && age < noticeLifetime;
    } catch (_) {
      return false;
    }
  }

  if (notice) {
    notice.hidden = hasCurrentAcknowledgement();
    notice.querySelector("[data-cookie-acknowledge]").addEventListener("click", (event) => {
      const restoreKeyboardFocus = event.detail === 0 && notice.contains(document.activeElement);
      try {
        localStorage.setItem(noticeKey, JSON.stringify({ version: noticeVersion, acknowledgedAt: Date.now() }));
      } catch (_) {
        // Dismiss this page's notice even when persistent storage is unavailable.
      }
      notice.hidden = true;
      if (restoreKeyboardFocus) {
        const target = noticeReturnTarget?.isConnected ? noticeReturnTarget : document.querySelector("a.wordmark");
        target?.focus({ preventScroll: true });
      }
    });
    document.querySelectorAll("[data-cookie-show-notice]").forEach((button) => {
      button.hidden = false;
      button.addEventListener("click", () => {
        noticeReturnTarget = dialog?.contains(button)
          ? (opener && !notice.contains(opener) ? opener : null)
          : button;
        try {
          localStorage.removeItem(noticeKey);
        } catch (_) {
          // The notice can still be shown without access to browser storage.
        }
        notice.hidden = false;
        if (dialog?.open) {
          focusNoticeAfterClose = true;
          dialog.close();
        } else {
          notice.querySelector("h2").focus();
        }
      });
    });
  }
  window.addEventListener("storage", (event) => {
    if (event.key === key || event.key === null) refresh();
    if (notice && (event.key === noticeKey || event.key === null)) notice.hidden = hasCurrentAcknowledgement();
  });

  if (!dialog || typeof dialog.showModal !== "function") return;
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
    if (focusNoticeAfterClose) {
      focusNoticeAfterClose = false;
      notice.querySelector("h2").focus();
    } else if (opener?.isConnected) opener.focus();
  });
})();
