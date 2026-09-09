(() => {
  "use strict";

  const rootSelector = "[data-file-preview]";
  const previews = new WeakMap();

  function clearPreview(root) {
    const preview = previews.get(root);
    if (preview) {
      previews.delete(root);
      URL.revokeObjectURL(preview.url);
    }

    const image = root.querySelector("[data-preview-image]");
    const name = root.querySelector("[data-preview-name]");
    if (image) {
      image.hidden = true;
      image.removeAttribute("src");
    }
    if (name) name.textContent = "";
  }

  function clearSelection(root) {
    const input = root.querySelector("[data-preview-input]");
    if (input) input.value = "";
    clearPreview(root);
  }

  document.addEventListener("change", (event) => {
    if (!(event.target instanceof Element)) return;
    const input = event.target.closest("[data-preview-input]");
    const root = input?.closest(rootSelector);
    if (!(input instanceof HTMLInputElement) || !root) return;

    const image = root.querySelector("[data-preview-image]");
    const name = root.querySelector("[data-preview-name]");
    const file = input.files?.[0];
    clearPreview(root);
    if (!image || !name || !file) return;

    if (!file.type.startsWith("image/")) {
      input.value = "";
      name.textContent = "이미지 파일을 선택해 주세요.";
      return;
    }

    let url;
    try {
      url = URL.createObjectURL(file);
    } catch {
      input.value = "";
      name.textContent = "이미지 미리보기를 만들 수 없습니다.";
      return;
    }

    previews.set(root, { input, image, url });
    name.textContent = file.name;
    image.src = url;
    image.hidden = false;
  });

  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-preview-clear]");
    const root = button?.closest(rootSelector);
    if (root) clearSelection(root);
  });

  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    const element = event.detail?.elt;
    if (!(element instanceof Element)) return;

    const owner = element.closest(rootSelector);
    const preview = owner && previews.get(owner);
    // 관련 없는 자식 제거는 유지 중인 미리보기를 끝내지 않는다.
    if (
      owner &&
      (element === owner ||
        (preview &&
          (element.contains(preview.input) || element.contains(preview.image))))
    ) {
      clearSelection(owner);
    }

    for (const root of element.querySelectorAll(rootSelector)) {
      clearSelection(root);
    }
  });
})();
