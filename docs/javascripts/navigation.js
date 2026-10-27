/* Give small screens room to read, with the menu returning on upward scroll. */
(() => {
  "use strict";
  const header = document.querySelector(".site-header");
  if (!header) return;
  const mobile = window.matchMedia("(max-width: 640px)");
  let previousY = window.scrollY;
  let direction = 0;
  let distance = 0;
  let scheduled = false;

  function reveal() {
    header.classList.remove("is-scroll-hidden");
    previousY = window.scrollY;
    direction = 0;
    distance = 0;
  }

  function update() {
    scheduled = false;
    // Clamp Safari's elastic overscroll so a bounce cannot hide the menu.
    const bottom = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    const y = Math.max(0, Math.min(window.scrollY, bottom));
    const delta = y - previousY;
    previousY = y;
    if (!mobile.matches || y < 160 || header.querySelector(":focus-visible")) {
      reveal();
      return;
    }
    if (!delta) return;
    const nextDirection = Math.sign(delta);
    distance = nextDirection === direction ? distance + Math.abs(delta) : Math.abs(delta);
    direction = nextDirection;
    if (distance >= (direction > 0 ? 18 : 8)) {
      header.classList.toggle("is-scroll-hidden", direction > 0);
    }
  }

  window.addEventListener("scroll", () => {
    if (!scheduled) {
      scheduled = true;
      window.requestAnimationFrame(update);
    }
  }, { passive: true });
  header.addEventListener("focusin", reveal);
  mobile.addEventListener("change", reveal);
  window.addEventListener("pageshow", reveal);
})();
