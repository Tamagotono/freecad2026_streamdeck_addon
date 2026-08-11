"""Tests for streamdeck_pages.py

streamdeck_pages.py has no FreeCAD or Qt dependencies so it can be tested
with a plain Python interpreter.  Run from the addon root directory:

    python3 -m pytest tests/ -v
"""

import unittest
from streamdeck_pages import StreamDeckPages


# ---------------------------------------------------------------------------
# Minimal mock objects
# ---------------------------------------------------------------------------

class MockAction:
    """Stand-in for gui_actions.Action"""
    def __init__(self, name, toolbar, enabled=True, iconid=1, title=""):
        self.name = name
        self.toolbar = toolbar
        self.enabled = enabled
        self.iconid = iconid
        self.title = title
        self.islastsubaction = False
        self.issubactionof = None


class MockToolbarActions:
    """Stand-in for gui_actions.ToolbarActions"""
    def __init__(self):
        self.toolbars = []
        self.toolbar_actions = {}
        self.actions = {}
        self.expanded_actions = {}

    def add_toolbar(self, name, action_names):
        self.toolbars.append(name)
        self.toolbar_actions[name] = list(action_names)
        for n in action_names:
            if n not in self.actions:
                self.actions[n] = MockAction(n, name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NB_KEYS = 8  # simulated 8-key Stream Deck throughout

def make_pages(with_nav_keys=True):
    return StreamDeckPages(NB_KEYS, with_nav_keys)

def make_tba(toolbars):
    """toolbars: dict of {toolbar_name: [action_names]}"""
    tba = MockToolbarActions()
    for name, actions in toolbars.items():
        tba.add_toolbar(name, actions)
    return tba

def names_on_page(page, pages):
    """Return the list of action names on a page string."""
    return [pages.parse_key(k).name for k in page.split(pages.SK)]

def names_on_all_pages(pages):
    """Return the set of all action names across every page."""
    result = set()
    for page in pages.pages:
        result.update(names_on_page(page, pages))
    return result


# ---------------------------------------------------------------------------
# parse_key
# ---------------------------------------------------------------------------

class TestParseKey(unittest.TestCase):

    def setUp(self):
        self.pages = make_pages()
        SV = self.pages.SV
        self.ks = SV.join(["tb1", "act1", "1", "42", "TopText", "BotText", "blue", "red"])

    def test_all_fields(self):
        key = self.pages.parse_key(self.ks)
        self.assertEqual(key.toolbar, "tb1")
        self.assertEqual(key.name, "act1")
        self.assertEqual(key.enabled, "1")
        self.assertEqual(key.iconid, "42")
        self.assertEqual(key.toptext, "TopText")
        self.assertEqual(key.bottomtext, "BotText")
        self.assertEqual(key.left_brkt_clr, "blue")
        self.assertEqual(key.right_brkt_clr, "red")

    def test_empty_fields(self):
        SV = self.pages.SV
        key = self.pages.parse_key(SV.join([""] * 8))
        self.assertEqual(key.name, "")
        self.assertEqual(key.left_brkt_clr, "")
        self.assertEqual(key.right_brkt_clr, "")


# ---------------------------------------------------------------------------
# flip
# ---------------------------------------------------------------------------

class TestFlip(unittest.TestCase):

    def setUp(self):
        self.pages = make_pages()
        self.pages.pages = ["p0", "p1", "p2"]
        self.pages.current_page = "p0"
        self.pages.current_page_no = 0
        self.pages.previous_current_page = None

    def test_forward(self):
        self.assertTrue(self.pages.flip(1))
        self.assertEqual(self.pages.current_page_no, 1)
        self.assertEqual(self.pages.current_page, "p1")

    def test_backward(self):
        self.pages.current_page_no = 2
        self.pages.current_page = "p2"
        self.assertTrue(self.pages.flip(-1))
        self.assertEqual(self.pages.current_page_no, 1)

    def test_clamps_at_start(self):
        self.assertFalse(self.pages.flip(-1))
        self.assertEqual(self.pages.current_page_no, 0)

    def test_clamps_at_end(self):
        self.pages.current_page_no = 2
        self.pages.current_page = "p2"
        self.assertFalse(self.pages.flip(1))
        self.assertEqual(self.pages.current_page_no, 2)

    def test_jump_multiple(self):
        self.assertTrue(self.pages.flip(2))
        self.assertEqual(self.pages.current_page_no, 2)


# ---------------------------------------------------------------------------
# rebuild_pages — page structure
# ---------------------------------------------------------------------------

class TestRebuildPagesStructure(unittest.TestCase):

    def test_each_page_has_correct_key_count(self):
        """Every page must have exactly NB_KEYS SK-separated slots."""
        tba = make_tba({"ToolA": ["a1", "a2", "a3"]})
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")

        for page in pages.pages:
            self.assertEqual(len(page.split(pages.SK)), NB_KEYS)

    def test_single_toolbar_fits_on_one_page(self):
        """4 actions + 2 nav slots fit within 8 keys — expect a single page."""
        tba = make_tba({"ToolA": ["a1", "a2", "a3", "a4"]})
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        self.assertEqual(len(pages.pages), 1)

    def test_overflow_creates_multiple_pages(self):
        """10 actions on a 6-slot page (8 keys minus 2 nav) needs 2 pages."""
        actions = ["a{}".format(i) for i in range(10)]
        tba = make_tba({"ToolA": actions})
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        self.assertGreater(len(pages.pages), 1)

    def test_two_toolbars_get_separate_pages(self):
        """Each toolbar gets its own page — ToolA fills then ToolB gets a fresh page."""
        tba = make_tba({"ToolA": ["a1", "a2"], "ToolB": ["b1", "b2"]})
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        self.assertEqual(len(pages.pages), 2)

    def test_no_nav_keys_fills_all_slots(self):
        """With nav keys disabled no PAGEPREV/PAGENEXT should appear."""
        tba = make_tba({"ToolA": ["a1", "a2"]})
        pages = make_pages(with_nav_keys=False)
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")

        all_names = names_on_all_pages(pages)
        self.assertNotIn("PAGEPREV", all_names)
        self.assertNotIn("PAGENEXT", all_names)

    def test_empty_tbactions_produces_no_pages(self):
        tba = make_tba({})
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        self.assertEqual(len(pages.pages), 0)


# ---------------------------------------------------------------------------
# rebuild_pages — action content
# ---------------------------------------------------------------------------

class TestRebuildPagesContent(unittest.TestCase):

    def test_all_actions_appear_on_pages(self):
        actions = ["a{}".format(i) for i in range(10)]
        tba = make_tba({"ToolA": actions})
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")

        all_names = names_on_all_pages(pages)
        for a in actions:
            self.assertIn(a, all_names)

    def test_repeated_toolbar_appears_on_every_page(self):
        """Actions from repeated_toolbars must be present on every page."""
        tba = make_tba({
            "Repeated": ["r1"],
            "ToolA": ["a{}".format(i) for i in range(10)],
        })
        pages = make_pages()
        pages.rebuild_pages(tba, ["Repeated"], "Blue", "Blue", "Red")

        self.assertGreater(len(pages.pages), 1)
        for page in pages.pages:
            self.assertIn("r1", names_on_page(page, pages))

    def test_excluded_toolbar_does_not_appear(self):
        """Toolbars in excluded_toolbars are never passed to rebuild_pages,
        so this tests that a toolbar absent from tba.toolbars is absent from pages."""
        tba = make_tba({"ToolA": ["a1"]})
        # ToolB is simply not in tba — simulates exclusion
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")

        all_names = names_on_all_pages(pages)
        self.assertNotIn("b1", all_names)


# ---------------------------------------------------------------------------
# rebuild_pages — expanded actions (regression tests)
# ---------------------------------------------------------------------------

class TestExpandedActions(unittest.TestCase):

    def test_all_expanded_parents_skips_toolbar(self):
        """Regression: toolbar where every action is an expanded parent must not crash,
        and that toolbar must produce no keys on the Stream Deck."""
        tba = make_tba({
            "ToolA": ["parent1", "parent2"],
            "ToolB": ["b1", "b2"],
        })
        tba.expanded_actions["parent1"] = True  # expanded — becomes invisible
        tba.expanded_actions["parent2"] = True

        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")  # must not raise
        pages.locate_current_page()

        all_names = names_on_all_pages(pages)
        self.assertIn("b1", all_names)
        self.assertNotIn("parent1", all_names)
        self.assertNotIn("parent2", all_names)

    def test_unexpanded_expandable_gets_expand_brackets(self):
        """An expandable action that is not expanded should carry the expand bracket color."""
        tba = make_tba({"ToolA": ["parent"]})
        tba.expanded_actions["parent"] = False  # expandable, but currently collapsed

        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        pages.locate_current_page()

        keys = [pages.parse_key(k) for k in pages.current_page.split(pages.SK)]
        parent_key = next(k for k in keys if k.name == "parent")
        self.assertEqual(parent_key.left_brkt_clr, "red")
        self.assertEqual(parent_key.right_brkt_clr, "red")

    def test_expanded_parent_shifts_subactions_into_its_slot(self):
        """When a parent is expanded its slot is taken by the first sub-item."""
        tba = make_tba({"ToolA": ["parent", "sub1", "sub2", "normal"]})
        tba.expanded_actions["parent"] = True   # expanded — parent is skipped
        tba.expanded_actions["sub1"] = False    # sub1 is a sub-action placeholder
        tba.expanded_actions["sub2"] = False

        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        pages.locate_current_page()

        page_names = names_on_page(pages.current_page, pages)
        self.assertNotIn("parent", page_names)
        self.assertIn("sub1", page_names)
        self.assertIn("sub2", page_names)
        self.assertIn("normal", page_names)


# ---------------------------------------------------------------------------
# locate_current_page
# ---------------------------------------------------------------------------

class TestLocateCurrentPage(unittest.TestCase):

    def test_initial_locate_lands_on_page_zero(self):
        tba = make_tba({"ToolA": ["a1", "a2"]})
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        pages.locate_current_page()

        self.assertEqual(pages.current_page_no, 0)
        self.assertIsNotNone(pages.current_page)

    def test_locate_new_toolbar_jumps_to_its_page(self):
        """Passing new_toolbar should navigate to that toolbar's first page."""
        tba = make_tba({
            "ToolA": ["a{}".format(i) for i in range(10)],
            "ToolB": ["b1"],
        })
        pages = make_pages()
        pages.rebuild_pages(tba, [], "Blue", "Blue", "Red")
        pages.locate_current_page()           # initialize to page 0
        pages.locate_current_page(new_toolbar="ToolB")

        self.assertIn("b1", names_on_page(pages.current_page, pages))

    def test_no_pages_gives_none_current_page(self):
        pages = make_pages()
        pages.rebuild_pages(make_tba({}), [], "Blue", "Blue", "Red")
        pages.locate_current_page()

        self.assertIsNone(pages.current_page)
        self.assertIsNone(pages.current_page_no)


if __name__ == "__main__":
    unittest.main()
