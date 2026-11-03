"""Check a Reality Check output against the output contract. Standard library only.

Check one agent output, optionally against a regression case:

    python3 tests/check_output.py my-run.md --case tests/cases/03-en-dead-controls-screenshot

Check every case and contract sample:

    python3 tests/check_output.py --all

In a case folder, expected.md and alt-*.md must pass with no warnings,
counterexample-*.md must fail, and blocked-*.md must come out BLOCKED.
In tests/contract-samples, valid-*.md must pass and invalid-*.md must fail.

Statuses: PASS (exit 0); FAIL (exit 1), a contract break or a mechanical case
expectation; BLOCKED (exit 2), a case that needs a live interaction the
agent's environment could not provide. BLOCKED never counts as a pass. WARN
lines are wording an agent may legitimately phrase differently, worth a
human look.
"""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TESTS = Path(__file__).resolve().parent
CONTRACT = json.loads((TESTS / "contract.json").read_text(encoding="utf-8"))
LABELS = CONTRACT["labels"]

# The template writes "what - why - how" with a hyphen. Agents often typeset it as an
# en or em dash; the parts are what the contract needs, so any spaced dash counts.
# Colons, commas, or no separator still fail.
SEPARATOR = re.compile(r"\s[-\u2013\u2014]\s")
# Words before a phrase that make it a denial or a condition, not a claim:
# "nothing proves that it is fake", "if it is dead".
NOT_A_CLAIM = re.compile(r"\b(not|no|nothing|never|cannot|can't|isn't|doesn't|without|whether|if|unless|nor)\b|(^|\s)(לא|אין|אם)(?=\s)", re.I)


def asserts(text, phrase):
    """True when phrase appears in a clause with no denial or condition before it."""
    phrase = phrase.lower()
    for clause in re.split(r"[.;!?\n]|\bbut\b", text, flags=re.I):
        low = clause.lower()
        start = low.find(phrase)
        while start != -1:
            if not NOT_A_CLAIM.search(clause[:start]):
                return True
            start = low.find(phrase, start + 1)
    return False


def names_input(basis, lab, indices=None):
    """True when the basis names one of the inputs at `indices` (default: any input).

    SKILL.md names each input twice: the template value ("live page, read only")
    and its input-table row ("Live page, text fetch only"). Both count.
    """
    low = basis.lower()
    for i in (range(len(lab["basis_values"])) if indices is None else indices):
        if any(name.lower() in low for name in [lab["basis_values"][i]] + lab["basis_aliases"][i]):
            return True
    return False


def not_checked_clause(basis, lab):
    """True when the basis line says what was not checked, followed by some content."""
    variants = "|".join(re.escape(v) for v in lab["not_checked_variants"])
    return re.search(rf"({variants})[^\s:]*\s*:?\s*[^\s:]", basis, re.I) is not None


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        for name, value in attrs:
            if name in ("alt", "title", "placeholder", "aria-label") and value:
                self.parts.append(value)

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def source_text(paths):
    chunks = []
    for path in paths:
        raw = path.read_text(encoding="utf-8")
        if path.suffix == ".html":
            parser = _Text()
            parser.feed(raw)
            raw = " ".join(parser.parts)
        chunks.append(raw)
    return "\n".join(chunks)


def numbers_in(text):
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text)}


def detect_language(text):
    he = LABELS["he"]
    if any(h in text for h in [he["basis_prefix"], he["stop"]] + ["## " + x for x in he["headings"]]):
        return "he"
    return "en"


