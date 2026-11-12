/* Apply the saved theme before painting, authorized by its exact CSP hash. */
try {
  document.documentElement.dataset.theme =
    localStorage.getItem("virtus-optio-theme") === "dark" ? "dark" : "light";
} catch (_) {
  document.documentElement.dataset.theme = "light";
}

// Reserve the mobile navigation layout before the deferred controls load.
document.documentElement.classList.add("js");
