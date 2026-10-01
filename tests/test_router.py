import unittest
from assistant.command_router import CommandRouter

class TestCommandRouter(unittest.TestCase):
    def setUp(self):
        self.router = CommandRouter()

    def test_open_app_routing(self):
        res = self.router.route("Open Chrome")
        self.assertIsNotNone(res)
        self.assertTrue(res["matched"])
        self.assertEqual(res["plan"][0]["tool"], "open_application")
        self.assertEqual(res["plan"][0]["args"]["app_name"], "chrome")

    def test_type_text_routing(self):
        res = self.router.route("Type YouTube")
        self.assertIsNotNone(res)
        self.assertTrue(res["matched"])
        self.assertEqual(res["plan"][0]["tool"], "type_text")
        self.assertEqual(res["plan"][0]["args"]["text"], "YouTube")

    def test_press_key_routing(self):
        res = self.router.route("Press enter")
        self.assertIsNotNone(res)
        self.assertTrue(res["matched"])
        self.assertEqual(res["plan"][0]["tool"], "press_key")
        self.assertEqual(res["plan"][0]["args"]["key"], "enter")

    def test_hotkey_routing(self):
        res = self.router.route("Press Ctrl L")
        self.assertIsNotNone(res)
        self.assertTrue(res["matched"])
        self.assertEqual(res["plan"][0]["tool"], "hotkey")

    def test_search_web_routing(self):
        res = self.router.route("Search YouTube for Java DSA")
        self.assertIsNotNone(res)
        self.assertTrue(res["matched"])
        self.assertEqual(res["plan"][0]["tool"], "search_web")
        self.assertEqual(res["plan"][0]["args"]["query"], "Java DSA")

    def test_compound_command_routing(self):
        res = self.router.route("Open Chrome and search YouTube for Java binary search")
        self.assertIsNotNone(res)
        self.assertTrue(res["matched"])
        self.assertEqual(len(res["plan"]), 2)
        self.assertEqual(res["plan"][0]["tool"], "open_application")
        self.assertEqual(res["plan"][1]["tool"], "search_web")


if __name__ == "__main__":
    unittest.main()
