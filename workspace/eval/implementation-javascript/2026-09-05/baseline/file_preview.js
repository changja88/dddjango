(() => {
  "use strict";

  const rootSelector = "[data-file-preview]";
  const previewUrls = new WeakMap();

  function clearPreview(root) {
    const url = previewUrls.get(root);
    if (url) {
      URL.revokeObjectURL(url);
      previewUrls.delete(root);
    }

    const image = root.querySelector("[data-preview-image]");
    image.removeAttribute("src");
    image.hidden = true;
    root.querySelector("[data-preview-name]").textContent = "";
  }

  document.addEventListener("change", (event) => {
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || !input.matches("[data-preview-input]")) {
      return;
    }

    const root = input.closest(rootSelector);
    if (!root) return;

    const file = input.files[0];
    clearPreview(root);
    if (!file) return;

    const name = root.querySelector("[data-preview-name]");
    if (!file.type.startsWith("image/")) {
      input.value = "";
      name.textContent = "이미지 파일을 선택해 주세요.";
      return;
    }

    const url = URL.createObjectURL(file);
    previewUrls.set(root, url);
    const image = root.querySelector("[data-preview-image]");
    image.src = url;
    image.hidden = false;
    name.textContent = file.name;
  });

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-preview-clear]");
    const root = button?.closest(rootSelector);
    if (!root) return;

    root.querySelector("[data-preview-input]").value = "";
    clearPreview(root);
  });

  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    const element = event.detail.elt;
    if (!(element instanceof Element)) return;

    const root = element.closest(rootSelector);
    if (root && previewUrls.has(root)) clearPreview(root);
    for (const descendant of element.querySelectorAll(rootSelector)) {
      if (previewUrls.has(descendant)) clearPreview(descendant);
    }
  });
})();
