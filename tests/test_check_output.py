"""Regression tests for tests/check_output.py. Standard library only.

    python3 -m unittest discover -s tests -p "test_*.py"

Each test class covers one validator bug found in the ChatGPT Work
behavior reports for 1.1.0, and checks both directions: what the fix lets
through, and what must still fail.
"""

import importlib.util
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("check_output", TESTS / "check_output.py")
co = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(co)

CASE01 = co.load_case(TESTS / "cases" / "01-he-agency-pasted")
CASE02 = co.load_case(TESTS / "cases" / "02-en-dead-controls-live")
CASE03 = co.load_case(TESTS / "cases" / "03-en-dead-controls-screenshot")


def report(fix_lines, lock_lines, basis="Basis: pasted copy; not checked: layout, whether anything works"):
    fixes = "\n".join(f"{i}. {line}" for i, line in enumerate(fix_lines, 1))
    locks = "\n".join(f"- {line}" for line in lock_lines)
    return (
        f"# Reality Check - Example\n{basis}\n\n## Verdict\nOnly after 3 fixes\n\nOne sentence why.\n\n"
        f"## Top 3 fixes\n{fixes}\n\n## Do not touch\n{locks}\n\n## Why\nLine one.\nLine two.\n"
    )


GOOD_FIXES = [
    "[observed] Headline has no noun - visitors cannot tell what is sold - use the noun already in the catalog.",
    "[observed] Two equal CTAs - visitors do not know the next step - choose one primary business action.",
    "[observed] Claim with no evidence - it reads as filler - connect it to evidence or remove it.",
]


def hard_of(text, case=None):
    return co.check_output(text, case)[0]


class SeparatorTests(unittest.TestCase):
    """Reports A and B: em dashes failed every fix and lock line although all three parts were there."""

    def test_hyphen_en_dash_and_em_dash_all_pass(self):
        for dash in ("-", "–", "—"):
            fixes = [f.replace(" - ", f" {dash} ") for f in GOOD_FIXES]
            self.assertEqual(hard_of(report(fixes, [f"Catalog {dash} the only concrete list"])), [], dash)

    def test_hebrew_report_with_em_dash_passes(self):
        text = (TESTS / "cases" / "05-he-clear-product-pasted" / "alt-em-dash.md").read_text(encoding="utf-8")
        self.assertIn("—", text)
        self.assertEqual(hard_of(text), [])

    def test_colon_or_comma_instead_of_dashes_still_fails(self):
        fixes = [f.replace(" - ", ": ", 1).replace(" - ", ", ") for f in GOOD_FIXES]
        problems = hard_of(report(fixes, ["Catalog: the only concrete list"]))
        self.assertEqual(sum("what - why it hurts - how" in p for p in problems), 3)
        self.assertTrue(any("element - why lock it" in p for p in problems))

    def test_one_dash_is_not_enough(self):
        fixes = [f.rsplit(" - ", 1)[0] for f in GOOD_FIXES]
        self.assertEqual(sum("what - why it hurts - how" in p for p in hard_of(report(fixes, ["Catalog - list"]))), 3)

    def test_hyphenated_words_are_not_separators(self):
        fixes = ["[observed] Above-the-fold copy is generic-looking and one-size-fits-all."] + GOOD_FIXES[1:]
        self.assertTrue(any("what - why it hurts - how" in p for p in hard_of(report(fixes, ["Catalog - list"]))))


class NegationTests(unittest.TestCase):
    """Report A: 'nothing in this screenshot proves that it is fake' was flagged as claiming it is fake."""

    def test_denial_and_condition_are_not_claims(self):
        self.assertFalse(co.asserts("Nothing in this screenshot proves that it is fake or that any button is broken.", "is fake"))
        self.assertFalse(co.asserts("If it is dead, the page fails at the moment of intent.", "is dead"))
        self.assertFalse(co.asserts("We cannot tell whether the panel is static.", "is static"))

    def test_plain_claims_are_still_flagged(self):
        self.assertTrue(co.asserts("The LIVE panel is fake.", "is fake"))
        self.assertTrue(co.asserts("The panel is not connected; it is static.", "is static"))
        self.assertTrue(co.asserts("Nothing loads, but the button is dead.", "is dead"))

    def test_case03_warns_only_on_the_claim(self):
        quoted = "Nothing in this screenshot proves that it is fake or that any button is broken."
        claim = "The LIVE panel is fake."
        _, soft_quoted, _ = co.check_output(report(GOOD_FIXES, ["Catalog - list"], "Basis: screenshot; not checked: buttons") + quoted, CASE03)
        _, soft_claim, _ = co.check_output(report(GOOD_FIXES, ["Catalog - list"], "Basis: screenshot; not checked: buttons") + claim, CASE03)
        self.assertFalse(any("is fake" in s for s in soft_quoted))
        self.assertTrue(any("is fake" in s for s in soft_claim))


class Case03AssumedTests(unittest.TestCase):
    """Report B: case 03 demanded an [assumed] fix that SKILL.md does not require."""

    def test_observed_only_screenshot_answer_passes(self):
        text = (TESTS / "cases" / "03-en-dead-controls-screenshot" / "alt-observed-only.md").read_text(encoding="utf-8")
        hard, soft, info = co.check_output(text, CASE03)
        self.assertEqual((hard, soft, info["status"]), ([], [], "PASS"))
        self.assertNotIn("assumed", info["tags"])

    def test_verified_tag_on_a_screenshot_still_fails(self):
        text = (TESTS / "cases" / "03-en-dead-controls-screenshot" / "alt-observed-only.md").read_text(encoding="utf-8")
        text = text.replace("1. [observed]", "1. [verified]", 1)
        self.assertIn("case forbids the [verified] tag with this input", hard_of(text, CASE03))


