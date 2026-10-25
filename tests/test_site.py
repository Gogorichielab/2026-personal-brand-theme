"""Build and inspect real Hugo output without third-party dependencies."""

import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit


REPO = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.meta = {}
        self.links = []
        self.canonical = []
        self.title = ""
        self.in_title = False
        self.h1_count = 0
        self.images = []
        self.in_card = False
        self.card_urls = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and attrs.get("class") == "writing-card":
            self.in_card = True
        if tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            if key:
                self.meta.setdefault(key, []).append(attrs.get("content"))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical.append(attrs["href"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
            if self.in_card:
                self.card_urls.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag):
        if tag == "article":
            self.in_card = False
        if tag == "title":
            self.in_title = False

    def handle_data(self, text):
        if self.in_title:
            self.title += text

    def value(self, name):
        values = self.meta[name]
        assert len(values) == 1, (name, values)
        return values[0]


def tiny_png(width, height):
    """A solid-color RGB PNG, so tests need no image library."""
    import struct
    import zlib

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    rows = (b"\x00" + b"\x2d\x60\x89" * width) * height
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="theme-integration-")
        cls.addClassCleanup(cls.temp.cleanup)
        work = Path(cls.temp.name)
        source = work / "example"
        shutil.copytree(
            REPO / "exampleSite", source,
            ignore=shutil.ignore_patterns("public", "resources", ".hugo_build.lock"),
        )
        # Exercise explicit descriptions containing punctuation and HTML escaping.
        (source / "content" / "metadata-check.md").write_text(
            '---\ntitle: "Metadata check"\n'
            'description: \'Read "small tools" & practical examples.\'\n'
            'lead: "This lead must not replace the description."\n'
            '---\n\nA different body summary.\n'
        )
        # Verify that absolute CTA destinations survive URL resolution.
        (source / "content" / "external-speaking.md").write_text(
            '---\ntitle: "External speaking"\ntype: "speaking"\n'
            'headline_lines: ["External speaking"]\n'
            'invite_url: "https://example.net/invite/"\n'
            'profile_url: "mailto:speaker@example.net"\n---\n'
        )
        (source / "content" / "remote-image.md").write_text(
            '---\ntitle: "Remote image"\n'
            'images: ["https://example.net/social.png"]\n---\n'
        )
        # A draft sharing first-post's tag must never be recommended.
        (source / "content" / "blog" / "draft-note.md").write_text(
            '---\ntitle: "Draft note"\ndate: 2026-10-01\ndraft: true\ntags: ["notes"]\n---\nDraft.\n'
        )
        # A title with spaces, Unicode and reserved characters for share links.
        (source / "content" / "blog" / "share-check.md").write_text(
            '---\ntitle: "Tom & Jerry: café? 50%"\ndate: 2025-01-01\n---\nShare check.\n'
        )
        # A bundled image narrower than every candidate width, and an external one.
        small = source / "content" / "image-check"
        small.mkdir()
        (small / "small.png").write_bytes(tiny_png(300, 100))
        (small / "index.md").write_text(
            '---\ntitle: "Image check"\n---\n\n![Small](small.png)\n\n'
            '![External](https://example.net/photo.jpg)\n'
        )
        # A series outside the blog whose part numbers disagree with the dates, plus a draft part.
        guides = source / "content" / "guides"
        guides.mkdir()
        for slug, date, weight, extra in (("c", "2025-03-01", 1, ""), ("a", "2025-01-01", 3, ""),
                                          ("b", "2025-02-01", 2, ""), ("draft", "2025-04-01", 4, "draft: true\n")):
            (guides / f"series-{slug}.md").write_text(
                f'---\ntitle: "Part {slug}"\ndate: {date}\nseries: ["Test Series"]\n'
                f'series_weight: {weight}\n{extra}---\nBody.\n'
            )
        cls.source, cls.work = source, work
        cls.sites = []
        for name, prefix in (("root", "/"), ("subpath", "/theme-demo/")):
            output = work / name
            base = "https://example.test" + prefix
            subprocess.run(
                [
                    os.environ.get("HUGO_BIN", "hugo"),
                    "--source", str(source),
                    "--themesDir", str(REPO.parent),
                    "--theme", REPO.name,
                    "--destination", str(output),
                    "--baseURL", base,
                    "--minify", "--panicOnWarning", "--noBuildLock",
                ],
                env={
                    **os.environ,
                    "HUGO_RESOURCEDIR": str(work / "resources"),
                },
                check=True, capture_output=True, text=True,
            )
            cls.sites.append((output, base, prefix))
        # Rebuild with a site-wide static image to check the optional fallback.
        override = source / "social.toml"
        override.write_text(
            '[params]\nimages = ["/images/portrait.svg"]\n'
            'image_alt = "Site default preview"\n'
        )
        cls.default_site = work / "default-image"
        subprocess.run(
            [
                os.environ.get("HUGO_BIN", "hugo"),
                "--source", str(source),
                "--themesDir", str(REPO.parent),
                "--theme", REPO.name,
                "--destination", str(cls.default_site),
                "--baseURL", "https://example.test/theme-demo/",
                "--config", f"{source / 'config.toml'},{override}",
                "--panicOnWarning", "--noBuildLock",
            ],
            env={**os.environ, "HUGO_RESOURCEDIR": str(work / "resources")},
            check=True, capture_output=True, text=True,
        )

    def test_optional_social_images(self):
        for output, _, _ in self.sites:
            remote = Page(output / "remote-image/index.html")
            self.assertEqual(remote.value("og:image"), "https://example.net/social.png")
        fallback = Page(self.default_site / "index.html")
        self.assertEqual(
            fallback.value("og:image"),
            "https://example.test/theme-demo/images/portrait.svg",
        )
        self.assertEqual(fallback.value("twitter:card"), "summary_large_image")
        self.assertEqual(fallback.value("og:image:alt"), "Site default preview")
        self.assertEqual(fallback.value("twitter:image:alt"), "Site default preview")
        bundle = Page(self.default_site / "blog/building-this-theme/index.html")
        self.assertEqual(
            bundle.value("og:image"),
            "https://example.test/theme-demo/blog/building-this-theme/cover.png",
        )
        # A page's own image keeps its own alt text, not the site default's.
        self.assertEqual(
            bundle.value("og:image:alt"),
            "Abstract cover illustration in the theme's blue palette",
        )
        for output, _, _ in self.sites:
            remote = Page(output / "remote-image/index.html")
            self.assertNotIn("og:image:alt", remote.meta)
            self.assertNotIn("twitter:image:alt", remote.meta)

    def test_page_descriptions_and_sharing(self):
        for output, base, _ in self.sites:
            with self.subTest(base=base):
                home = Page(output / "index.html")
                post = Page(output / "blog/first-post/index.html")
                self.assertIn("Every site starts somewhere", post.value("description"))
                self.assertNotEqual(post.value("description"), home.value("description"))
                self.assertEqual(post.value("og:description"), post.value("description"))
                self.assertEqual(post.value("twitter:description"), post.value("description"))
                self.assertEqual(post.value("og:type"), "article")
                self.assertEqual(home.value("og:type"), "website")
                self.assertEqual(post.value("twitter:card"), "summary")
                explicit = Page(output / "metadata-check/index.html")
                self.assertEqual(
                    explicit.value("description"),
                    'Read "small tools" & practical examples.',
                )
                bundle = Page(output / "blog/building-this-theme/index.html")
                self.assertEqual(
                    bundle.value("description"),
                    "Why I built a Hugo theme that puts the person first and the blog close behind.",
                )
                self.assertEqual(bundle.value("twitter:card"), "summary_large_image")
                self.assertEqual(
                    bundle.value("og:image"),
                    base + "blog/building-this-theme/cover.png",
                )
                self.assertEqual(bundle.value("twitter:image"), bundle.value("og:image"))
                topic = Page(output / "tags/notes/index.html")
                self.assertEqual(
                    topic.value("description"), "Browse posts about Notes on Example Person."
                )

    def test_archive_metadata_and_post_selection(self):
        for output, base, prefix in self.sites:
            for archive in ("", "blog/", "tags/", "tags/notes/"):
                with self.subTest(base=base, archive=archive):
                    first = Page(output / archive / "index.html")
                    second = Page(output / archive / "page/2/index.html")
                    expected = base + archive + "page/2/"
                    self.assertEqual(second.canonical, [expected])
                    self.assertEqual(second.value("og:url"), expected)
                    self.assertIn("Page 2", second.title)
                    self.assertNotEqual(second.title, first.title)
                    self.assertIn("(Page 2)", second.value("description"))
            for archive in ("", "blog/"):
                second = Page(output / archive / "page/2/index.html")
                # The head must not initialize the homepage paginator with all pages.
                entries = json.loads((output / "blog/search.json").read_text())
                self.assertEqual(
                    set(second.card_urls), {entry["url"] for entry in entries[6:12]}
                )
                self.assertTrue((output / archive / "page/3/index.html").is_file())

    def test_contact_journey_and_external_links(self):
        for output, base, prefix in self.sites:
            with self.subTest(base=base):
                for path in ("index.html", "about/index.html", "speaking/index.html"):
                    page = Page(output / path)
                    self.assertIn(prefix + "contact/", page.links)
                    self.assertNotIn("https://example.org/contact/", page.links)
                home = Page(output / "index.html")
                self.assertEqual(home.links.count(prefix + "contact/"), 2)
                speaking = Page(output / "speaking/index.html")
                self.assertEqual(speaking.links.count(prefix + "contact/"), 2)
                external = Page(output / "external-speaking/index.html")
                self.assertIn("https://example.net/invite/", external.links)
                self.assertIn("mailto:speaker@example.net", external.links)
                contact = (output / "contact/index.html").read_text()
                self.assertIn("does not send a message", contact)

    def test_search_and_internal_links(self):
        for output, base, prefix in self.sites:
            with self.subTest(base=base):
                entries = json.loads((output / "blog/search.json").read_text())
                self.assertEqual(len(entries), 19)
                for entry in entries:
                    self.assertTrue(entry["url"].startswith(prefix + "blog/"))
                for path in output.rglob("*.html"):
                    page = Page(path)
                    # Hugo's redirect aliases have no page metadata or main content.
                    if not page.canonical:
                        continue
                    relative = path.relative_to(output).as_posix()
                    url = base + relative.removesuffix("index.html")
                    if not page.h1_count:
                        continue
                    self.assertEqual(page.h1_count, 1, path)
                    for href in page.links:
                        destination = urlsplit(urljoin(url, href))
                        if destination.netloc != "example.test":
                            continue
                        self.assertTrue(destination.path.startswith(prefix), (path, href))
                        target = output / destination.path[len(prefix):]
                        self.assertTrue(
                            target.is_file() or (target / "index.html").is_file(),
                            (path, href),
                        )

    def build(self, name, toml):
        """Build the example site with an extra config file; return the result."""
        override = self.source / f"{name}.toml"
        override.write_text(toml)
        output = self.work / name
        result = subprocess.run(
            [
                os.environ.get("HUGO_BIN", "hugo"),
                "--source", str(self.source),
                "--themesDir", str(REPO.parent),
                "--theme", REPO.name,
                "--destination", str(output),
                "--config", f"{self.source / 'config.toml'},{override}",
                "--noBuildLock",
            ],
            env={**os.environ, "HUGO_RESOURCEDIR": str(self.work / "resources")},
            capture_output=True, text=True,
        )
        return result, output

    @staticmethod
    def stylesheet(output):
        (css,) = (output / "css").glob("personal*.css")
        return css.read_text()

    @staticmethod
    def related(output, slug):
        page = (output / "blog" / slug / "index.html").read_text()
        if 'id="related-title"' not in page and "id=related-title" not in page:
            return None
        section = page.split("related-title", 1)[1].split("</section>", 1)[0]
        return re.findall(r'<h3><a href="?([^" >]+)', section)

    def test_related_articles(self):
        lists = []
        for output, base, prefix in self.sites:
            with self.subTest(base=base):
                links = self.related(output, "first-post")
                self.assertTrue(links)
                self.assertLessEqual(len(links), 3)
                self.assertEqual(len(links), len(set(links)))
                self.assertNotIn(prefix + "blog/first-post/", links)
                self.assertTrue(all(link.startswith(prefix + "blog/") for link in links))
                self.assertFalse(any("draft-note" in link for link in links))
                # A post sharing no tags gets no section, and older/newer links stay.
                self.assertIsNone(self.related(output, "podcast-guest"))
                self.assertIn("article-neighbors", (output / "blog/podcast-guest/index.html").read_text())
                lists.append([link.removeprefix(prefix) for link in links])
        # Two separate builds of the same content recommend the same posts in the same order.
        self.assertEqual(lists[0], lists[1])

    def test_related_articles_can_be_disabled(self):
        result, output = self.build("no-related", "[params.related]\nenabled = false\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(self.related(output, "first-post"))

    def test_responsive_article_images(self):
        for output, base, prefix in self.sites:
            with self.subTest(base=base):
                (cover,) = Page(output / "blog/building-this-theme/index.html").images[:1]
                widths = [int(c.split()[1].rstrip("w")) for c in cover["srcset"].split(", ")]
                self.assertEqual(widths, [480, 800, 1200])  # source is 1200px wide
                self.assertIn("sizes", cover)
                self.assertTrue(cover["src"].startswith(prefix) and cover["src"].endswith(".webp"))
                self.assertEqual((cover["width"], cover["height"]), ("1200", "630"))
                self.assertEqual((cover["loading"], cover["decoding"]), ("lazy", "async"))
                self.assertTrue(cover["alt"])
                small, external = Page(output / "image-check/index.html").images[:2]
                self.assertNotIn("srcset", small)  # no candidate may exceed the 300px source
                self.assertEqual(small["width"], "300")
                self.assertEqual(external["src"], "https://example.net/photo.jpg")
                self.assertNotIn("srcset", external)

    def test_copy_script_only_where_needed(self):
        script = re.compile(r'<script src="?[^ >"]*/js/copy\.min[^>]*>')
        for output, _, _ in self.sites:
            code = script.search((output / "blog/copying-code-examples/index.html").read_text())
            self.assertIn("data-code", code.group(0))
            post = script.search((output / "blog/first-post/index.html").read_text())  # copy link only
            self.assertNotIn("data-code", post.group(0))
            self.assertIsNone(script.search((output / "index.html").read_text()))
        result, output = self.build(
            "no-copy", "[params.copy_code]\nenabled = false\n[params.share]\nenabled = false\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        page = (output / "blog/copying-code-examples/index.html").read_text()
        self.assertIsNone(script.search(page))
        self.assertNotIn("article-share", page)

    def test_share_links(self):
        for output, base, _ in self.sites:
            with self.subTest(base=base):
                page = (output / "blog/share-check/index.html").read_text()
                hrefs = re.findall(r'href="?([^" >]+)"?>(?:LinkedIn|Bluesky|Email)<', page)
                self.assertEqual(len(hrefs), 3)  # only the configured destinations
                url = (base + "blog/share-check/").replace(":", "%3A").replace("/", "%2F")
                title = "Tom%20%26%20Jerry%3A%20caf%C3%A9%3F%2050%25"
                linkedin, bluesky, email = (h.replace("&amp;", "&") for h in hrefs)
                self.assertEqual(linkedin, "https://www.linkedin.com/sharing/share-offsite/?url=" + url)
                self.assertEqual(bluesky, f"https://bsky.app/intent/compose?text={title}%20{url}")
                self.assertEqual(email, f"mailto:?subject={title}&body={url}")
        result, _ = self.build("bad-share", '[params.share]\ndestinations = ["myspace"]\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("params.share.destinations", result.stderr)

    def test_series(self):
        for output, base, prefix in self.sites:
            with self.subTest(base=base):
                term = (output / "series/test-series/index.html").read_text()
                url = lambda slug: prefix + f"guides/series-{slug}/"
                # Part order wins over dates, and the draft part stays out.
                self.assertEqual(re.findall(r'<h3><a href="?([^" >]+)', term), [url("c"), url("b"), url("a")])
                self.assertFalse((output / "guides/series-draft").exists())
                for slug, position, prev, nxt in (("c", 1, None, "b"), ("b", 2, "c", "a"), ("a", 3, "b", None)):
                    page = (output / f"guides/series-{slug}/index.html").read_text()
                    self.assertIn(f"Part {position} of 3", page)
                    self.assertRegex(page, rf'href="?{re.escape(url(slug))}"? aria-current="?page')
                    found = lambda label: (re.findall(rf'href="?([^" >]+)"?><small>{label}', page) or [None])[0]
                    self.assertEqual(found("← Previous part"), prev and url(prev))
                    self.assertEqual(found("Next part →"), nxt and url(nxt))
                plain = (output / "blog/first-post/index.html").read_text()
                self.assertNotIn("series-box", plain)
                self.assertNotIn("Previous part", plain)
        for name, front_matter, message in (
            ("missing", 'series: ["Test Series"]', "needs a series_weight"),
            ("repeated", 'series: ["Test Series"]\nseries_weight: 2', "both have series_weight 2"),
            ("two-series", 'series: ["Test Series", "Other"]\nseries_weight: 9', "can belong to one series"),
        ):
            with self.subTest(name=name):
                bad = self.source / "content" / "guides" / "series-bad.md"
                bad.write_text(f'---\ntitle: "Bad"\n{front_matter}\n---\nBody.\n')
                try:
                    result, _ = self.build(f"series-{name}", "")
                finally:
                    bad.unlink()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    @staticmethod
    def switcher(page):
        nav = re.search(r'<nav class="?lang-nav.*?</nav>', page, re.S)
        return nav and dict((lang, href) for href, lang in re.findall(r'href="?([^" >]+)"? lang="?(\w+)', nav.group(0)))

    def test_translations_and_language_switcher(self):
        for output, base, prefix in self.sites:
            with self.subTest(base=base):
                spanish = (output / "es/index.html").read_text()
                self.assertRegex(spanish, r'<html lang="?es')
                self.assertIn("Saltar al contenido", spanish)
                self.assertIn("Built with", spanish)  # missing from es.toml, so English is used
                self.assertNotIn("Saltar al contenido", (output / "index.html").read_text())
                # A translated page links to its translation; others fall back to the language's home.
                self.assertEqual(self.switcher((output / "blog/first-post/index.html").read_text())["es"],
                                 prefix + "es/blog/first-post/")
                self.assertEqual(self.switcher((output / "blog/notes-on-writing/index.html").read_text())["es"],
                                 prefix + "es/")
                self.assertEqual(self.switcher(spanish)["en"], prefix)
                entries = json.loads((output / "es/blog/search.json").read_text())
                self.assertEqual([e["url"] for e in entries], [prefix + "es/blog/first-post/"])
                self.assertIn("12 de enero de 2026", (output / "es/blog/first-post/index.html").read_text())
        result, output = self.build("one-language", 'disableLanguages = ["es"]\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("lang-nav", (output / "index.html").read_text())

    def test_dark_appearance(self):
        for output, _, _ in self.sites:  # the example site opts into "toggle", which includes "auto"
            css = self.stylesheet(output)
            self.assertIn("prefers-color-scheme:dark", css)
            self.assertIn("--ink:#e4edf6", css)
            self.assertIn("--surface:#ffffff", css)
        result, output = self.build("light-only", '[params.colors]\nappearance = "light"\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        css = self.stylesheet(output)
        self.assertNotIn("prefers-color-scheme", css)
        self.assertNotIn("#e4edf6", css)
        result, _ = self.build("bad-appearance", '[params.colors]\nappearance = "dim"\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("params.colors.appearance", result.stderr)

    def test_appearance_toggle(self):
        for output, base, _ in self.sites:
            with self.subTest(base=base):
                page = (output / "index.html").read_text()
                head = page.split("</head>", 1)[0]
                self.assertIn('localStorage.getItem("appearance")', head)  # inline, so a saved choice applies before paint
                control = re.search(r'<div class="?appearance"?.*?</div>', page, re.S).group(0)
                self.assertRegex(control, r'role="?group"? aria-labelledby="?appearance-label"? hidden')
                self.assertEqual(re.findall(r'value="?(\w+)"?>', control), ["light", "dark", "system"])
                self.assertIn(">Oscuro<", (output / "es/index.html").read_text())
                css = self.stylesheet(output)
                self.assertIn(":root[data-appearance=dark]{", css)
                self.assertIn(":root:not([data-appearance=light])", css)
        result, output = self.build("auto-only", '[params.colors]\nappearance = "auto"\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        page = (output / "index.html").read_text()
        self.assertNotIn("localStorage", page)
        self.assertNotIn('class="appearance"', page)
        self.assertIn("prefers-color-scheme:dark", self.stylesheet(output))

    def test_default_brand_colors(self):
        for output, _, _ in self.sites:
            css = self.stylesheet(output)
            for value in ("--ink:#102b4c", "--accent:#2d6089", "--focus:#4075a2", "--rule:#a5bed2"):
                self.assertIn(value, css)

    def test_color_preset_and_override(self):
        result, output = self.build(
            "forest", '[params.colors]\npreset = "forest"\naccent = "#123456"\n'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        css = self.stylesheet(output)
        self.assertIn("--ink:#173a2c", css)
        self.assertIn("--accent:#123456", css)
        self.assertNotIn("#102b4c", css)


    def test_invalid_color_settings_fail_with_the_setting_name(self):
        for name, toml, message in (
            ("bad-preset", '[params.colors]\npreset = "neon"\n', "params.colors.preset"),
            ("bad-value", '[params.colors]\naccent = "blue"\n', "params.colors.accent"),
            ("bad-key", '[params.colors]\nbrand = "#123456"\n', "params.colors.brand"),
        ):
            with self.subTest(name=name):
                result, _ = self.build(name, toml)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

if __name__ == "__main__":
    unittest.main()
