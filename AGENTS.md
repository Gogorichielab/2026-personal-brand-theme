# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

A Hugo theme: simple, clean, personal-brand first, content second. See `README.md`.

## Conventions

- **Use [Conventional Commits](https://www.conventionalcommits.org/).** Releases are cut automatically from commit messages on `main`:
  - `feat:` → minor release, `fix:` / `perf:` → patch release, `feat!:` or a `BREAKING CHANGE:` footer → major release.
  - `docs:`, `chore:`, `style:`, `refactor:`, `test:`, `ci:` do not trigger a release.
- Don't edit `CHANGELOG.md` by hand or create `v*` tags manually; `.github/workflows/release.yml` owns both. Versions come from git tags (`vX.Y.Z`), not a version file.
- No Node: don't add `package.json` or npm dependencies. Use Hugo Pipes for any asset processing.
- Follow standard Hugo theme layout (`layouts/`, `assets/`, `static/`, `archetypes/`, `i18n/`, `theme.toml`) as it gets added.

## Checking your work

- If an `exampleSite/` exists, build it with `hugo --source exampleSite --themesDir ../.. --theme 2026-personal-brand-theme` and fix any errors or warnings.
- Keep pages accessible: semantic HTML, alt text, visible focus states, sufficient color contrast.
