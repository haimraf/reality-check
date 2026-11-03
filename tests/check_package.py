"""Package checks for the Reality Check skill. Standard library only.

Run from the repository root:

    python3 tests/check_package.py

Checks that the two shipped copies are identical, that frontmatter and
metadata.json are valid for Agent Skills directories, that triggers and
output labels agree across the skill, its Hebrew translation, and both
READMEs, that core rules are still present, and that the SKILL.md body
stays inside its size budget. Exit code 0 means every check passed.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "reality-check"
TESTS = ROOT / "tests"
SHIPPED = ["SKILL.md", "SKILL_HE.md", "metadata.json"]
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

failures = []


def check(ok, message):
    if not ok:
        failures.append(message)
    return ok


def parse_frontmatter(text, label):
    """Parse flat YAML frontmatter: `key: value` and folded `key: >-` blocks.

    Anything nested (an indented line that is not part of a folded block)
    is reported, because the Agent Skills spec allows only string values
    and Claude Desktop rejects a nested `metadata` block.
    """
    if not text.startswith("---\n"):
        check(False, f"{label}: must start with '---' frontmatter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        check(False, f"{label}: frontmatter is not closed with '---'")
        return {}, text
    lines = text[4:end].split("\n")
    body = text[end + 5:]
    data, key, mode, buf = {}, None, None, []

    def flush():
        if key is not None and mode is not None:
            joiner = " " if mode.startswith(">") else "\n"
            data[key] = joiner.join(part for part in buf if part)

    for line in lines:
        if not line.strip():
            continue
        if line[0] in " \t":
            if mode is None:
                check(False, f"{label}: nested frontmatter value near '{line.strip()}'; keep frontmatter flat and put enriched metadata in metadata.json")
                continue
            buf.append(line.strip())
            continue
        flush()
        key, mode, buf = None, None, []
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not check(match is not None, f"{label}: unreadable frontmatter line '{line}'"):
            continue
        k, value = match.groups()
        if value in (">", ">-", "|", "|-"):
            key, mode = k, value
        elif value == "":
            key, mode = k, None
            check(False, f"{label}: key '{k}' has a nested value; only flat string values are allowed")
        else:
            data[k] = value.strip().strip('"').strip("'")
    flush()
    return data, body


def main():
    contract = json.loads((TESTS / "contract.json").read_text(encoding="utf-8"))
    triggers = json.loads((TESTS / "triggers.json").read_text(encoding="utf-8"))

    # 1. The root copy and the package folder ship the same bytes.
    for name in SHIPPED:
        root_file, pkg_file = ROOT / name, PKG / name
        if check(root_file.exists() and pkg_file.exists(), f"{name}: missing at root or in reality-check/"):
            check(root_file.read_bytes() == pkg_file.read_bytes(),
                  f"{name}: root copy differs from reality-check/{name}; copy the package file to the root")

    skill_text = (PKG / "SKILL.md").read_text(encoding="utf-8")
    he_text = (PKG / "SKILL_HE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_he = (ROOT / "README.he.md").read_text(encoding="utf-8")

    # 2. Frontmatter.
    fm, body = parse_frontmatter(skill_text, "SKILL.md")
    he_fm, he_body = parse_frontmatter(he_text, "SKILL_HE.md")
    extra = set(fm) - ALLOWED_KEYS
    check(not extra, f"SKILL.md: unexpected frontmatter keys {sorted(extra)}; allowed: {sorted(ALLOWED_KEYS)}")
    check(set(he_fm) <= ALLOWED_KEYS, f"SKILL_HE.md: unexpected frontmatter keys {sorted(set(he_fm) - ALLOWED_KEYS)}")
    name = fm.get("name", "")
    check(bool(NAME_RE.match(name)) and len(name) <= 64, f"SKILL.md: invalid name '{name}'")
    check(name == PKG.name, f"SKILL.md: name '{name}' must match folder '{PKG.name}'")
    check(he_fm.get("name") == name, "SKILL_HE.md: name must match SKILL.md")
    for label, data in (("SKILL.md", fm), ("SKILL_HE.md", he_fm)):
        desc = data.get("description", "")
        check(0 < len(desc) <= 1024, f"{label}: description must be 1-1024 characters (is {len(desc)})")
        # Some clients count bytes; Hebrew is two bytes per letter in UTF-8.
        check(len(desc.encode("utf-8")) <= 1024, f"{label}: description is {len(desc.encode('utf-8'))} UTF-8 bytes; keep it at or under 1024")
        check("<" not in desc and ">" not in desc, f"{label}: no angle brackets in description")
        comp = data.get("compatibility", "")
        check(len(comp) <= 500, f"{label}: compatibility over 500 characters")
        check(data.get("license") == "MIT", f"{label}: license should be MIT")
    desc = fm.get("description", "")
    check("Use when" in desc, "SKILL.md: description needs a 'Use when' clause")
    check("Do NOT use" in desc, "SKILL.md: description needs a 'Do NOT use' boundary")

    # 3. Style: plain hyphens only (Skills IL convention, consistent across languages).
    for name in SHIPPED:
        text = (PKG / name).read_text(encoding="utf-8")
        dashes = re.findall("[–—]", text)
        check(not dashes, f"{name}: contains {len(dashes)} en/em dashes; use '-'")

    # 4. metadata.json.
    meta = json.loads((PKG / "metadata.json").read_text(encoding="utf-8"))
    for key in ("author", "version", "category", "tags", "display_name", "display_description", "supported_agents"):
        check(key in meta, f"metadata.json: missing '{key}'")
    check(bool(SEMVER_RE.match(meta.get("version", ""))), "metadata.json: version must be MAJOR.MINOR.PATCH")
    tags = meta.get("tags", {})
    check(len(tags.get("he", [])) == len(tags.get("en", [])) > 0, "metadata.json: tags.he and tags.en must be non-empty and the same length")
    check(all(t.strip() for t in tags.get("he", []) + tags.get("en", [])), "metadata.json: empty tag")
    for key in ("display_name", "display_description"):
        check(all(meta.get(key, {}).get(lang) for lang in ("he", "en")), f"metadata.json: {key} needs he and en")
    agents = meta.get("supported_agents", [])
    check(isinstance(agents, list) and agents and all(isinstance(a, str) for a in agents), "metadata.json: supported_agents must be a non-empty list of strings")

    # 5. Version agrees with the changelog.
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    top = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.M)
    check(top is not None and top.group(1) == meta.get("version"),
          f"CHANGELOG.md: top entry {top.group(1) if top else None} must match metadata.json version {meta.get('version')}")

    # 6. Triggers agree across the description, the Hebrew file, and both READMEs.
    canon = triggers["canonical"]
    low_desc = desc.lower()
    for phrase in canon["en"] + canon["transliterated"] + canon["negative"]:
        check(phrase.lower() in low_desc, f"SKILL.md description: missing trigger '{phrase}'")
    for phrase in canon["he"]:
        check(phrase in desc, f"SKILL.md description: missing Hebrew trigger '{phrase}'")
        check(phrase in he_fm.get("description", ""), f"SKILL_HE.md description: missing trigger '{phrase}'")
        check(phrase in readme_he, f"README.he.md: missing trigger '{phrase}'")
    for phrase in canon["he"] + canon["transliterated"] + ["reality check"]:
        check(phrase.lower() in readme.lower(), f"README.md: missing trigger '{phrase}'")
    check(len(triggers["should_trigger"]) >= 5 and len(triggers["should_not_trigger"]) >= 5,
          "triggers.json: keep at least five prompts on each side of the eval set")

    # 7. Output labels exist everywhere they are documented.
    for lang in ("en", "he"):
        labels = contract["labels"][lang]
        required = (labels["headings"] + list(labels["verdicts"].values()) + list(labels["tags"].values())
                    + labels["basis_values"] + [labels["basis_prefix"], labels["not_checked"], labels["stop"], labels["empty_slot"]])
        for item in required:
            check(item in skill_text, f"SKILL.md: missing {lang} contract label '{item}'")
            check(item in he_text, f"SKILL_HE.md: missing {lang} contract label '{item}'")
    for verdict in contract["labels"]["en"]["verdicts"].values():
        check(verdict in readme, f"README.md: missing verdict label '{verdict}'")
    for verdict in contract["labels"]["he"]["verdicts"].values():
        check(verdict in readme_he, f"README.he.md: missing verdict label '{verdict}'")

    # The README example is a real reference output, not a hand-edited copy.
    example = (TESTS / "cases" / "03-en-dead-controls-screenshot" / "expected.md").read_text(encoding="utf-8").strip()
    check(example in readme, "README.md: the example must match tests/cases/03-en-dead-controls-screenshot/expected.md")
    quoted = [line for line in readme_he.splitlines() if line.startswith(">")]
    # Undo the blockquote, the escaped '#' and '-', and the trailing '\' hard breaks used for RTL display.
    unquoted = "\n".join(re.sub(r"^\\([#-])", r"\1", line[2:] if line.startswith("> ") else line[1:]).rstrip("\\") for line in quoted)
    example_he = (TESTS / "cases" / "01-he-agency-pasted" / "expected.md").read_text(encoding="utf-8").strip()
    check(example_he in unquoted, "README.he.md: the example must match tests/cases/01-he-agency-pasted/expected.md")

    # Basis aliases must be the input-table names the skill itself uses.
    for lang, text in (("en", skill_text), ("he", he_text)):
        table_rows = [line.lower() for line in text.splitlines() if line.startswith("| ")]
        for names in contract["labels"][lang]["basis_aliases"]:
            for name in names:
                check(any(row.startswith("| " + name.lower()) for row in table_rows),
                      f"contract.json: basis alias '{name}' is not an input-table row in the {lang} skill file")

    # 8. Core rules are still present in both languages.
    for anchor in contract["rule_anchors"]["en"]:
        check(anchor in skill_text, f"SKILL.md: rule anchor missing: '{anchor}'")
    for anchor in contract["rule_anchors"]["he"]:
        check(anchor in he_text, f"SKILL_HE.md: rule anchor missing: '{anchor}'")

    # 9. The Hebrew translation keeps the same structure.
    def h2(text):
        prose = re.sub(r"^```.*?^```", "", text, flags=re.M | re.S)
        return re.findall(r"^## ", prose, re.M)

    def hard_rules(text, heading):
        section = text.split(heading, 1)[1].split("\n## ", 1)[0]
        return re.findall(r"^\d+\. ", section, re.M)

    def modules(text):
        return re.findall(r"^\*\*[^*]+\.\*\* ", text, re.M)

    check(len(h2(body)) == len(h2(he_body)), f"SKILL_HE.md: {len(h2(he_body))} sections vs {len(h2(body))} in SKILL.md")
    check(len(hard_rules(body, "## Hard rules")) == len(hard_rules(he_body, "## כללים מחייבים")),
          "SKILL_HE.md: hard rule count differs from SKILL.md")
    check(len(modules(body)) == len(modules(he_body)) == 5, "SKILL.md and SKILL_HE.md must each define five modules")

    # 10. Size budget for the part loaded on every activation.
    budget = contract["budget"]
    words, size = len(body.split()), len(body.encode("utf-8"))
    check(words <= budget["body_words_max"], f"SKILL.md body is {words} words; budget {budget['body_words_max']}")
    check(size <= budget["body_bytes_max"], f"SKILL.md body is {size} bytes; budget {budget['body_bytes_max']}")

    if failures:
        print(f"FAIL: {len(failures)} problem(s)")
        for item in failures:
            print(f"  - {item}")
        return 1
    print(f"OK: package checks passed (SKILL.md body {words} words, {size} bytes; description {len(desc)} chars, {len(desc.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
