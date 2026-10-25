# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

A Hugo theme: simple, clean, personal-brand first, content second. See `README.md`.

Read `CONTRIBUTING.md` for the contribution workflow and local checks. Follow `SECURITY.md` when handling security reports.

## Conventions

- **Use [Conventional Commits](https://www.conventionalcommits.org/).** Releases are cut automatically from commit messages on `main`:
  - `feat:` → minor release, `fix:` / `perf:` → patch release, `feat!:` or a `BREAKING CHANGE:` footer → major release.
  - `docs:`, `chore:`, `style:`, `refactor:`, `test:`, `ci:` do not trigger a release.
- Don't create `v*` tags or GitHub Releases by hand; `.github/workflows/release.yml` tags each releasable merge to `main` and writes the release notes. There is no `CHANGELOG.md` or version file; release notes live on the GitHub Releases page.
- No Node: don't add `package.json` or npm dependencies. Use Hugo Pipes for any asset processing.
- Never hard-code interface text in templates or scripts. Add a key to `i18n/en.toml` (and `i18n/es.toml`) and use `T`; scripts read their text from `data-` attributes.
- Follow standard Hugo theme layout (`layouts/`, `assets/`, `static/`, `archetypes/`, `i18n/`, `theme.toml`) as it gets added.

## Skills

Use these skill packs. If your agent supports skills or plugins, install them; otherwise read the linked `SKILL.md` files and follow them.

| Pack | Use it for | Install |
| --- | --- | --- |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | **Every code change.** Write the smallest change that fully solves the task. Run `/ponytail-review` on your diff before opening a PR; `/ponytail-audit` for whole-repo reviews. | Claude Code: `/plugin marketplace add DietrichGebert/ponytail`, then `/plugin install ponytail@ponytail`. Codex: `codex plugin marketplace add DietrichGebert/ponytail`, then `codex plugin add ponytail@ponytail`. Others: follow its `AGENTS.md` / `skills/ponytail/SKILL.md`. |
| [Marketing Skills](https://github.com/coreyhaines31/marketingskills) | Copy and content: README and demo text (`copywriting`, `copy-editing`), page structure and metadata (`seo-audit`, `schema`, `site-architecture`, `ai-seo`), and launch posts (`launch`). | `npx skills add coreyhaines31/marketingskills` (add `-a claude-code` in Claude Code), or the plugin route in its README. |
| [Business Analysis Skills](https://github.com/45ck/business-analysis-skills) | Before building a feature: frame the problem (`problem-statement-refiner`), write `acceptance-criteria-writer` criteria, and find gaps (`edge-case-elicitor`, `requirements-gap-auditor`). | Clone it and run `bash install.sh`, or copy its `.claude/` / `.agents/` folders into your agent's skills directory. |

Install skills globally (in your home directory), not into this repo, and never commit skill files here. If a skill conflicts with this file, this file wins. Never cut accessibility to make a change smaller.

## Pull requests

- Use the repository's issue and PR templates. Link the related issue, explain the change, and report the checks you ran.
- Include before/after screenshots for visual changes. Update documentation, examples, and translations when behavior changes.
- Keep PR titles in Conventional Commits format.
- `.github/CODEOWNERS` assigns `@gogorichie` as the default owner for all files, including the ownership file. Keep ownership entries accurate; code-owner approval requirements are managed separately through repository rules.

When you open a pull request, label it with the agent that created it:

| Created by | Label |
| --- | --- |
| Claude (Claude Code) | `Claude` |
| ChatGPT / OpenAI (e.g. Codex) | `OpenAI` |
| GitHub Copilot | `GitHub Copilot` |

Use the existing label exactly as named; don't create variants.

## Checking your work

- For code changes, run `python3 -m unittest discover -s tests -v` with Hugo Extended available as `hugo`, or set `HUGO_BIN` to its executable path. Report any checks you could not run.
- For documentation-only changes, check links, formatting, and any commands or configuration examples you changed.
- Build the demo with `hugo --source exampleSite --themesDir ../.. --theme 2026-personal-brand-theme --minify --panicOnWarning` and fix any errors or warnings. `.github/workflows/pages.yml` deploys it to GitHub Pages on every push to `main`.
- The demo is served from a subpath (`/2026-personal-brand-theme/`), so build links with `relURL`/`.RelPermalink` and never `"/" | relURL` (a leading slash drops the subpath); use `site.Home.RelPermalink` for the home link.
- Keep pages accessible: semantic HTML, alt text, visible focus states, sufficient color contrast.