class NotCheckedTests(unittest.TestCase):
    """Report B: a report with no 'not checked' clause on the Basis line passed."""

    def test_report_without_clause_fails_in_both_languages(self):
        self.assertTrue(any("not checked" in p for p in hard_of(report(GOOD_FIXES, ["Catalog - list"], "Basis: pasted copy"))))
        text = (TESTS / "cases" / "01-he-agency-pasted" / "counterexample-no-not-checked.md").read_text(encoding="utf-8")
        self.assertTrue(any("לא נבדק" in p for p in hard_of(text)))

    def test_clause_needs_content(self):
        self.assertTrue(hard_of(report(GOOD_FIXES, ["Catalog - list"], "Basis: pasted copy; not checked:")))

    def test_accepted_wordings(self):
        for basis in ("Basis: screenshot; not checked: buttons", "Basis: screenshot; not tested: buttons", "Basis: screenshot. Not verified: buttons"):
            self.assertEqual(hard_of(report(GOOD_FIXES, ["Catalog - list"], basis)), [], basis)

    def test_stop_output_does_not_need_the_clause(self):
        text = (TESTS / "contract-samples" / "valid-stop-unreachable.md").read_text(encoding="utf-8")
        self.assertEqual(hard_of(text), [])


class BlockedTests(unittest.TestCase):
    """Reports A and B: case 02 without a working browser was scored FAIL; it is BLOCKED, never PASS."""

    def status(self, text):
        return co.check_output(text, CASE02)[2]["status"]

    def test_unreachable_page_is_blocked(self):
        text = (TESTS / "cases" / "02-en-dead-controls-live" / "blocked-unreachable.md").read_text(encoding="utf-8")
        self.assertEqual(self.status(text), "BLOCKED")

    def test_read_only_report_is_blocked(self):
        expected = (TESTS / "cases" / "02-en-dead-controls-live" / "expected.md").read_text(encoding="utf-8")
        read_only = expected.replace("live page, interacted", "live page, read only").replace("[verified]", "[observed]")
        self.assertEqual(self.status(read_only), "BLOCKED")

    def test_contract_break_is_fail_not_blocked(self):
        self.assertEqual(self.status("# Reality Check - x\nNot diagnosed: could not load."), "FAIL")

    def test_interacted_runs_are_still_judged(self):
        expected = (TESTS / "cases" / "02-en-dead-controls-live" / "expected.md").read_text(encoding="utf-8")
        counter = (TESTS / "cases" / "02-en-dead-controls-live" / "counterexample-invented-number.md").read_text(encoding="utf-8")
        self.assertEqual(self.status(expected), "PASS")
        self.assertEqual(self.status(counter), "FAIL")

    def test_other_cases_never_report_blocked(self):
        text = (TESTS / "contract-samples" / "valid-stop-unreachable.md").read_text(encoding="utf-8")
        self.assertEqual(co.check_output(text, CASE01)[2]["status"], "FAIL")


class BasisNameTests(unittest.TestCase):
    """Final 19f49f7 run: case 04 wrote "live page, text fetch only", the skill's own
    input-table name for "live page, read only", and was scored FAIL."""

    CASE04 = co.load_case(TESTS / "cases" / "04-en-spa-shell")

    def test_case04_original_output_passes(self):
        text = (TESTS / "cases" / "04-en-spa-shell" / "alt-text-fetch-only.md").read_text(encoding="utf-8")
        self.assertIn("live page, text fetch only", text)
        hard, soft, info = co.check_output(text, self.CASE04)
        self.assertEqual((hard, soft, info["status"]), ([], [], "PASS"))

    def test_every_table_name_is_accepted_in_both_languages(self):
        for lang in ("en", "he"):
            lab = co.LABELS[lang]
            for i, names in enumerate(lab["basis_aliases"]):
                for name in names:
                    self.assertTrue(co.names_input(f"{lab['basis_prefix']} {name.capitalize()}; x", lab, [i]), name)

    def test_unknown_or_vague_names_still_fail(self):
        for basis in ("Basis: live page; not checked: buttons", "Basis: I looked at it; not checked: buttons", "Basis: web page; not checked: buttons"):
            self.assertTrue(any("must name the input" in p for p in hard_of(report(GOOD_FIXES, ["Catalog - list"], basis))), basis)

    def test_a_read_only_name_does_not_count_as_interacted(self):
        expected = (TESTS / "cases" / "02-en-dead-controls-live" / "expected.md").read_text(encoding="utf-8")
        text_fetch = expected.replace("live page, interacted", "live page, text fetch only").replace("[verified]", "[observed]")
        clicked = expected.replace("live page, interacted", "live page, rendered and clicked")
        self.assertEqual(co.check_output(text_fetch, CASE02)[2]["status"], "BLOCKED")
        self.assertEqual(co.check_output(clicked, CASE02)[2]["status"], "PASS")

    def test_case04_still_rejects_a_screenshot_basis(self):
        text = (TESTS / "cases" / "04-en-spa-shell" / "alt-text-fetch-only.md").read_text(encoding="utf-8")
        text = text.replace("live page, text fetch only", "screenshot")
        self.assertIn("case expects basis ['live page, read only']", hard_of(text, self.CASE04))


if __name__ == "__main__":
    unittest.main()
