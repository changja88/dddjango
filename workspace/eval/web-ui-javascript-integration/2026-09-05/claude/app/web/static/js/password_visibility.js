(() => {
  const ROOT_SELECTOR = "[data-password-visibility]";
  const INPUT_SELECTOR = "[data-password-input]";
  const TOGGLE_SELECTOR = "[data-password-toggle]";

  function sync(root) {
    const input = root.querySelector(INPUT_SELECTOR);
    const button = root.querySelector(TOGGLE_SELECTOR);
    if (!input || !button) return;
    const visible = input.type === "text";
    button.setAttribute("aria-pressed", String(visible));
    button.textContent = visible
      ? button.dataset.passwordHideLabel
      : button.dataset.passwordShowLabel;
    button.hidden = false;
  }

  function activate(scope) {
    const roots = new Set(scope.querySelectorAll(ROOT_SELECTOR));
    if (scope instanceof Element) {
      const owner = scope.closest(ROOT_SELECTOR);
      if (owner) roots.add(owner);
    }
    for (const root of roots) sync(root);
  }

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest(TOGGLE_SELECTOR);
    if (!button) return;
    const root = button.closest(ROOT_SELECTOR);
    const input = root ? root.querySelector(INPUT_SELECTOR) : null;
    if (!input) return;
    input.type = input.type === "password" ? "text" : "password";
    sync(root);
  });

  document.addEventListener("htmx:load", (event) => activate(event.detail.elt));

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => activate(document), { once: true });
  } else {
    activate(document);
  }
})();
