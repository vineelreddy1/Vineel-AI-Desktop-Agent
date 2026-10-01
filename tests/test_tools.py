import unittest
from tools import TOOL_REGISTRY, get_tool, execute_tool
from computer.applications import find_executable_path

class TestToolRegistry(unittest.TestCase):
    def test_registered_tools(self):
        expected_tools = [
            "open_application", "close_application", "type_text", 
            "press_key", "hotkey", "open_url", "search_web", 
            "list_windows", "take_screenshot"
        ]
        for t in expected_tools:
            self.assertIn(t, TOOL_REGISTRY)

    def test_app_path_resolution(self):
        path = find_executable_path("chrome")
        self.assertIsNotNone(path)

    def test_tool_schema_structure(self):
        tool = get_tool("open_application")
        self.assertEqual(tool["name"], "open_application")
        self.assertIn("app_name", tool["parameters"]["properties"])
        self.assertEqual(tool["risk_level"], "LOW")


if __name__ == "__main__":
    unittest.main()
