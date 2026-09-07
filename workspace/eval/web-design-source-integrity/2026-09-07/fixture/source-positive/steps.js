(() => {
  const root = document.querySelector('[data-flow]');
  let step = 1;
  const name = root.querySelector('[name="display-name"]');
  function show(next) {
    step = next;
    root.querySelectorAll('[data-step]').forEach(section => { section.hidden = Number(section.dataset.step) !== step; });
    root.querySelectorAll('[data-progress]').forEach(item => {
      if (Number(item.dataset.progress) === step) item.setAttribute('aria-current', 'step');
      else item.removeAttribute('aria-current');
    });
    root.querySelector('[data-name-summary]').textContent = name.value || '기록';
    root.querySelector('[data-complete-name]').textContent = name.value || '기록';
    root.querySelector('[data-mood-summary]').textContent = root.querySelector('[name="mood"]:checked').value;
  }
  root.addEventListener('click', event => {
    if (event.target.closest('[data-next]')) show(step + 1);
    if (event.target.closest('[data-prev]')) show(step - 1);
    if (event.target.closest('[data-finish]')) show(4);
    if (event.target.closest('[data-restart]')) {
      name.value = '';
      root.querySelector('[name="mood"]').checked = true;
      show(1);
    }
    if (event.target.closest('[data-footnote]')) event.preventDefault();
  });
})();
