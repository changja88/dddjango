(() => {
  const ROOT_SELECTOR = "[data-image-preview]";
  const INPUT_SELECTOR = "[data-image-preview-input]";
  const CLEAR_SELECTOR = "[data-image-preview-clear]";
  const OUTPUT_SELECTOR = "[data-image-preview-output]";
  const NAME_SELECTOR = "[data-image-preview-name]";
  const EMPTY_SELECTOR = "[data-image-preview-empty]";
  const ERROR_SELECTOR = "[data-image-preview-error]";

  const previews = new WeakMap();

  function stateOf(root) {
    let state = previews.get(root);
    if (!state) {
      state = { objectUrl: "", generation: 0 };
      previews.set(root, state);
    }
    return state;
  }

  function releaseUrl(root) {
    const state = previews.get(root);
    if (!state || !state.objectUrl) return;
    URL.revokeObjectURL(state.objectUrl);
    state.objectUrl = "";
  }

  function clearOutput(root) {
    const output = root.querySelector(OUTPUT_SELECTOR);
    const name = root.querySelector(NAME_SELECTOR);
    const empty = root.querySelector(EMPTY_SELECTOR);
    const error = root.querySelector(ERROR_SELECTOR);
    if (output) {
      output.removeAttribute("src");
      output.hidden = true;
    }
    if (name) name.textContent = "";
    if (error) error.hidden = true;
    if (empty) empty.hidden = false;
  }

  function showError(root) {
    clearOutput(root);
    const empty = root.querySelector(EMPTY_SELECTOR);
    const error = root.querySelector(ERROR_SELECTOR);
    if (empty) empty.hidden = true;
    if (error) error.hidden = false;
  }

  function select(root, file) {
    const state = stateOf(root);
    releaseUrl(root);
    clearOutput(root);
    state.generation += 1;
    if (!file) return;
    const output = root.querySelector(OUTPUT_SELECTOR);
    if (!output) return;
    if (!file.type.startsWith("image/")) {
      showError(root);
      return;
    }
    const url = URL.createObjectURL(file);
    state.objectUrl = url;
    const name = root.querySelector(NAME_SELECTOR);
    const empty = root.querySelector(EMPTY_SELECTOR);
    if (name) name.textContent = file.name;
    if (empty) empty.hidden = true;
    output.dataset.imagePreviewGeneration = String(state.generation);
    output.src = url;
    output.hidden = false;
  }

  function isCurrentResult(root, output) {
    const state = previews.get(root);
    if (!state || !state.objectUrl) return false;
    if (output.getAttribute("src") !== state.objectUrl) return false;
    return output.dataset.imagePreviewGeneration === String(state.generation);
  }

  function cleanup(root) {
    releaseUrl(root);
    previews.delete(root);
  }

  function activate(scope) {
    const roots = new Set(scope.querySelectorAll(ROOT_SELECTOR));
    if (scope instanceof Element) {
      const owner = scope.closest(ROOT_SELECTOR);
      if (owner) roots.add(owner);
    }
    for (const root of roots) {
      const clear = root.querySelector(CLEAR_SELECTOR);
      if (clear) clear.hidden = false;
    }
  }

  document.addEventListener("change", (event) => {
    if (!(event.target instanceof Element)) return;
    const input = event.target.closest(INPUT_SELECTOR);
    if (!input) return;
    const root = input.closest(ROOT_SELECTOR);
    if (!root) return;
    select(root, input.files && input.files.length ? input.files[0] : null);
  });

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const clear = event.target.closest(CLEAR_SELECTOR);
    if (!clear) return;
    const root = clear.closest(ROOT_SELECTOR);
    if (!root) return;
    const input = root.querySelector(INPUT_SELECTOR);
    if (input) input.value = "";
    select(root, null);
  });

  document.addEventListener(
    "error",
    (event) => {
      if (!(event.target instanceof Element)) return;
      const output = event.target.closest(OUTPUT_SELECTOR);
      if (!output) return;
      const root = output.closest(ROOT_SELECTOR);
      if (!root || !isCurrentResult(root, output)) return;
      releaseUrl(root);
      showError(root);
    },
    true,
  );

  document.addEventListener(
    "load",
    (event) => {
      if (!(event.target instanceof Element)) return;
      const output = event.target.closest(OUTPUT_SELECTOR);
      if (!output) return;
      const root = output.closest(ROOT_SELECTOR);
      if (!root || !isCurrentResult(root, output)) return;
      const error = root.querySelector(ERROR_SELECTOR);
      if (error) error.hidden = true;
      output.hidden = false;
    },
    true,
  );

  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    const element = event.detail.elt;
    if (!(element instanceof Element)) return;
    if (element.matches(ROOT_SELECTOR)) cleanup(element);
    for (const root of element.querySelectorAll(ROOT_SELECTOR)) cleanup(root);
    const owner = element.closest(ROOT_SELECTOR);
    if (!owner || owner === element) return;
    if (element.matches(OUTPUT_SELECTOR) || element.querySelector(OUTPUT_SELECTOR)) {
      cleanup(owner);
    }
  });

  document.addEventListener("htmx:load", (event) => activate(event.detail.elt));

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => activate(document), { once: true });
  } else {
    activate(document);
  }
})();
