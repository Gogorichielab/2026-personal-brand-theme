// Inlined in <head>: apply a saved choice before the page paints, then wire the footer control.
(() => {
  const root = document.documentElement;
  try {
    const saved = localStorage.getItem('appearance');
    if (saved === 'light' || saved === 'dark') root.dataset.appearance = saved;
  } catch (e) {}
  document.addEventListener('DOMContentLoaded', () => {
    const group = document.querySelector('.appearance');
    if (!group) return;
    const buttons = group.querySelectorAll('button');
    const show = (mode) => buttons.forEach((b) => b.setAttribute('aria-pressed', b.value === mode));
    buttons.forEach((b) => b.addEventListener('click', () => {
      if (b.value === 'system') delete root.dataset.appearance;
      else root.dataset.appearance = b.value;
      try {
        if (b.value === 'system') localStorage.removeItem('appearance');
        else localStorage.setItem('appearance', b.value);
      } catch (e) {}
      show(b.value);
    }));
    show(root.dataset.appearance || 'system');
    group.hidden = false;
  });
})();
