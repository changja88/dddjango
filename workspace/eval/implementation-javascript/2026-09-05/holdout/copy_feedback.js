(() => {
  "use strict";

  const rootSelector = "[data-copy-feedback]";
  const inputSelector = "[data-copy-text]";
  const statusSelector = "[data-copy-status]";
  const currentOperations = new WeakMap();

  async function copyText(root) {
    const input = root.querySelector(inputSelector);
    const status = root.querySelector(statusSelector);
    if (!(input instanceof HTMLInputElement) || !status) return;

    const operation = { input, status };
    currentOperations.set(root, operation);
    status.textContent = "";

    let message;
    try {
      await navigator.clipboard.writeText(input.value);
      message = "복사했습니다";
    } catch {
      message = "복사하지 못했습니다";
    }

    if (
      currentOperations.get(root) !== operation ||
      !root.isConnected ||
      root.querySelector(inputSelector) !== input ||
      root.querySelector(statusSelector) !== status
    ) {
      return;
    }

    status.textContent = message;
    currentOperations.delete(root);
  }

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-copy-button]");
    const root = button?.closest(rootSelector);
    if (!root) return;
    void copyText(root);
  });

  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    const removed = event.detail?.elt;
    if (!(removed instanceof Element)) return;

    const root = removed.closest(rootSelector);
    const operation = root && currentOperations.get(root);
    if (
      operation &&
      (removed === root ||
        removed.contains(operation.input) ||
        removed.contains(operation.status))
    ) {
      currentOperations.delete(root);
    }

    for (const descendantRoot of removed.querySelectorAll(rootSelector)) {
      currentOperations.delete(descendantRoot);
    }
  });
})();
