(() => {
  const field = document.querySelector('#blog-search');
  if (!field) return;
  const normal = document.querySelector('#archive-default');
  const results = document.querySelector('#search-results');
  const status = document.querySelector('#search-status');
  const t = field.dataset; // interface text from the theme's translations
  let index;
  let generation = 0;
  const load = () => index || (index = fetch(field.dataset.index).then(r => {
    if (!r.ok) throw new Error('Search unavailable');
    return r.json();
  }).catch(error => { index = null; throw error; }));
  field.addEventListener('input', async () => {
    const current = ++generation;
    const query = field.value.trim().toLocaleLowerCase();
    if (!query) { normal.hidden = false; results.hidden = true; status.textContent = ''; return; }
    status.textContent = t.searching;
    try {
      const posts = await load();
      if (current !== generation) return;
      const words = query.split(/\s+/);
      const matches = posts.filter(p => words.every(w => [p.title, p.text, ...p.tags].join(' ').toLocaleLowerCase().includes(w)));
      results.replaceChildren();
      for (const post of matches) {
        const article = document.createElement('article'); article.className = 'writing-card';
        const date = document.createElement('p'); date.className = 'post-meta'; date.textContent = post.date;
        const heading = document.createElement('h3');
        const link = document.createElement('a'); link.href = post.url; link.textContent = post.title; heading.append(link);
        const summary = document.createElement('p'); summary.textContent = post.summary;
        article.append(date, heading, summary); results.append(article);
      }
      normal.hidden = true; results.hidden = false;
      status.textContent = matches.length
        ? (matches.length === 1 ? t.foundOne : t.foundOther).replace('{count}', matches.length)
        : t.none;
    } catch (_) {
      if (current !== generation) return;
      status.textContent = t.error;
      normal.hidden = false; results.hidden = true;
    }
  });
})();
