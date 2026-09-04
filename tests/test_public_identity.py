import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = (
    ROOT / "index.html",
    ROOT / "support" / "index.html",
    ROOT / "privacy" / "index.html",
    ROOT / "imprint" / "index.html",
)


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


if __name__ == "__main__":
    unittest.main()
