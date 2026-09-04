import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = (
    ROOT / "index.html",
    ROOT / "support" / "index.html",
    ROOT / "privacy" / "index.html",
    ROOT / "imprint" / "index.html",
)
SUPPORTED_LANGUAGES = ("en", "de", "es", "fr", "it", "pt")


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        value = data.strip()
        if value:
            self.text.append(value)

    def handle_starttag(self, _tag, attributes):
        for name, value in attributes:
            if name in {"aria-label", "alt", "title", "placeholder"} and value:
                self.text.append(value)


class PublicIdentityTests(unittest.TestCase):
    def test_public_pages_use_the_canonical_product_and_publisher_names(self):
        for path in PUBLIC_PAGES:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn("LST Camino Planner", text)
                self.assertIn("Long Slow Travel", text)
                self.assertNotRegex(text, re.compile(r"(?<!LST )Camino Planner"))
                self.assertNotIn("LSTCamino", text)

    def test_iphone_settings_uses_the_installed_app_name(self):
        support = (ROOT / "support" / "index.html").read_text(encoding="utf-8")
        privacy = (ROOT / "privacy" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Location Services → LST Camino", support)
        self.assertIn("change LST Camino’s location permission", privacy)

    def test_multilingual_catalog_is_complete_for_public_content(self):
        catalog = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))

        self.assertEqual(tuple(catalog["languages"]), SUPPORTED_LANGUAGES)
        for language in SUPPORTED_LANGUAGES:
            self.assertIn(language, catalog["ui"])
            self.assertIn(language, catalog["shared"])
            for page in ("home", "support", "privacy", "imprint"):
                self.assertIn(language, catalog["metadata"][page])

        for page, relative_path in (("home", "index.html"), ("support", "support/index.html")):
            localized = catalog["pages"][page]
            expected_keys = set(localized["de"])
            self.assertTrue(expected_keys)
            for language in SUPPORTED_LANGUAGES[1:]:
                with self.subTest(page=page, language=language):
                    self.assertEqual(set(localized[language]), expected_keys)
                    self.assertTrue(all(localized[language].values()))

            collector = TextCollector()
            collector.feed((ROOT / relative_path).read_text(encoding="utf-8"))
            self.assertEqual(expected_keys - set(collector.text), set())

    def test_language_picker_preserves_choice_and_has_safe_fallback(self):
        script = (ROOT / "script.js").read_text(encoding="utf-8")

        self.assertIn('const supportedLanguages = ["en", "de", "es", "fr", "it", "pt"]', script)
        self.assertIn('window.localStorage.setItem("lst-site-language"', script)
        self.assertIn('new URLSearchParams(window.location.search).get("lang")', script)
        self.assertIn('|| "en"', script)
        self.assertIn('alternate.hreflang = code', script)

        expected_pages = {
            "index.html": 'data-page="home"',
            "support/index.html": 'data-page="support"',
            "privacy/index.html": 'data-page="privacy" data-source-language="en"',
            "imprint/index.html": 'data-page="imprint" data-source-language="de"',
        }
        for relative_path, marker in expected_pages.items():
            with self.subTest(path=relative_path):
                self.assertIn(marker, (ROOT / relative_path).read_text(encoding="utf-8"))

    def test_developer_history_is_present_and_localized(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        catalog = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
        source = (
            "Built by Aurea Moemke, creator of Camino Pilgrim—the free Android "
            "Camino companion available from 2014 to 2025."
        )

        self.assertIn(source, home)
        self.assertIn("assets/camino-pilgrim-icon.png", home)
        icon = ROOT / "assets" / "camino-pilgrim-icon.png"
        self.assertTrue(icon.is_file())
        self.assertEqual(icon.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertNotIn("developer-story-mark", home)
        for language in SUPPORTED_LANGUAGES[1:]:
            with self.subTest(language=language):
                translation = catalog["pages"]["home"][language][source]
                self.assertIn("Aurea Moemke", translation)
                self.assertIn("Camino Pilgrim", translation)
                self.assertRegex(translation, r"2014.*2025")

    def test_route_library_names_every_current_walking_route_pack(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        expected_route_packs = (
            "Sarria to Santiago",
            "Camino Francés",
            "Camino Finisterre",
            "Camino Português",
        )

        for route in expected_route_packs:
            with self.subTest(route=route):
                self.assertIn(f"<h3>{route}</h3>", home)

        self.assertIn("<strong>Central Route</strong>", home)
        self.assertIn("<strong>Coastal Route</strong>", home)
        self.assertNotIn("<h3>Camino Português Central</h3>", home)
        self.assertNotIn("<h3>Camino Português Coastal</h3>", home)
        self.assertEqual(home.count("One-time purchase"), 3)
        self.assertNotIn("More ways to Santiago", home)
        self.assertNotIn("GROWING LIBRARY", home)

    def test_home_page_uses_the_supplied_real_app_screenshots(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        screenshots = (
            "lst-camino-journeys.png",
            "lst-camino-routes.png",
            "lst-camino-template-create.png",
            "lst-camino-itinerary-map.png",
            "lst-camino-itinerary-days-current.png",
            "lst-camino-elevation-profile-current.png",
            "lst-camino-my-schedule.png",
        )

        for filename in screenshots:
            with self.subTest(filename=filename):
                asset = ROOT / "assets" / filename
                self.assertIn(f'assets/{filename}', home)
                self.assertTrue(asset.is_file())
                self.assertGreater(asset.stat().st_size, 100_000)
                self.assertEqual(asset.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

        self.assertNotIn("route-window app-screen", home)
        self.assertNotIn("assets/lst-camino-day-map.png", home)
        self.assertEqual(home.count('class="screen-frame"'), len(screenshots))

    def test_feature_cards_do_not_imitate_app_screens(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        stylesheet = (ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertNotIn("mini-stage-list", home)
        self.assertNotIn("profile-art", home)
        self.assertNotIn("Downloaded and ready", home)
        self.assertNotIn(".mini-stage-list", stylesheet)
        self.assertNotIn(".profile-art", stylesheet)
        self.assertNotIn(".offline-chip", stylesheet)

    def test_screenshot_frames_crop_simulator_edges(self):
        stylesheet = (ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn(".screen-frame", stylesheet)
        self.assertIn("overflow: hidden", stylesheet)
        self.assertIn("width: calc(100% + 10px)", stylesheet)
        self.assertIn("margin: -5px", stylesheet)
        self.assertNotRegex(
            stylesheet,
            r"(?:journeys-capture|route-capture)[^}]*transform:",
        )
        self.assertNotRegex(
            stylesheet,
            r"screen-shot[^}]*screen-frame[^}]*transform:",
        )

    def test_unreviewed_legal_translations_are_not_presented_as_authoritative(self):
        privacy = (ROOT / "privacy" / "index.html").read_text(encoding="utf-8")
        imprint = (ROOT / "imprint" / "index.html").read_text(encoding="utf-8")
        catalog = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))

        self.assertIn('data-source-language="en"', privacy)
        self.assertIn('data-source-language="de"', imprint)
        self.assertIn("data-language-notice", privacy)
        self.assertIn("data-language-notice", imprint)
        self.assertGreaterEqual(privacy.count("data-no-translate"), 2)
        self.assertGreaterEqual(imprint.count("data-no-translate"), 2)
        for language in SUPPORTED_LANGUAGES:
            self.assertTrue(catalog["ui"][language]["legalNotices"]["privacy"])
            self.assertTrue(catalog["ui"][language]["legalNotices"]["imprint"])

    def test_complaint_right_uses_clear_gdpr_article_77_wording(self):
        privacy = (ROOT / "privacy" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Lodge a complaint:", privacy)
        self.assertIn("where you usually live or work", privacy)
        self.assertIn("where you believe the infringement occurred", privacy)
        self.assertNotIn("responsible for Long Slow Travel or", privacy)

    def test_privacy_contact_callout_does_not_repeat_personal_address(self):
        privacy = (ROOT / "privacy" / "index.html").read_text(encoding="utf-8")
        contact = privacy.split('<section id="contact"', 1)[1].split("</section>", 1)[0]

        self.assertIn("contact Long Slow Travel by email", contact)
        self.assertIn("support@longslowtravel.com", contact)
        self.assertNotIn("Aurea Moemke", contact)
        self.assertNotIn("Römerstädter", contact)
        self.assertNotIn("86199", contact)


if __name__ == "__main__":
    unittest.main()
