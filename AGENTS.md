# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

A Hugo theme: simple, clean, personal-brand first, content second. See `README.md`.

## Conventions

- **Use [Conventional Commits](https://www.conventionalcommits.org/).** Releases are cut automatically from commit messages on `main`:
  - `feat:` → minor release, `fix:` / `perf:` → patch release, `feat!:` or a `BREAKING CHANGE:` footer → major release.
  - `docs:`, `chore:`, `style:`, `refactor:`, `test:`, `ci:` do not trigger a release.
- Don't create `v*` tags or GitHub Releases by hand; `.github/workflows/release.yml` tags each releasable merge to `main` and writes the release notes. There is no `CHANGELOG.md` or version file; release notes live on the GitHub Releases page.
- No Node: don't add `package.json` or npm dependencies. Use Hugo Pipes for any asset processing.
- Follow standard Hugo theme layout (`layouts/`, `assets/`, `static/`, `archetypes/`, `i18n/`, `theme.toml`) as it gets added.

## Pull requests

When you open a pull request, label it with the agent that created it:

| Created by | Label |
| --- | --- |
| Claude (Claude Code) | `Claude` |
| ChatGPT / OpenAI (e.g. Codex) | `OpenAI` |
| GitHub Copilot | `GitHub Copilot` |

Use the existing label exactly as named; don't create variants.

## Checking your work

- Build the demo with `hugo --source exampleSite --themesDir ../.. --theme 2026-personal-brand-theme` and fix any errors or warnings. `.github/workflows/pages.yml` deploys it to GitHub Pages on every push to `main`.
- The demo is served from a subpath (`/2026-personal-brand-theme/`), so build links with `relURL`/`.RelPermalink` and never `"/" | relURL` (a leading slash drops the subpath); use `site.Home.RelPermalink` for the home link.
- Keep pages accessible: semantic HTML, alt text, visible focus states, sufficient color contrast.
