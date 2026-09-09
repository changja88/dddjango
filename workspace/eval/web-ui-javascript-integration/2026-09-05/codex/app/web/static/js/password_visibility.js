(() => {
  const selector = "[data-password-visibility]";

  function controls(root) {
    const input = root.querySelector("[data-password-input]");
    const button = root.querySelector("[data-password-toggle]");
    const status = root.querySelector("[data-password-status]");
    if (!input || !button || !status) return null;
    if (![input, button, status].every((node) => node.closest(selector) === root)) return null;
    return { input, button, status };
  }

  function synchronize(current) {
    const visible = current.input.type === "text";
    current.button.setAttribute("aria-pressed", String(visible));
    current.status.textContent = visible
      ? "Password visible. Activate to conceal."
      : "Password hidden. Activate to show.";
    current.button.hidden = false;
  }

  function activate(scope) {
    const roots = new Set(scope.querySelectorAll(selector));
    const owner = scope instanceof Element ? scope.closest(selector) : null;
    if (owner) roots.add(owner);
    for (const root of roots) {
      const current = controls(root);
      if (current) synchronize(current);
    }
  }

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-password-toggle]");
    const root = button?.closest(selector);
    if (!root) return;
    const current = controls(root);
    if (!current || current.button !== button) return;
    current.input.type = current.input.type === "password" ? "text" : "password";
    synchronize(current);
  });
  document.addEventListener("htmx:load", (event) => activate(event.detail.elt));
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => activate(document), { once: true });
  } else {
    activate(document);
  }
})();
