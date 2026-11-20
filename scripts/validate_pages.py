"""Fail-closed checks for the isolated, explicitly allowlisted Pages source."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EXT = {".md", ".html", ".css", ".js", ".svg", ".png", ".jpg",
               ".jpeg", ".webp", ".avif", ".ico"}
TEXT_EXT = {".md", ".html", ".css", ".js", ".svg"}
CONFIG_KEYS = {"site_name", "site_url", "docs_dir", "site_dir", "nav",
               "theme", "use_directory_urls"}
BANNED = (
    re.compile(r"\b(?:AGENTS\.md|AGENT_WORKFLOW|CONTRIBUTING(?:\.md)?)\b", re.I),
    re.compile(r"\b(?:TODO|FIXME|REPLACE(?:_[A-Z0-9_]+)?|PLACEHOLDER|TBD)\b", re.I),
    re.compile(r"(?:instrukcj\w*\s+dla\s+agent\w*|poleceni\w*\s+dla\s+agent\w*|"
               r"agent\s*:\s*(?:wykonaj|zmień|dodaj|popraw|sprawdź)|"
               r"agent instructions|system prompt|developer instructions)", re.I),
    re.compile(r"(?:uwagi?\s+redakcyjne|notatk\w*\s+(?:dla\s+)?(?:autora|redaktora)|"
               r"editorial notes?|notes? to (?:author|editor)|"
               r"przed publikacją|do uzupełnienia|wstaw tutaj)", re.I),
    re.compile(r"(?:jak\s+(?:pomóc|wspierać)\s+(?:projekt|repozytorium)|"
               r"how to contribute|contributing guidelines|"
               r"contribute to (?:this|the) (?:project|repository)|"
               r"send (?:a )?pull request)", re.I),
)
UNSAFE_PARTS = {"docs", ".github", "secrets", "credentials", "private",
                "participants", "students", "raw", "internal"}


def safe_relative(path: object) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    if path.startswith(("/", "./")) or "//" in path:
        return False
    parts = PurePosixPath(path).parts
    return bool(parts) and all(
        part not in {"", ".", ".."} and not part.startswith(".")
        and part.lower() not in UNSAFE_PARTS for part in parts
    ) and PurePosixPath(path).suffix.lower() in ALLOWED_EXT


def nav_paths(value: object) -> list[str] | None:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            nested = nav_paths(item)
            if nested is None:
                return None
            result.extend(nested)
        return result
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            nested = nav_paths(item)
            if nested is None:
                return None
            result.extend(nested)
        return result
    return None


def check_pages(root: Path = ROOT) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    try:
        policy = json.loads((root / "config/pages-policy.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return ["PAGES POLICY: missing or invalid config"]
    if not isinstance(policy, dict) or type(policy.get("schema_version")) is not int or policy["schema_version"] != 1:
        return ["PAGES POLICY: unsupported schema_version"]
    if (policy.get("source_dir"), policy.get("output_dir"),
            policy.get("mkdocs_config")) != ("pages", "site", "mkdocs.yml"):
        errors.append("PAGES POLICY: source/build paths must remain isolated")
    allowed = policy.get("public_files")
    if not isinstance(allowed, list) or not allowed or any(
            not safe_relative(item) for item in allowed):
        return sorted(set(errors + ["PAGES POLICY: invalid public file allowlist"]))
    if len(set(allowed)) != len(allowed) or "index.md" not in allowed:
        errors.append("PAGES POLICY: duplicate or missing index")

    try:
        config = yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return sorted(set(errors + ["PAGES CONFIG: missing or invalid mkdocs.yml"]))
    if not isinstance(config, dict):
        return sorted(set(errors + ["PAGES CONFIG: expected mapping"]))
    if config.get("docs_dir") != "pages" or config.get("site_dir") != "site":
        errors.append("PAGES CONFIG: docs_dir/pages and site_dir/site required")
    if set(config) - CONFIG_KEYS:
        errors.append("PAGES CONFIG: unreviewed configuration keys")
    theme = config.get("theme", "mkdocs")
    if theme != "mkdocs" and theme != {"name": "mkdocs"}:
        errors.append("PAGES CONFIG: unreviewed theme")
    nav = nav_paths(config.get("nav"))
    if nav is None or "index.md" not in nav or any(item not in allowed for item in nav):
        errors.append("PAGES CONFIG: navigation must contain only allowlisted files")
    if not isinstance(config.get("site_name"), str) or not config["site_name"].strip():
        errors.append("PAGES CONFIG: site_name required")

    source = root / "pages"
    if not source.is_dir() or source.is_symlink():
        return sorted(set(errors + ["PAGES SOURCE: missing or symlinked pages directory"]))
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source).as_posix()
        if path.is_symlink():
            errors.append("PAGES SYMLINK: " + rel)
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            errors.append("PAGES UNSUPPORTED: " + rel)
            continue
        if not safe_relative(rel) or rel not in allowed:
            errors.append("PAGES NOT APPROVED: " + rel)
            continue
        try:
            if path.stat().st_size > 2_000_000:
                errors.append("PAGES TOO LARGE: " + rel)
                continue
            if path.suffix.lower() in TEXT_EXT:
                value = path.read_text(encoding="utf-8")
                if any(regex.search(value) for regex in BANNED):
                    errors.append("PAGES EDITORIAL OR AGENT CONTENT: " + rel)
                if re.search(r"\.\./|file://|https?://\S*(?:/AGENTS\.md|/\.github/)",
                             value, re.I):
                    errors.append("PAGES INTERNAL REFERENCE: " + rel)
        except (OSError, UnicodeError):
            errors.append("PAGES UNREADABLE: " + rel)
    for rel in allowed:
        path = source / rel
        if not path.is_file() or path.is_symlink():
            errors.append("PAGES MISSING APPROVED FILE: " + rel)
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check_pages(args.root)
    for error in errors:
        print("ERROR:", error)
    print("FAIL: pages" if errors else "PASS: pages")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
