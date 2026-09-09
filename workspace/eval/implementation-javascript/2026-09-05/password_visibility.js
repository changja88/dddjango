(() => {
  const selector = "[data-password-visibility]";
  function activate(scope) {
    const roots = new Set(scope.querySelectorAll(selector));
    const owner = scope instanceof Element ? scope.closest(selector) : null;
    if (owner) roots.add(owner);
    for (const root of roots) {
      const input = root.querySelector("[data-password-input]");
      const button = root.querySelector("[data-password-toggle]");
      if (!input || !button) continue;
      button.setAttribute("aria-pressed", String(input.type === "text"));
      button.hidden = false;
    }
  }
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-password-toggle]");
    const root = button?.closest(selector);
    const input = root?.querySelector("[data-password-input]");
    if (!input) return;
    const visible = input.type === "password";
    input.type = visible ? "text" : "password";
    button.setAttribute("aria-pressed", String(visible));
  });
  document.addEventListener("htmx:load", (event) => activate(event.detail.elt));
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => activate(document), { once: true });
  } else {
    activate(document);
  }
})();