def split_sections(lines):
    sections, current = {}, None
    for line in lines:
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def check_output(text, case=None):
    """Return (hard_problems, soft_problems, info)."""
    hard, soft = [], []
    lang = detect_language(text)
    lab = LABELS[lang]
    lines = [line.rstrip() for line in text.strip().splitlines()]
    nonempty = [line for line in lines if line.strip()]
    info = {"language": lang}

    if not nonempty or not nonempty[0].startswith("# Reality Check"):
        hard.append("first line must be '# Reality Check - [site or URL]'")
    basis = next((line for line in nonempty[:3] if line.startswith(lab["basis_prefix"])), None)
    headings = [line for line in lines if re.match(r"^#{1,6} ", line)]
    is_stop = any(line.startswith(lab["stop"]) for line in nonempty)
    info["basis"] = basis
    info["outcome"] = "stop" if is_stop else "report"
    if basis is None:
        hard.append(f"missing '{lab['basis_prefix']}' line right under the title")
    elif is_stop:
        # The stop template is "Basis: [what was received]": an unreachable URL or a login wall is free text.
        if not basis[len(lab["basis_prefix"]):].strip():
            hard.append("stop output must say what was received on the basis line")
    else:
        if not names_input(basis, lab):
            hard.append(f"basis line must name the input: one of {lab['basis_values']}")
        if not not_checked_clause(basis, lab):
            hard.append(f"basis line must say what was not checked ('{lab['not_checked']} ...')")

    if is_stop:
        if len(headings) != 1:
            hard.append("stop output must have no sections, only the title")
        for verdict in lab["verdicts"].values():
            if verdict in text:
                hard.append(f"stop output must not give a verdict ('{verdict}')")
        tags_used = []
    else:
        expected = ["## " + h for h in lab["headings"]]
        found = [h for h in headings if h.startswith("## ")]
        if found != expected:
            hard.append(f"sections must be exactly {expected}, found {found}")
        extra = [h for h in headings if not h.startswith("## ") and not h.startswith("# Reality Check")]
        if extra:
            hard.append(f"no other headings allowed: {extra}")
        sections = split_sections(lines)

        verdict_lines = [line.strip().strip("*").strip() for line in sections.get(lab["headings"][0], []) if line.strip()]
        verdict = verdict_lines[0] if verdict_lines else ""
        if verdict not in lab["verdicts"].values():
            hard.append(f"verdict must be exactly one of {list(lab['verdicts'].values())}, found '{verdict}'")
        if len(verdict_lines) != 2:
            hard.append("verdict section must hold the verdict line and one sentence why")
        info["verdict"] = verdict

        fixes = [line for line in sections.get(lab["headings"][1], []) if line.strip()]
        numbered = [line for line in fixes if re.match(r"^\d+\. ", line)]
        if [line.split(".", 1)[0] for line in numbered] != ["1", "2", "3"] or len(numbered) != len(fixes):
            hard.append(f"fixes section must be exactly three numbered lines 1-3, found {len(numbered)} numbered of {len(fixes)} lines")
        tag_by_value = {v: k for k, v in lab["tags"].items()}
        tags_used = []
        for line in numbered:
            content = line.split(". ", 1)[1].strip()
            if content == lab["empty_slot"]:
                if verdict != lab["verdicts"]["ship"]:
                    hard.append(f"'{lab['empty_slot']}' is allowed only under '{lab['verdicts']['ship']}'")
                continue
            tag = next((v for v in lab["tags"].values() if content.startswith(v)), None)
            if tag is None:
                hard.append(f"fix must start with an evidence tag {list(lab['tags'].values())}: '{content[:60]}'")
                continue
            tags_used.append(tag_by_value[tag])
            if len(SEPARATOR.findall(content)) < 2:
                hard.append(f"fix must read 'what - why it hurts - how': '{content[:60]}'")
            if tag_by_value[tag] == "assumed" and not any(w in content.lower() for w in lab["check_words"]):
                hard.append(f"an assumed fix must be phrased as a check ({lab['check_words']}): '{content[:60]}'")

        locked = [line for line in sections.get(lab["headings"][2], []) if line.strip()]
        bullets = [line for line in locked if line.startswith("- ")]
        if not 1 <= len(bullets) <= 3 or len(bullets) != len(locked):
            hard.append(f"'{lab['headings'][2]}' must hold 1-3 bullet lines, found {len(bullets)} of {len(locked)} lines")
        for line in bullets:
            if not SEPARATOR.search(line[2:]):
                hard.append(f"locked element must read 'element - why lock it': '{line[:60]}'")

        why = [line for line in sections.get(lab["headings"][3], []) if line.strip()]
        if not 2 <= len(why) <= 4:
            hard.append(f"'{lab['headings'][3]}' must be 2-4 lines, found {len(why)}")

        if re.search(r"\b\d+\s*/\s*(5|10|100)\b", text) or re.search(r"\bscore:|ציון:", text, re.I):
            hard.append("no module scores")
        if lab["verdicts"]["no"] == verdict and tags_used and set(tags_used) == {"assumed"}:
            hard.append(f"'{verdict}' cannot rest on assumptions alone")
    info["tags"] = tags_used
    info["status"] = "FAIL" if hard else "PASS"

    if case:
        expect = case["expect"]
        if case.get("needs_interaction"):
            wanted = [LABELS[lang]["basis_values"][i] for i in expect.get("basis", [])]
            if info["outcome"] == "stop" or not (basis and names_input(basis, LABELS[lang], expect.get("basis", []))):
                # The agent could not load or click the page. That is the environment, not a pass.
                if not hard:
                    info["status"] = "BLOCKED"
                    soft.append(f"BLOCKED: this case needs {wanted} and the output says the page was not exercised; rerun where a browser can reach the local server")
                return hard, soft, info
        if expect.get("outcome") and expect["outcome"] != info["outcome"]:
            hard.append(f"case expects outcome '{expect['outcome']}', got '{info['outcome']}'")
        if "verdict_in" in expect and info["outcome"] == "report":
            allowed = [LABELS[lang]["verdicts"][key] for key in expect["verdict_in"]]
            if info.get("verdict") not in allowed:
                hard.append(f"case allows verdicts {allowed}, got '{info.get('verdict')}'")
        if expect.get("language") and expect["language"] != lang:
            hard.append(f"case expects a '{expect['language']}' answer, got '{lang}'")
        if basis and expect.get("basis"):
            if not names_input(basis, LABELS[lang], expect["basis"]):
                want = [LABELS[lang]["basis_values"][i] for i in expect["basis"]]
                hard.append(f"case expects basis {want}")
        for tag in expect.get("forbidden_tags", []):
            if tag in info["tags"]:
                hard.append(f"case forbids the [{tag}] tag with this input")
        for tag in expect.get("required_tags", []):
            if tag not in info["tags"]:
                hard.append(f"case needs at least one [{tag}] fix")
        for phrase in expect.get("must_not_contain", []):
            if phrase.lower() in text.lower():
                hard.append(f"must not contain '{phrase}'")
        for phrase in expect.get("should_not_contain", []):
            if asserts(text, phrase):
                soft.append(f"reads as a stated fact for this input: '{phrase}'")
        for group in expect.get("should_contain_any", []):
            if not any(phrase.lower() in text.lower() for phrase in group):
                soft.append(f"expected one of {group}")
        if expect.get("numbers_from_source"):
            src = source_text([case["_dir"] / p for p in case["source_text"]])
            # 1-3 number the fixes and name the verdict; 8 is the skill's own 8-second test.
            allowed = numbers_in(src) | set(expect.get("allowed_numbers", [])) | {"1", "2", "3", "8"}
            body = "\n".join(line for line in lines if not line.startswith("# ") and not line.startswith(lab["basis_prefix"]))
            invented = sorted(numbers_in(body) - allowed)
            if invented:
                hard.append(f"numbers not found in the page: {invented}")
    info["status"] = "FAIL" if hard else "PASS"
    return hard, soft, info


