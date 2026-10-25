# Security Policy

## System and Scope

This repository is a Hugo theme and an example static site. The demo is built and deployed to GitHub Pages; people using the theme can deploy it elsewhere.

Security review covers:

- Hugo layouts, partials, shortcodes, image rendering, and generated HTML, JSON, metadata, and feeds.
- Browser-side search in `assets/js/personal.js` and its generated index.
- Example content and configuration where they demonstrate security-sensitive behavior.
- GitHub Actions, dependency updates, build artifacts, release automation, and deployment permissions.

There is no application server, database, login system, or message-processing contact form in the repository. The example contact page is documentation, not a submission endpoint. Hosting controls and integrations added by downstream users require their own assessment; repository code that undermines those controls remains relevant.

## Supported Versions

Security fixes target `main` and the latest stable release. Reports involving older releases are welcome, but backports are assessed individually and are not guaranteed. Include the exact theme tag or commit and Hugo version in every report.

The previous 5.x/4.x version table was placeholder text and did not describe this project's releases. This policy establishes no fixed acknowledgement or remediation deadline.

## Reporting a Vulnerability

Use [GitHub private vulnerability reporting](https://github.com/Gogorichielab/2026-personal-brand-theme/security/advisories/new). Private reporting is enabled for this repository.

Include the affected commit or release, relevant paths, required configuration, attacker-controlled input, reproduction steps, expected behavior, and observed impact. Use a minimal example without real secrets or personal information. Identify whether the problem affects the demo, sites using the theme, the build environment, or release integrity.

Do not put exploit details, credentials, or private data in a public issue or pull request. If private reporting becomes unavailable, open an issue requesting a private contact channel without disclosing vulnerability details.

## Threat Model and Trust Boundaries

- Anonymous visitors can supply search queries and interact with published pages. A query must not gain the ability to execute script or change the deployed site.
- Site maintainers control templates, configuration, Markdown, front matter, bundled images, and authored HTML. The raw HTML shortcode is not a sanitizer or a sandbox for untrusted submissions.
- Reviewers must identify the actual content source and publishing permissions. Content imported from external systems or contributed by less-trusted authors must not automatically be treated as trusted just because it appears in the repository.
- Search-index text, titles, summaries, tags, URLs, and metadata cross output-context boundaries. Evaluate HTML, attributes, JavaScript, JSON, and URL handling in their actual consumers.
- Pull request content is less trusted than the release and deployment environment. CI tokens, repository write access, release tags, artifacts, and deployment authority are sensitive assets.
- External fonts, linked resources, Hugo distributions, and GitHub Actions are dependencies. Distinguish a defect in this repository's integration from an upstream or hosting issue, and describe the resulting repository impact.

## Security Invariants

- Visitor-controlled queries and lower-trust content must not become executable HTML, script, or unsafe navigation. Preserve context-appropriate escaping; scrutinize `safeHTML`, `safeJS`, `safeURL`, and DOM assignments rather than assuming they validate their inputs.
- Search results must display textual fields as text. Search failure must not introduce an unsafe fallback. Generated URL fields need assessment separately from text fields.
- Metadata and structured data must serialize and escape correctly, including quotes, markup, and script-closing sequences.
- Generated pages, feeds, search indexes, assets, logs, and artifacts must not expose credentials or content that was not intended for publication. A static site provides no access control for a published URL.
- Untrusted pull requests and dependency changes must not gain privileged tokens, execute with release authority, or publish a deployment. Check event types, actor checks, permission scopes, artifact provenance, and workflow inputs.
- Releases and deployments must preserve the integrity of reviewed source and build inputs. Evaluate downloaded tools and third-party actions as part of that chain.

These are review requirements, not claims that every control has already been validated.

## Reportable Findings and Severity Context

Report a concrete violation with a realistic input source, reachable execution path, affected trust boundary, and demonstrated or well-supported impact. Relevant impacts include script execution in another visitor's browser, disclosure of unpublished content or credentials, malicious navigation through a lower-trust input, and compromise of CI, releases, or deployments.

Explain who controls the input and what access they already have. A maintainer deliberately adding executable site code does not by itself demonstrate an attacker crossing a trust boundary. Conversely, do not dismiss a content-based issue without determining whether an attacker can influence the content in the affected deployment.

Calibrate severity to the privileges gained, affected users or artifacts, required interaction, and configuration prerequisites. Missing hardening or an unsafe-looking API is evidence to investigate; do not equate it with an exploitable vulnerability without tracing the relevant boundary.

## Exclusions, Accepted Risk, and Known Limitations

No additional finding-class exclusions or accepted vulnerabilities are established by this policy. Unclear deployment assumptions and proposed risk acceptance require maintainer confirmation; they must not silently suppress a finding.

The theme cannot enforce downstream hosting headers, repository branch protection, private build inputs, or a user's custom templates and integrations. Check those controls when evidence is available and identify unknown settings explicitly.

The integration suite checks rendered metadata, links, images, archive pagination, and search data. Passing those checks is not proof of XSS resistance, supply-chain integrity, or safe handling of arbitrary imported content. A policy review is not a completed security scan.
