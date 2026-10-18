// Project filter on the homepage + copy-email buttons.

document.addEventListener('DOMContentLoaded', () => {
  // ── filter ──
  const buttons = [...document.querySelectorAll('.filter')];
  const items = [...document.querySelectorAll('[data-tags]')];
  const other = document.querySelector('.other');
  const status = document.querySelector('.filter-status');

  function apply(filter) {
    let shown = 0;
    for (const item of items) {
      const match = filter === 'all' || item.dataset.tags.split(' ').includes(filter);
      item.classList.toggle('is-hidden', !match);
      if (match) shown++;
    }
    if (other) {
      const anyOther = other.querySelector('[data-tags]:not(.is-hidden)');
      other.classList.toggle('is-hidden', !anyOther);
    }
    for (const b of buttons) b.setAttribute('aria-pressed', String(b.dataset.filter === filter));
    if (status) status.textContent = `Showing ${shown} project${shown === 1 ? '' : 's'}`;
  }

  for (const b of buttons) b.addEventListener('click', () => apply(b.dataset.filter));

  // ── copy email ──
  for (const btn of document.querySelectorAll('[data-copy]')) {
    btn.addEventListener('click', async () => {
      const text = btn.dataset.copy;
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        const ta = Object.assign(document.createElement('textarea'), { value: text });
        document.body.append(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
      }
      const label = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(() => { btn.textContent = label; }, 1600);
    });
  }
});
