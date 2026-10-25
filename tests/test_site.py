"""Build and inspect real Hugo output without third-party dependencies."""

import json
import os
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
        override.write_text('[params]\nimages = ["images/portrait.svg"]\n')
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
        bundle = Page(self.default_site / "blog/building-this-theme/index.html")
        self.assertEqual(
            bundle.value("og:image"),
            "https://example.test/theme-demo/blog/building-this-theme/cover.png",
        )

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
                self.assertEqual(len(entries), 17)
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


if __name__ == "__main__":
    unittest.main()
