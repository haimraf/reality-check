"""Check a Reality Check output against the output contract. Standard library only.

Check one agent output, optionally against a regression case:

    python3 tests/check_output.py my-run.md --case tests/cases/03-en-dead-controls-screenshot

Check every case (each expected.md must pass, each counterexample-*.md must fail)
and every contract sample (valid-*.md must pass, invalid-*.md must fail):

    python3 tests/check_output.py --all

Hard problems (exit code 1) are contract breaks and mechanical case
expectations. Soft problems are printed as WARN: wording an agent may
legitimately phrase differently, worth a human look.
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
    elif not any(value in basis for value in lab["basis_values"]):
        hard.append(f"basis line must name the input: one of {lab['basis_values']}")

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
            if content.count(" - ") < 2:
                hard.append(f"fix must read 'what - why it hurts - how': '{content[:60]}'")
            if tag_by_value[tag] == "assumed" and not any(w in content.lower() for w in lab["check_words"]):
                hard.append(f"an assumed fix must be phrased as a check ({lab['check_words']}): '{content[:60]}'")

        locked = [line for line in sections.get(lab["headings"][2], []) if line.strip()]
        bullets = [line for line in locked if line.startswith("- ")]
        if not 1 <= len(bullets) <= 3 or len(bullets) != len(locked):
            hard.append(f"'{lab['headings'][2]}' must hold 1-3 bullet lines, found {len(bullets)} of {len(locked)} lines")
        for line in bullets:
            if " - " not in line[2:]:
                hard.append(f"locked element must read 'element - why lock it': '{line[:60]}'")

        why = [line for line in sections.get(lab["headings"][3], []) if line.strip()]
        if not 2 <= len(why) <= 4:
            hard.append(f"'{lab['headings'][3]}' must be 2-4 lines, found {len(why)}")

        if re.search(r"\b\d+\s*/\s*(5|10|100)\b", text) or re.search(r"\bscore:|ציון:", text, re.I):
            hard.append("no module scores")
        if lab["verdicts"]["no"] == verdict and tags_used and set(tags_used) == {"assumed"}:
            hard.append(f"'{verdict}' cannot rest on assumptions alone")
    info["tags"] = tags_used

    if case:
        expect = case["expect"]
        if expect.get("outcome") and expect["outcome"] != info["outcome"]:
            hard.append(f"case expects outcome '{expect['outcome']}', got '{info['outcome']}'")
        if "verdict_in" in expect and info["outcome"] == "report":
            allowed = [LABELS[lang]["verdicts"][key] for key in expect["verdict_in"]]
            if info.get("verdict") not in allowed:
                hard.append(f"case allows verdicts {allowed}, got '{info.get('verdict')}'")
        if expect.get("language") and expect["language"] != lang:
            hard.append(f"case expects a '{expect['language']}' answer, got '{lang}'")
        if basis and expect.get("basis"):
            want = [LABELS[lang]["basis_values"][i] for i in expect["basis"]]
            if not any(value in basis for value in want):
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
            if phrase.lower() in text.lower():
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
        expected = case_dir / "expected.md"
        hard, soft, info = check_output(expected.read_text(encoding="utf-8"), case)
        status = "ok" if not hard else "FAIL"
        print(f"{status:4} {case_dir.name}/expected.md ({info['outcome']}, {info.get('verdict', '-')}, tags {info['tags']})")
        report("expected", hard, soft)
        ok &= not hard
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
    print(f"{'PASS' if not hard else 'FAIL'}: {info}")
    return 0 if not hard else 1


if __name__ == "__main__":
    sys.exit(main())
