/* Offer email choices while retaining the footer's normal mailto fallback. */
(() => {
  "use strict";

  const dialog = document.getElementById("email-contact-dialog");
  if (!dialog || typeof dialog.showModal !== "function") return;

  const email = "virtusoptio@gmail.com";
  const heading = dialog.querySelector("h2");
  const feedback = dialog.querySelector("[data-email-feedback]");
  const fallback = dialog.querySelector("[data-email-copy-fallback]");
  const address = fallback.querySelector("input");
  let opener;

  document.querySelectorAll("[data-email-contact]").forEach((link) => {
    link.setAttribute("aria-haspopup", "dialog");
    link.setAttribute("aria-controls", dialog.id);
    link.addEventListener("click", (event) => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      feedback.textContent = "";
      fallback.hidden = true;
      dialog.showModal();
      document.documentElement.classList.add("email-dialog-open");
      heading.focus();
    });
  });

  dialog.querySelector("[data-email-close]").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener("close", () => {
    document.documentElement.classList.remove("email-dialog-open");
    if (opener?.isConnected) opener.focus();
  });

  dialog.querySelector("[data-copy-email]").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(email);
      feedback.textContent = "Email address copied.";
      fallback.hidden = true;
    } catch (_) {
      feedback.textContent = "Automatic copying is unavailable in this browser.";
      fallback.hidden = false;
      address.focus();
      address.select();
    }
  });
})();
