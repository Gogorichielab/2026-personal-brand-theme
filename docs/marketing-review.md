# Marketing review: Sunday morning

Reviewed the Hugo theme and example site using the [CRO](https://github.com/coreyhaines31/marketingskills/blob/e85f3cbc2e4a79bf33b2a12e9bdd9087d414735b/skills/cro/SKILL.md), [copywriting](https://github.com/coreyhaines31/marketingskills/blob/e85f3cbc2e4a79bf33b2a12e9bdd9087d414735b/skills/copywriting/SKILL.md), and [SEO audit](https://github.com/coreyhaines31/marketingskills/blob/e85f3cbc2e4a79bf33b2a12e9bdd9087d414735b/skills/seo-audit/SKILL.md) skills from coreyhaines31/marketingskills.

## Context and scope

This is a reusable personal-brand theme, with a fictional example author. Visitors should be able to understand the author's work, explore relevant articles, and reach a contact destination. Theme evaluators should be able to try those paths in the demo.

Copy diagnosis: B. The theme already has an informal voice centered on small projects and learning in public. Preserve that voice and the configurable layout; make the demo's subject and next actions more concrete.

There is no repository product-marketing context, traffic attribution, conversion baseline, Search Console data, or customer research. Goals are inferred from the README and templates. These changes address observable implementation problems; conversion or ranking gains have not been measured.

## Findings and applied changes

| Priority | Evidence before the change | Feedback | Applied change |
| --- | --- | --- | --- |
| High | Header, homepage, and speaking contact buttons led to `https://example.org/contact/`; relative destinations were rendered without `relURL`. | Remove dead ends and make the next step clear. | Add an explicitly labeled demo contact page and route the demo buttons there. Resolve relative CTA paths under the configured base URL; retain external links. Remove the fictional speaker-profile destination. |
| High | `baseof.html` used the site description whenever front matter omitted a description, including on individual posts. | Give search visitors a page-specific reason to click. | Use explicit descriptions, leads, or plain-text summaries. Add descriptions to the main demo pages and generated descriptions for topic archives. |
| High | Canonical metadata used the page permalink on every generated archive page. | Distinguish page 2 and later from the archive landing page. | Share paginator selection between metadata and archive templates. Give later pages their own canonical and Open Graph URLs, with page numbers in titles and descriptions. |
| Medium | The head emitted no Open Graph or Twitter card tags. | Make shared articles identifiable outside the site. | Add titles, descriptions, canonical sharing URLs, and optional bundle/static/remote images with a site-wide fallback. Preserve existing BlogPosting JSON-LD. |
| Medium | The demo hero said “Curiosity. Ideas. Community.” and introduced only “work, ideas, and people.” | Describe what a reader can actually find. | Use “Small tools. Useful notes. Shared openly.” and name web projects and accessibility. Give contact buttons a consistent “Start a conversation” label and explain what to include. |

## Further hypotheses

These require real visitors and a configured contact destination before testing:

- Compare the chosen hero with “Build for the web. Share what you learn.” The alternative puts the activity first; the chosen version matches the demo's posts and project examples.
- Compare “Start a conversation” with “Discuss a project” and “Invite me to speak.” A general contact label serves the demo's mixed audience; narrower labels may work better on a real project or speaking page.
- Compare the current about-first hero action with a projects-first action. Track completed contact actions as well as clicks so the test measures useful interest.

Do not add invented testimonials, audience counts, or performance claims. A real deployment needs the author's actual identity, examples of work, and contact details. Analytics, real-user performance, indexing, and social-platform rendering remain outside this local code review.

## Validation

Hugo Extended 0.152.2 built the production demo with warnings treated as errors. Five integration tests passed, building at both a domain root and a subpath plus a site-default-image configuration. They check description precedence and escaping, social image resolution, archive canonical URLs and post selection, contact destinations, all 17 search records, and generated internal links. The Pages workflow now runs these tests before uploading its artifact.
