/* Give small screens room to read, with the menu returning on upward scroll. */
(() => {
  "use strict";
  const header = document.querySelector(".site-header");
  if (!header) return;
  const mobile = window.matchMedia("(max-width: 640px)");
  const menuToggle = header.querySelector("[data-menu-toggle]");
  const menu = header.querySelector(".header-menu");
  const themeToggle = header.querySelector(".theme-toggle");
  let previousY = null;
  let latestY = 0;
  let documentHeight = Infinity;
  let viewportHeight = 0;
  let direction = 0;
  let distance = 0;
  let scheduled = false;

  function clampScroll(y) {
    return Math.max(0, Math.min(y, Math.max(0, documentHeight - viewportHeight)));
  }

  // ResizeObserver runs after layout. Cache these dimensions instead of forcing
  // layout during initialization or reading scrollHeight on every scroll frame.
  if (typeof ResizeObserver !== "undefined") {
    const boundsObserver = new ResizeObserver(() => {
      documentHeight = document.documentElement.scrollHeight;
      viewportHeight = window.innerHeight;
      latestY = clampScroll(window.scrollY);
      previousY = previousY === null ? latestY : clampScroll(previousY);
    });
    boundsObserver.observe(document.documentElement);
  }
  window.addEventListener("resize", () => { viewportHeight = window.innerHeight; }, { passive: true });

  function reveal(y = null) {
    header.classList.remove("is-scroll-hidden");
    previousY = y;
    direction = 0;
    distance = 0;
  }

  function setMenuOpen(open, restoreFocus = false) {
    if (!menuToggle || !menu) return;
    // Do not leave keyboard focus in content that is about to be hidden.
    if (!open && mobile.matches && menu.contains(document.activeElement)) {
      if (restoreFocus) menuToggle.focus();
      else document.activeElement.blur();
    } else if (!open && restoreFocus) {
      menuToggle.focus();
    }
    header.classList.toggle("is-menu-open", open);
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    reveal();
  }

  function syncMenuOrder() {
    if (!menu || !themeToggle) return;
    const actions = menu.parentElement;
    const focused = document.activeElement;
    // Keep reading/tab order aligned with the responsive visual order, using
    // the same links rather than separate mobile and desktop controls.
    if (mobile.matches) {
      if (actions.lastElementChild !== menu) actions.appendChild(menu);
    } else if (menu.nextElementSibling !== themeToggle) {
      actions.insertBefore(menu, themeToggle);
    }
    if (menu.contains(focused) && document.activeElement !== focused) {
      focused.focus({ preventScroll: true });
    }
  }

  if (menuToggle && menu) {
    syncMenuOrder();
    menuToggle.hidden = false;
    header.classList.add("menu-ready");
    setMenuOpen(false);
    menuToggle.addEventListener("click", () => {
      setMenuOpen(!header.classList.contains("is-menu-open"));
    });
    header.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && header.classList.contains("is-menu-open")) {
        event.preventDefault();
        setMenuOpen(false, true);
      }
    });
    document.addEventListener("click", (event) => {
      if (header.classList.contains("is-menu-open") && !header.contains(event.target)) {
        setMenuOpen(false);
      }
    });
    menu.addEventListener("click", (event) => {
      if (event.target.closest("a[href]")) setMenuOpen(false);
    });
    header.addEventListener("focusout", (event) => {
      // The next focused control is known here; activeElement can briefly be body.
      // Null destinations are handled by outside clicks instead of hiding a link
      // before its pending click can navigate.
      if (header.classList.contains("is-menu-open") && event.relatedTarget && !header.contains(event.relatedTarget)) {
        setMenuOpen(false);
      }
    });
  }

  function update() {
    scheduled = false;
    // Clamp Safari's elastic overscroll so a bounce cannot hide the menu.
    const y = clampScroll(latestY);
    const delta = previousY === null ? 0 : y - previousY;
    previousY = y;
    if (!mobile.matches || y < 160 || header.classList.contains("is-menu-open") || header.querySelector(":focus-visible")) {
      reveal(y);
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
    // Scroll events arrive after layout; collect reads before the frame's writes.
    latestY = clampScroll(window.scrollY);
    if (!scheduled) {
      scheduled = true;
      window.requestAnimationFrame(update);
    }
  }, { passive: true });
  header.addEventListener("focusin", () => reveal());
  function reset() {
    setMenuOpen(false, mobile.matches && menu?.contains(document.activeElement));
    syncMenuOrder();
    if (!mobile.matches && document.activeElement === menuToggle) {
      menu.querySelector("a[href]")?.focus({ preventScroll: true });
    }
    reveal();
  }
  mobile.addEventListener("change", reset);
  window.addEventListener("pageshow", reset);
})();
