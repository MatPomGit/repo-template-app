"""Fail-closed checks for the isolated, explicitly allowlisted Pages source."""
from __future__ import annotations

import argparse
import hashlib
import posixpath
import json
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".ico"}
BUILT_EXT = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".ico", ".svg", ".css",
             ".js", ".json", ".ttf", ".woff", ".woff2", ".map", ".gif", ".eot"}
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
    r"<\s*/?\s*(?:script|iframe|object|embed|form|base|meta|foreignObject)\b|"
    r"\bon[a-z]+\s*=|"
    r"\b(?:javascript|vbscript)\s*:|"
    r"\bdata\s*:\s*text/html",
    re.I,
)

UNSAFE_PARTS = {"docs", ".github", "secrets", "credentials", "private",
                "participants", "students", "raw", "internal",
                "agents.md", "agent_workflow.md", "contributing.md"}


def safe_relative(path: object, extensions: set[str] = ALLOWED_EXT) -> bool:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return False
    if path.startswith(("/", "./")) or "//" in path:
        return False
    parts = PurePosixPath(path).parts
    return bool(parts) and all(
        part not in {"", ".", ".."} and not part.startswith(".")
        and part.lower() not in UNSAFE_PARTS for part in parts
    ) and PurePosixPath(path).suffix.lower() in extensions


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
    images = policy.get("approved_image_sha256")
    theme = policy.get("approved_theme_assets")
    if (not isinstance(images, dict) or not isinstance(theme, dict) or not theme or
            any(not safe_relative(path, BUILT_EXT) or not isinstance(digest, str)
                or not re.fullmatch(r"[a-f0-9]{64}", digest)
                for path, digest in theme.items()) or
            any(not safe_relative(path) or PurePosixPath(path).suffix.lower() not in IMAGE_EXT
                or path not in allowed or not isinstance(digest, str)
                or not re.fullmatch(r"[a-f0-9]{64}", digest)
                for path, digest in images.items())):
        return sorted(set(errors + ["PAGES POLICY: invalid theme or image digest manifest"]))

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
    if config.get("theme") != {"name": "mkdocs", "highlightjs": False}:
        errors.append("PAGES CONFIG: reviewed local-only theme required")
    nav = nav_paths(config.get("nav"))
    if nav is None or "index.md" not in nav or any(item not in allowed for item in nav):
        errors.append("PAGES CONFIG: navigation must contain only allowlisted files")
    if not isinstance(config.get("site_name"), str) or not config["site_name"].strip():
        errors.append("PAGES CONFIG: site_name required")
    elif UNSAFE_MARKUP.search(config["site_name"]):
        errors.append("PAGES CONFIG: unsafe site title")

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
            if path.suffix.lower() in IMAGE_EXT:
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                if images.get(rel) != actual:
                    errors.append("PAGES IMAGE HASH UNAPPROVED: " + rel)
                for error in image_metadata_errors(path):
                    errors.append(error.replace(path.name, rel))
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



def image_metadata_errors(path: Path) -> list[str]:
    """Conservative high-confidence metadata screen; does not certify anonymity."""
    if path.suffix.lower() not in IMAGE_EXT or path.suffix.lower() == ".ico":
        return []
    rel = path.name
    try:
        data = path.read_bytes()
    except OSError:
        return ["PAGES IMAGE UNREADABLE: " + rel]
    ext = path.suffix.lower()
    try:
        if ext == ".png":
            if not data.startswith(b"\x89PNG\r\n\x1a\n"):
                return ["PAGES IMAGE INVALID PNG: " + rel]
            pos = 8
            saw_end = False
            while pos + 12 <= len(data):
                n = int.from_bytes(data[pos:pos + 4], "big")
                kind = data[pos + 4:pos + 8]
                if pos + 12 + n > len(data):
                    return ["PAGES IMAGE INVALID PNG: " + rel]
                if kind in {b"eXIf", b"iTXt", b"tEXt", b"zTXt", b"iCCP"}:
                    return ["PAGES IMAGE METADATA: " + rel]
                pos += n + 12
                if kind == b"IEND":
                    saw_end = True
                    break
            if not saw_end:
                return ["PAGES IMAGE INVALID PNG: " + rel]
        elif ext in {".jpg", ".jpeg"}:
            if not data.startswith(b"\xff\xd8"):
                return ["PAGES IMAGE INVALID JPEG: " + rel]
            pos = 2
            while pos < len(data):
                if data[pos] != 0xFF:
                    return ["PAGES IMAGE INVALID JPEG: " + rel]
                while pos < len(data) and data[pos] == 0xFF:
                    pos += 1
                if pos >= len(data):
                    return ["PAGES IMAGE INVALID JPEG: " + rel]
                marker = data[pos]
                pos += 1
                if marker in {0xD9, 0xDA}:
                    break  # Image data is not interpreted as metadata.
                if pos + 2 > len(data):
                    return ["PAGES IMAGE INVALID JPEG: " + rel]
                n = int.from_bytes(data[pos:pos + 2], "big")
                if n < 2 or pos + n > len(data):
                    return ["PAGES IMAGE INVALID JPEG: " + rel]
                if marker in {0xE1, 0xE2, 0xED, 0xFE}:
                    return ["PAGES IMAGE METADATA: " + rel]
                pos += n
        elif ext == ".webp":
            if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
                return ["PAGES IMAGE INVALID WEBP: " + rel]
            pos = 12
            while pos + 8 <= len(data):
                kind = data[pos:pos + 4]
                n = int.from_bytes(data[pos + 4:pos + 8], "little")
                if pos + 8 + n > len(data):
                    return ["PAGES IMAGE INVALID WEBP: " + rel]
                if kind in {b"EXIF", b"XMP ", b"ICCP"}:
                    return ["PAGES IMAGE METADATA: " + rel]
                pos += 8 + n + (n % 2)
        elif ext == ".avif":
            # AVIF can contain nested BMFF metadata. Full inspection still
            # requires an approved media tool and editorial review.
            if b"ftyp" not in data[:24]:
                return ["PAGES IMAGE INVALID AVIF: " + rel]
            if b"Exif" in data or b"application/rdf+xml" in data or b"XMP_" in data:
                return ["PAGES IMAGE METADATA: " + rel]
    except (ValueError, IndexError):
        return ["PAGES IMAGE MALFORMED: " + rel]
    return []


