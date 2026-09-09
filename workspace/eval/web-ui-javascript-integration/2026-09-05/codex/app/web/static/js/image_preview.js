(() => {
  const selector = "[data-image-preview]";
  const records = new WeakMap();

  function owners(scope) {
    const roots = new Set(scope.querySelectorAll(selector));
    const owner = scope instanceof Element ? scope.closest(selector) : null;
    if (owner) roots.add(owner);
    return roots;
  }

  function dependencies(root) {
    const body = root.querySelector("[data-image-preview-body]");
    if (!body) return null;
    const nodes = {
      body,
      input: body.querySelector("[data-image-input]"),
      image: body.querySelector("[data-image-output]"),
      filename: body.querySelector("[data-image-filename]"),
      status: body.querySelector("[data-image-status]"),
      clear: body.querySelector("[data-image-clear]"),
    };
    return Object.values(nodes).every((node) => node && node.closest(selector) === root)
      ? nodes : null;
  }

  function matches(record, nodes) {
    return nodes && Object.keys(nodes).every((key) => record.nodes[key] === nodes[key]);
  }

  function reset(record) {
    record.generation += 1;
    const url = record.url;
    record.url = null;
    record.nodes.image.removeAttribute("src");
    record.nodes.image.hidden = true;
    record.nodes.filename.textContent = "";
    record.nodes.status.textContent = "No image selected.";
    record.nodes.status.dataset.status = "empty";
    if (url !== null) URL.revokeObjectURL(url);
  }

  function dispose(root, record) {
    reset(record);
    records.delete(root);
  }

  function activate(scope) {
    for (const root of owners(scope)) {
      const nodes = dependencies(root);
      const previous = records.get(root);
      if (previous && matches(previous, nodes)) continue;
      if (previous) dispose(root, previous);
      if (!nodes || !root.isConnected) continue;
      const record = { nodes, generation: 0, url: null };
      records.set(root, record);
      reset(record);
      nodes.clear.hidden = false;
    }
  }

  function fail(record, message) {
    reset(record);
    record.nodes.input.value = "";
    record.nodes.status.textContent = message;
    record.nodes.status.dataset.status = "error";
  }

  async function select(root, record) {
    reset(record);
    const file = record.nodes.input.files[0];
    if (!file) return;
    if (file.type && !file.type.startsWith("image/")) {
      fail(record, "Choose an image file.");
      return;
    }
    const generation = record.generation;
    const nodes = record.nodes;
    let url = null;
    const isCurrent = () => records.get(root) === record
      && record.generation === generation && record.url === url
      && root.isConnected && nodes.body.isConnected && nodes.image.isConnected
      && matches(record, dependencies(root));
    try {
      url = URL.createObjectURL(file);
      record.url = url;
      nodes.image.src = url;
      nodes.status.textContent = "Loading image…";
      nodes.status.dataset.status = "loading";
      await nodes.image.decode();
      if (!isCurrent()) return;
      if (nodes.image.naturalWidth <= 0 || nodes.image.naturalHeight <= 0) {
        throw new Error("Image has no decoded dimensions.");
      }
      nodes.image.hidden = false;
      nodes.filename.textContent = file.name;
      nodes.status.textContent = "Image ready.";
      nodes.status.dataset.status = "success";
    } catch {
      if (!isCurrent()) return;
      fail(record, "This file could not be displayed as an image. Choose another image.");
    }
  }

  document.addEventListener("change", (event) => {
    if (!(event.target instanceof Element)) return;
    const input = event.target.closest("[data-image-input]");
    const root = input?.closest(selector);
    const record = root ? records.get(root) : null;
    if (!record || record.nodes.input !== input) return;
    void select(root, record);
  });
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-image-clear]");
    const root = button?.closest(selector);
    const record = root ? records.get(root) : null;
    if (!record || record.nodes.clear !== button) return;
    reset(record);
    record.nodes.input.value = "";
  });
  document.addEventListener("htmx:beforeCleanupElement", (event) => {
    const removed = event.detail.elt;
    for (const root of owners(removed)) {
      const record = records.get(root);
      if (!record) continue;
      if (removed.contains(root)
          || Object.values(record.nodes).some((node) => removed.contains(node))) {
        dispose(root, record);
      }
    }
  });
  document.addEventListener("htmx:load", (event) => activate(event.detail.elt));
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => activate(document), { once: true });
  } else {
    activate(document);
  }
})();
