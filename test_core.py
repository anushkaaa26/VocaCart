import unittest
from shopping_agent import _rule_parse, execute_command, render_response
from database import get_shopping_list, remove_from_list, clear_completed


class CommandParserTests(unittest.TestCase):
    def test_multi_add(self):
        parsed = _rule_parse("Add 5 apples and 2 bottles of water")
        self.assertEqual(parsed["intent"], "add")
        self.assertEqual(len(parsed["commands"]), 2)
        self.assertEqual(parsed["commands"][0]["quantity"], 5)
        self.assertEqual(parsed["commands"][1]["unit"], "bottles")

    def test_correction(self):
        parsed = _rule_parse("Actually make that 3", "Classic Milk")
        self.assertEqual(parsed["intent"], "update")
        self.assertEqual(parsed["commands"][0]["item"], "Classic Milk")
        self.assertEqual(parsed["commands"][0]["quantity"], 3)

    def test_budget(self):
        parsed = _rule_parse("Set my budget to $25")
        self.assertEqual(parsed["intent"], "budget")
        self.assertEqual(parsed["budget"], 25)

    def test_search_filters(self):
        parsed = _rule_parse("Find organic honey under $20 with 4+ stars")
        self.assertEqual(parsed["intent"], "search")
        self.assertEqual(parsed["max_price"], 20)
        self.assertEqual(parsed["min_rating"], 4)
        self.assertTrue(parsed["organic"])

    def test_hinglish(self):
        parsed = _rule_parse("2 litre doodh aur 5 kele add karo")
        self.assertEqual(parsed["intent"], "add")
        self.assertEqual(len(parsed["commands"]), 2)


class ExecuteCommandIntegrationTests(unittest.TestCase):
    """Exercises the full pipeline (parse -> resolve -> SQLite) end to end,
    against the real store.db. GROQ_API_KEY is intentionally unset in CI/test
    runs so this also verifies the deterministic rule-based fallback path
    that ships without any API key configured."""

    def tearDown(self):
        # Clean up anything this test class added so the suite is repeatable.
        for name in ["Fresh Apples", "Drinking Water"]:
            remove_from_list(name)
        clear_completed()

    def test_add_then_remove_round_trip(self):
        result = execute_command("Add 3 apples and 1 bottle of water")
        self.assertEqual(result["intent"], "add")
        self.assertEqual(len(result["items"]), 2)
        names = {i["item_name"] for i in result["items"]}
        self.assertIn("Fresh Apples", names)

        active = {i["item_name"] for i in get_shopping_list()}
        self.assertIn("Fresh Apples", active)

        removed = execute_command("Remove apples from my list")
        self.assertEqual(removed["intent"], "remove")
        active_after = {i["item_name"] for i in get_shopping_list()}
        self.assertNotIn("Fresh Apples", active_after)

    def test_search_returns_rated_products(self):
        result = execute_command("Find organic honey under $20 with 4+ stars")
        self.assertEqual(result["intent"], "search")
        self.assertTrue(result["products"])
        for p in result["products"]:
            self.assertGreaterEqual(p["average_rating"], 4.0)
            self.assertLessEqual(p["price"], 20)
            self.assertTrue(p["is_organic"])

    def test_unknown_command_has_helpful_response(self):
        result = execute_command("asdkjaslkdjaslkd nonsense")
        response = render_response(result)
        self.assertIn("add, remove, update, search", response)


if __name__ == "__main__":
    unittest.main()