INLINE_THEME_CONFIG = re.compile(
    r'^\s*var\s+base_url\s*=\s*"(?:/|\.{1,2}(?:/\.\.)*)"\s*,\s*'
    r'shortcuts\s*=\s*\{\s*"help":\s*191,\s*"next":\s*78,\s*'
    r'"previous":\s*80,\s*"search":\s*83\s*\}\s*;\s*$'
)


class _RenderedSecurity(HTMLParser):
    """Fail closed on unapproved active markup and script sources in built HTML."""

    def __init__(self, html_path: str, approved_scripts: set[str]) -> None:
        super().__init__(convert_charrefs=True)
        self.html_path = html_path
        self.approved_scripts = approved_scripts
        self.errors: list[str] = []
        self.script_open = False
        self.script_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        props = {name.lower(): (value or "") for name, value in attrs}
        if tag in {"iframe", "object", "embed", "base"} or (tag == "form" and props):
            self.errors.append("PAGES BUILD ACTIVE TAG: " + self.html_path)
        if any(name.startswith("on") for name in props):
            self.errors.append("PAGES BUILD EVENT HANDLER: " + self.html_path)
        if any(re.search(r"(?i)\b(?:javascript|vbscript)\s*:|data\s*:\s*text/html", value)
               for value in props.values()):
            self.errors.append("PAGES BUILD ACTIVE URL: " + self.html_path)
        if tag == "meta" and props.get("http-equiv", "").lower() == "refresh":
            self.errors.append("PAGES BUILD META REFRESH: " + self.html_path)
        if tag == "script":
            source = props.get("src")
            if source:
                if source.startswith("/") and not source.startswith("//"):
                    rel = source.lstrip("/")
                elif re.match(r"^[A-Za-z][\w+.-]*:|^//", source):
                    rel = None
                else:
                    rel = posixpath.normpath(posixpath.join(
                        posixpath.dirname(self.html_path), source
                    ))
                if (rel not in self.approved_scripts or
                        rel is None or rel.startswith(("../", "/"))):
                    self.errors.append("PAGES BUILD UNAPPROVED SCRIPT: " + self.html_path)
            else:
                self.script_open = True
                self.script_text = []
        if tag in {"link", "img", "source"}:
            url = props.get("href", props.get("src", ""))
            if re.match(r"(?i)^https?://|^//", url):
                self.errors.append("PAGES BUILD EXTERNAL RESOURCE: " + self.html_path)

    def handle_data(self, data: str) -> None:
        if self.script_open:
            self.script_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.script_open:
            self.script_open = False
            code = "".join(self.script_text)
            if not INLINE_THEME_CONFIG.fullmatch(code):
                self.errors.append("PAGES BUILD UNAPPROVED INLINE SCRIPT: " + self.html_path)

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
        theme_assets = policy.get("approved_theme_assets")
        image_hashes = policy.get("approved_image_sha256")
        if (not isinstance(theme_assets, dict) or not theme_assets or
                not isinstance(image_hashes, dict) or
                any(not safe_relative(k, BUILT_EXT) or
                    not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v)
                    for k, v in theme_assets.items())):
            return ["PAGES BUILD: invalid theme digest manifest"]
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
    # Exact theme assets and their SHA-256 are captured from reviewed MkDocs.
    generated = {"sitemap.xml", "sitemap.xml.gz", "search/search_index.json"}
    approved_scripts = {k for k in theme_assets if k.endswith(".js")} | {
        k for k in allowed if k.endswith(".js")
    }
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
        if rel not in expected_html | expected_assets | generated | set(theme_assets):
            errors.append("PAGES BUILD UNEXPECTED FILE: " + rel)
            continue
        if rel in theme_assets:
            if hashlib.sha256(file.read_bytes()).hexdigest() != theme_assets[rel]:
                errors.append("PAGES BUILD THEME HASH MISMATCH: " + rel)
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
                if file.suffix.lower() == ".html":
                    security = _RenderedSecurity(rel, approved_scripts)
                    security.feed(value)
                    security.close()
                    errors.extend(security.errors)
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
