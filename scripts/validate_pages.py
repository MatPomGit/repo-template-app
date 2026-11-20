"""Fail-closed checks for the isolated, explicitly allowlisted Pages source."""
from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
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
    re.compile(r"\b(?:TODO|FIXME|REPLACE(?:_[A-Z0-9_]+)?|PLACEHOLDER|TBD|"
               r"NOT_RUN|NOT_VERIFIED|NOT_DEFINED|NOT_CONFIGURED|INTERNAL_ONLY)\b", re.I),
    re.compile(r"(?:instrukcj\w*\s+dla\s+agent\w*|poleceni\w*\s+dla\s+agent\w*|"
               r"agent\s*:\s*(?:wykonaj|zmień|dodaj|popraw|sprawdź)|"
               r"dla\s+agenta\s*:|instructions for (?:an?\s+)?agent|"
               r"agent instructions|system prompt|developer instructions)", re.I),
    re.compile(r"(?:uwagi?\s+redakcyjne|notatk\w*\s+(?:dla\s+)?(?:autora|redaktora)|"
               r"editorial notes?|notes? to (?:author|editor)|"
               r"przed publikacją|do uzupełnienia|wstaw tutaj)", re.I),
    re.compile(r"(?:jak\s+(?:pomóc|wspierać)\s+(?:projekt|repozytorium)|"
               r"how to contribute|contributing guidelines|"
               r"contribute to (?:this|the) (?:project|repository)|"
               r"send (?:a )?pull request)", re.I),
)
# Heuristic source checks: publication also needs human review.
BANNED += (
    re.compile(
        r"\b(?:asystenc\w*\s+(?:AI|sztucznej\s+inteligencji)|"
        r"chatgpt|copilot|agent\w*\s+AI|AI\s+assistant|AI\s+agent)\b"
        r"\s*[,;:\-]?\s*(?:wykonaj|napisz|zmień|zaktualizuj|dodaj|usuń|"
        r"wygeneruj|popraw|sprawdź|przepisz|update|write|edit|modify|"
        r"rewrite|remove|create|generate|fix|ignore)\b",
        re.I,
    ),
    re.compile(
        r"\b(?:instrukcje?|polecenia?)\s+(?:dla\s+)?"
        r"(?:AI|ChatGPT|Copilota|asystenta|agent\w*)\b|"
        r"\binstructions?\s+for\s+(?:AI|ChatGPT|Copilot|an?\s+assistant)\b",
        re.I,
    ),
)
UNSAFE_MARKUP = re.compile(
    r"<\s*/?\s*(?:script|iframe|object|embed|form|base|meta)\b|"
    r"\bon[a-z]+\s*=|"
    r"\b(?:javascript|vbscript)\s*:|"
    r"\bdata\s*:\s*text/html",
    re.I,
)

UNSAFE_PARTS = {"docs", ".github", "secrets", "credentials", "private",
                "participants", "students", "raw", "internal",
                "agents.md", "agent_workflow.md", "contributing.md"}


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
                if UNSAFE_MARKUP.search(value):
                    errors.append("PAGES UNSAFE ACTIVE CONTENT: " + rel)
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


