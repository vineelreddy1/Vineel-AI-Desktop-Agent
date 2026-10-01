import unittest
from assistant.planner import Planner

class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = Planner()

    def test_mock_multi_step_plan(self):
        cmd = "Open Chrome, go to YouTube, search for Java DSA, and press enter"
        plan = self.planner.plan(cmd)
        self.assertIsInstance(plan, list)
        self.assertGreaterEqual(len(plan), 3)
        self.assertEqual(plan[0]["tool"], "open_application")
        self.assertEqual(plan[1]["tool"], "open_url")


if __name__ == "__main__":
    unittest.main()
