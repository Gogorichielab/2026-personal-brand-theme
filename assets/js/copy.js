(() => {
  // Interface text comes from the theme's translations, set on this <script> tag.
  const t = document.currentScript.dataset;
  const status = document.createElement('p');
  status.className = 'sr-only';
  status.setAttribute('role', 'status');
  document.body.append(status);

  // A button that copies getText() and reports the result visibly and to assistive technology.
  const copyButton = (label, done, failed, getText, onFail) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = label;
    let reset;
    button.addEventListener('click', async () => {
      let message = done;
      try {
        await navigator.clipboard.writeText(getText());
        button.textContent = t.copied;
      } catch (_) {
        button.textContent = t.copyFailed;
        message = failed;
        if (onFail) onFail();
      }
      status.textContent = message;
      clearTimeout(reset);
      reset = setTimeout(() => { button.textContent = label; status.textContent = ''; }, 3000);
    });
    return button;
  };

  if (t.code) {
    for (const block of document.querySelectorAll('.article-body .highlight, .article-body pre')) {
      if (block.matches('.highlight pre')) continue; // copied through its .highlight wrapper
      const codes = block.querySelectorAll('code');
      const code = codes[codes.length - 1]; // with a line-number table, the last <code> holds the source
      if (!code) continue;
      block.before(copyButton(t.copyCode, t.copyCodeDone, t.copyCodeFailed, () => {
        const source = code.cloneNode(true);
        source.querySelectorAll('.ln').forEach(number => number.remove()); // inline line numbers
        return source.textContent;
      }));
    }
  }

  const share = document.querySelector('.article-share[data-url]');
  if (share) {
    const url = share.dataset.url;
    share.append(copyButton(t.copyLink, t.copyLinkDone, t.copyLinkFailed, () => url, () => {
      if (share.querySelector('.share-fallback')) return;
      // Leave a visible, selectable link when the clipboard can't be used.
      const fallback = document.createElement('p');
      fallback.className = 'share-fallback';
      const link = document.createElement('a');
      link.href = url;
      link.textContent = url;
      fallback.append(t.copyLinkFailed + ' ', link);
      share.after(fallback);
    }));
    share.hidden = false;
  }
})();