class _RenderedText(HTMLParser):
    """Extract the actual text shown to visitors, excluding theme scripts/CSS."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ignored = 0
        self.fragments: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.ignored += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.ignored:
            self.ignored -= 1

    def handle_data(self, data: str) -> None:
        if not self.ignored:
            self.fragments.append(data)


def rendered_text(html: str) -> str:
    parser = _RenderedText()
    parser.feed(html)
    parser.close()
    return " ".join(parser.fragments)


def check_built_site(root: Path = ROOT, site_dir: Path | None = None) -> list[str]:
    """Inspect rendered output; validation is not publication authorisation."""
    root = Path(root).resolve()
    directory = root / "site" if site_dir is None else Path(site_dir)
    if not directory.is_absolute():
        directory = root / directory
    if not directory.is_dir() or directory.is_symlink():
        return ["PAGES BUILD: missing or symlinked site output"]

    try:
        policy = json.loads((root / "config/pages-policy.json").read_text(encoding="utf-8"))
        allowed = policy["public_files"]
        config = yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))
        if not isinstance(allowed, list) or not all(safe_relative(x) for x in allowed):
            return ["PAGES BUILD: invalid source allowlist"]
        directory_urls = config.get("use_directory_urls", True)
        if type(directory_urls) is not bool:
            return ["PAGES BUILD: invalid URL configuration"]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, yaml.YAMLError, AttributeError):
        return ["PAGES BUILD: invalid source policy or configuration"]

    expected_html = {"404.html"}  # Standard MkDocs-generated fallback.
    expected_assets = set()
    for item in allowed:
        path = PurePosixPath(item)
        if path.suffix.lower() == ".md":
            without_suffix = path.with_suffix("")
            if without_suffix.name == "index":
                expected_html.add(str(without_suffix.parent / "index.html"))
            elif directory_urls:
                expected_html.add(str(without_suffix / "index.html"))
            else:
                expected_html.add(str(without_suffix) + ".html")
        elif path.suffix.lower() == ".html":
            expected_html.add(item)
        else:
            expected_assets.add(item)

    errors: list[str] = []
    found_html: set[str] = set()
    # Only assets from the pinned MkDocs theme or approved sources may appear.
    theme_dirs = {"css", "js", "img", "fonts", "webfonts", "search"}
    theme_ext = {".css", ".js", ".png", ".ico", ".svg", ".woff", ".woff2",
                 ".ttf", ".eot", ".map", ".json", ".gif", ".webp"}
    generated = {"sitemap.xml", "sitemap.xml.gz", "search/search_index.json"}
    for file in sorted(directory.rglob("*")):
        rel = file.relative_to(directory).as_posix()
        if file.is_symlink():
            errors.append("PAGES BUILD SYMLINK: " + rel)
            continue
        if file.is_dir():
            continue
        if not file.is_file():
            errors.append("PAGES BUILD UNSUPPORTED: " + rel)
            continue
        parts = PurePosixPath(rel).parts
        if any(part.lower() in UNSAFE_PARTS or part.startswith(".") for part in parts):
            errors.append("PAGES BUILD PRIVATE PATH: " + rel)
            continue
        theme_asset = parts[0] in theme_dirs and file.suffix.lower() in theme_ext
        if rel not in expected_html | expected_assets | generated and not theme_asset:
            errors.append("PAGES BUILD UNEXPECTED FILE: " + rel)
            continue
        if file.suffix.lower() == ".html":
            if rel not in expected_html:
                errors.append("PAGES BUILD UNAPPROVED HTML: " + rel)
                continue
            found_html.add(rel)
        if file.suffix.lower() == ".html" or rel == "search/search_index.json":
            try:
                if file.stat().st_size > 2_000_000:
                    errors.append("PAGES BUILD OVERSIZED: " + rel)
                    continue
                value = file.read_text(encoding="utf-8")
                checked_text = rendered_text(value) if file.suffix.lower() == ".html" else value
                if any(regex.search(checked_text) for regex in BANNED):
                    errors.append("PAGES BUILD EDITORIAL CONTENT: " + rel)
                if re.search(r"(?:\.\./docs/|/\.github/|\bAGENTS\.md\b|file://)",
                             value, re.I):
                    errors.append("PAGES BUILD INTERNAL REFERENCE: " + rel)
            except (OSError, UnicodeError):
                errors.append("PAGES BUILD UNREADABLE: " + rel)
    for item in expected_html - {"404.html"}:
        if item not in found_html:
            errors.append("PAGES BUILD MISSING HTML: " + item)
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--site-dir", type=Path, default=None,
                        help="also audit rendered site output (no deployment)")
    args = parser.parse_args()
    errors = check_pages(args.root)
    if args.site_dir is not None:
        errors.extend(check_built_site(args.root, args.site_dir))
    for error in errors:
        print("ERROR:", error)
    print("FAIL: pages" if errors else "PASS: pages")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