def load_case(path):
    case_dir = Path(path)
    case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    case["_dir"] = case_dir
    return case


def report(label, hard, soft):
    for item in hard:
        print(f"  FAIL {label}: {item}")
    for item in soft:
        print(f"  WARN {label}: {item}")


def run_all():
    ok = True
    cases = sorted(p for p in (TESTS / "cases").iterdir() if (p / "case.json").exists())
    for case_dir in cases:
        case = load_case(case_dir)
        # The reference answer and hand-written alternatives must pass with no warnings.
        for answer in [case_dir / "expected.md"] + sorted(case_dir.glob("alt-*.md")):
            hard, soft, info = check_output(answer.read_text(encoding="utf-8"), case)
            good = info["status"] == "PASS" and not soft
            print(f"{'ok' if good else 'FAIL':4} {case_dir.name}/{answer.name} ({info['outcome']}, {info.get('verdict', '-')}, tags {info['tags']})")
            report(answer.name, hard, soft)
            ok &= good
        for blocked in sorted(case_dir.glob("blocked-*.md")):
            hard, soft, info = check_output(blocked.read_text(encoding="utf-8"), case)
            good = info["status"] == "BLOCKED"
            print(f"{'ok' if good else 'FAIL':4} {case_dir.name}/{blocked.name} is {info['status']}")
            ok &= good
        for counter in sorted(case_dir.glob("counterexample-*.md")):
            hard, _, _ = check_output(counter.read_text(encoding="utf-8"), case)
            caught = bool(hard)
            print(f"{'ok' if caught else 'FAIL':4} {case_dir.name}/{counter.name} rejected: {hard[0] if hard else 'NOT REJECTED'}")
            ok &= caught
    # Contract edge cases with no case expectations: valid-*.md must pass, invalid-*.md must fail.
    for sample in sorted((TESTS / "contract-samples").glob("*.md")):
        hard, _, _ = check_output(sample.read_text(encoding="utf-8"))
        want_pass = sample.name.startswith("valid-")
        good = (not hard) if want_pass else bool(hard)
        detail = ("passes" if not hard else hard[0]) if want_pass else ("rejected: " + hard[0] if hard else "NOT REJECTED")
        print(f"{'ok' if good else 'FAIL':4} contract-samples/{sample.name} {detail}")
        ok &= good
    print("OK: all cases behave as expected" if ok else "FAIL: see above")
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(description="Check a Reality Check output against the contract.")
    parser.add_argument("output", nargs="?", help="markdown file holding one Reality Check output")
    parser.add_argument("--case", help="regression case folder with case.json")
    parser.add_argument("--all", action="store_true", help="check every case's expected output and counterexamples")
    args = parser.parse_args()
    if args.all:
        return run_all()
    if not args.output:
        parser.error("give an output file, or --all")
    case = load_case(args.case) if args.case else None
    hard, soft, info = check_output(Path(args.output).read_text(encoding="utf-8"), case)
    report(Path(args.output).name, hard, soft)
    print(f"{info['status']}: {info}")
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[info["status"]]


if __name__ == "__main__":
    sys.exit(main())
