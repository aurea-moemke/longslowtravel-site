import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


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
        self.resources = []

    def handle_data(self, data):
        value = data.strip()
        if value:
            self.text.append(value)

    def handle_starttag(self, _tag, attributes):
        for name, value in attributes:
            if name in {"href", "src"} and value:
                self.resources.append(value)
            if name in {"aria-label", "alt", "title", "placeholder"} and value:
                self.text.append(value)


class PublicIdentityTests(unittest.TestCase):
    def test_local_page_links_assets_and_fragments_resolve(self):
        for page in PUBLIC_PAGES:
            collector = TextCollector()
            collector.feed(page.read_text(encoding="utf-8"))
            for resource in collector.resources:
                url = urlsplit(resource)
                if url.scheme or url.netloc:
                    continue
                with self.subTest(page=page.name, resource=resource):
                    base = ROOT if url.path.startswith("/") else page.parent
                    target = (base / unquote(url.path).lstrip("/")).resolve() if url.path else page
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), str(target))
                    if url.fragment and target.suffix == ".html":
                        self.assertIn(
                            f'id="{unquote(url.fragment)}"',
                            target.read_text(encoding="utf-8"),
                        )

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

    def test_release_guidance_is_present_and_translated(self):
        catalog = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
        offline = (
            "Installed route content and schedules stay on your iPhone for offline use. "
            "Basemap tiles need a separate download in Trail Mode. "
            "Test both in airplane mode before departure."
        )
        required = {
            "home": [offline, "Begin with a curated itinerary or shape your own."],
            "support": [
                offline,
                "Trail Mode shows your location only while the app is open. "
                "It does not provide background tracking or emergency monitoring.",
                "Account → Settings → Delete Account",
                "Your installed route content and schedules remain available offline. "
                "Basemap tiles are separate: open a day’s map, enter Trail Mode, choose "
                "Download, and wait for “Offline map ready for this stage”. "
                "Repeat for each stage you need.",
                "Before departure, turn on airplane mode and turn off Wi-Fi, then check "
                "your routes, schedules, and downloaded stage maps. Downloads cover the "
                "selected stage area, not every map area or zoom level. Sign-in, "
                "purchases, restoration, and sync require an internet connection.",
            ],
        }
        for page, strings in required.items():
            path = ROOT / ("index.html" if page == "home" else "support/index.html")
            collector = TextCollector()
            collector.feed(path.read_text(encoding="utf-8"))
            for source in strings:
                with self.subTest(page=page, source=source):
                    self.assertIn(source, collector.text)
                    for language in SUPPORTED_LANGUAGES[1:]:
                        self.assertTrue(catalog["pages"][page][language].get(source))

        for language in SUPPORTED_LANGUAGES[1:]:
            instructions = catalog["pages"]["support"][language]
            settings_key = next(key for key in instructions if key.startswith("In iPhone Settings,"))
            self.assertIn("LST Camino", instructions[settings_key])
            self.assertNotIn("LST Camino Planner", instructions[settings_key])

    def test_planning_aid_warning_is_preserved_in_every_language(self):
        support = (ROOT / "support/index.html").read_text(encoding="utf-8")
        source = (
            "LST Camino Planner is a planning aid, not an emergency or navigation service. "
            "For urgent help, contact local emergency services. In Spain and across the EU, call"
        )
        catalog = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
        self.assertIn(source, support)
        self.assertIn('href="tel:112">112</a>', support)
        for language in SUPPORTED_LANGUAGES[1:]:
            self.assertTrue(catalog["pages"]["support"][language].get(source))

    def test_privacy_matches_current_deployed_features(self):
        privacy = (ROOT / "privacy/index.html").read_text(encoding="utf-8")
        self.assertIn("Hosts the production account API", privacy)
        self.assertIn("information is stored", privacy)
        self.assertNotIn("Will host", privacy)
        self.assertNotIn("When production account services are enabled", privacy)
        self.assertNotIn("will be stored", privacy)
        self.assertIn("accommodations you mark as favourites", privacy)
        self.assertIn("lst-site-language", privacy)
        self.assertIn("clear this website’s data", privacy)
        self.assertIn("Account → Settings → Delete Account", privacy)
        self.assertIn("Trail Mode shows your location only while the app is open", privacy)
        self.assertIn("Bavarian State Office for Data Protection Supervision", privacy)

    def test_marketing_does_not_claim_proven_routes_or_no_telemetry(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        privacy = (ROOT / "privacy/index.html").read_text(encoding="utf-8")
        catalog = (ROOT / "translations.json").read_text(encoding="utf-8")
        self.assertNotIn("proven stage pattern", home + catalog)
        self.assertNotIn("No ads or tracking", home + catalog)
        self.assertNotIn("<b>No tracking</b>", privacy)
        self.assertIn("Mapbox", privacy)
        self.assertIn("telemetry", privacy)

    def test_legal_content_keeps_its_actual_language(self):
        for page, language in (("privacy", "en"), ("imprint", "de")):
            source = (ROOT / page / "index.html").read_text(encoding="utf-8")
            self.assertEqual(source.count(f'data-no-translate lang="{language}"'), 2)
        script = (ROOT / "script.js").read_text(encoding="utf-8")
        self.assertGreater(
            script.index("document.documentElement.lang = language"),
            script.index("const catalog = await response.json()"),
        )

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
