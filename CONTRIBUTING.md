# Contributing

Bug reports, fixes, documentation, translations, and testing are welcome.

## Open an issue

Check [existing issues](https://github.com/Gogorichielab/2026-personal-brand-theme/issues) first. Use the bug report or feature request template. For a larger change, discuss the approach in an issue before starting.

Report security vulnerabilities privately using the instructions in [SECURITY.md](SECURITY.md).

## Make a change

1. Fork the repository and clone your fork into a directory named `2026-personal-brand-theme`.
2. Create a branch for your change.
3. Keep the change focused. Update the documentation or example site when behavior changes.
4. Open a pull request against `main`. Link the issue, explain what changed, and describe how you checked it. Include screenshots for visual changes.

## Local checks

Install [Hugo Extended](https://gohugo.io/installation/) 0.146.0 or later and Python 3. From the repository root, run:

```sh
hugo --source exampleSite --themesDir ../.. --theme 2026-personal-brand-theme --minify --panicOnWarning
python3 -m unittest discover -s tests -v
```

The tests use `hugo` from your PATH, or the executable specified by `HUGO_BIN`. Pull requests also run the Hugo build and test matrix in GitHub Actions.

For documentation-only changes, check links, formatting, and any commands or configuration examples you changed.

## Project conventions

- Use [Conventional Commits](https://www.conventionalcommits.org/), such as `fix: correct a mobile layout` or `docs: clarify search setup`. Use the same format for your PR title.
- Keep the Hugo build free of Node/npm dependencies; use Hugo Pipes for asset processing.
- Add interface text to `i18n/en.toml` and `i18n/es.toml` and use Hugo's translation functions. Browser scripts read translated text from `data-` attributes.
- Preserve keyboard access, visible focus states, alt text, and readable color contrast.
- Make links work at both a domain root and a hosting subpath.
- AI-assisted contributions should follow [AGENTS.md](AGENTS.md), including its review guidance and agent-label conventions.

Releases are automated after changes reach `main`; contributors do not need to create release tags or a changelog.
