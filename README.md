# 2026 Personal Brand Theme

A responsive Hugo theme that puts a person and their work up front, with the blog close behind. It includes a configurable homepage, post archive, optional client-side search, author details, social links, project highlights, and an optional speaking page layout.

![Example homepage showing the personal introduction, latest blog posts, project highlights, and contact section.](exampleSite/homepage-screenshot.png)

## Requirements

- Hugo Extended 0.146.0 or later

## Install

Add the theme as a Git submodule:

```sh
git submodule add https://github.com/Gogorichielab/2026-personal-brand-theme.git themes/2026-personal-brand-theme
```

Set the theme in your Hugo configuration:

```toml
theme = "2026-personal-brand-theme"
```

The theme uses your `Site.Title`, main menu, content, and Hugo taxonomies. Set the parameters you need to personalize the homepage and shared site chrome:

```toml
[params.author]
	name = "Example Person"
	location = "Somewhere"
	image = "images/portrait.jpg"
	image_alt = "Example Person"
	bio = "A short author biography."

[params.brand]
	name = "Example"
	mark = "."
	connect_url = "https://example.org/contact/"
	connect_text = "Let's connect"
	about_url = "about/"
	github_url = "https://github.com/example"
	footer_tagline = "Always learning and sharing."

[params.home]
	headline = ["Curiosity.", "Ideas."]
	headline_accent = "Community."
	intro = ["A short introduction to your work.", "Add another paragraph if useful."]
	areas = ["What you do", "What you build", "Who you help"]
	about_url = "about/"
	blog_url = "blog/"
	topics = ["Technology", "Projects"]
	cta_url = "https://example.org/contact/"

[[params.social]]
	name = "GitHub"
	url = "https://github.com/example"
```

Homepage highlights are optional repeatable entries:

```toml
[[params.home.highlights]]
	eyebrow = "01 / Build"
	title_lines = ["Ideas into", "working things."]
	description = "A short description of this area."
	url = "projects/"
	link_text = "Explore projects"
```

## Page Headings

Section and page headings have defaults you can replace in each page's front matter:

| Page | Front matter keys |
| --- | --- |
| Blog and other lists (`content/blog/_index.md`, …) | `eyebrow`, `heading` |
| Projects (`content/projects/_index.md`) | `eyebrow`, `heading`, `list_heading`, `github_text` |
| Speaking (`content/speaking/index.md`) | `eyebrow`, `invite_text`, `profile_text` |

```yaml
---
title: "Blog"
eyebrow: "Writing"
heading: "Notes and essays"
---
```

## Blog Search

Search is opt-in. To enable it, add `enabled = true` under `[params.search]`, configure a `Search` output format, and add `Search` to the outputs for your blog section:

```toml
[params.search]
	enabled = true

[outputFormats.Search]
	mediaType = "application/json"
	baseName = "search"
	isPlainText = true
	notAlternative = true
```

```yaml
outputs: ["HTML", "RSS", "Search"]
```

## Contact Links

Set `params.brand.connect_url` and `params.home.cta_url` to a relative page path such as `contact/`, a full HTTPS URL, or a `mailto:` link. The speaking page's `invite_url` and `profile_url` accept the same formats. Relative paths respect your site's `baseURL`, including a GitHub Pages subpath.

The example site includes a demo contact page. Replace its instructions with your own contact details before publishing; it does not send messages.

## Search and Social Previews

Give important pages a `description` in front matter. The theme uses it for the search description, Open Graph tags, and Twitter card tags. Without one, it uses a page's `lead`, then its content summary; the homepage uses `params.description`. Topic archives get descriptions based on their topic. Paginated archives have their own canonical URLs and page numbers in their titles.

For a social preview image, set `images` to a list of image paths in front matter:

```yaml
description: "What readers will learn from this article."
images: ["cover.png"]
```

An image in a page bundle is resolved from that bundle. Static images can use paths such as `images/social-card.png`, and absolute HTTPS image URLs are also supported. Set `params.images` in the site configuration for a default social image. Pages without an image use a summary card.

## Validation

Run `python3 -m unittest discover -s tests -v` with Hugo Extended available as `hugo`, or set `HUGO_BIN` to its executable path. The integration checks build the demo at both a domain root and a subpath, then check metadata, archive pagination, contact links, and search data.

See [`exampleSite/`](exampleSite/) for a working minimal setup, deployed as a live demo at <https://gogorichielab.github.io/2026-personal-brand-theme/>. The build command from the theme repository is:

```sh
hugo --source exampleSite --themesDir ../.. --theme 2026-personal-brand-theme --minify
```

## License

MIT. See [LICENSE](LICENSE).
