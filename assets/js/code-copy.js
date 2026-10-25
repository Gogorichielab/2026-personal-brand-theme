(() => {
  const status = document.createElement('p');
  status.className = 'sr-only';
  status.setAttribute('role', 'status');
  document.body.append(status);

  for (const block of document.querySelectorAll('.article-body .highlight, .article-body pre')) {
    if (block.matches('.highlight pre')) continue; // copied through its .highlight wrapper
    const codes = block.querySelectorAll('code');
    const code = codes[codes.length - 1]; // with a line-number table, the last <code> holds the source
    if (!code) continue;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = 'Copy code';
    block.before(button);

    let reset;
    button.addEventListener('click', async () => {
      const source = code.cloneNode(true);
      source.querySelectorAll('.ln').forEach(number => number.remove()); // inline line numbers
      let message;
      try {
        await navigator.clipboard.writeText(source.textContent);
        button.textContent = 'Copied';
        message = 'Code copied to clipboard.';
      } catch (_) {
        button.textContent = 'Copy failed';
        message = 'Copy failed. Select the code and copy it manually.';
      }
      status.textContent = message;
      clearTimeout(reset);
      reset = setTimeout(() => { button.textContent = 'Copy code'; status.textContent = ''; }, 3000);
    });
  }
})();
