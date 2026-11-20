"""Idempotent offline metadata initializer for a newly created app-* repository.

Does not assign a license, assert runtime validation, or publish the application.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
APP_ID = re.compile(r"^app-[a-z0-9]+(?:-[a-z0-9]+)*$")


def initialise(root: Path, app_id: str, title: str, owner: str,
               repository_url: str, platform: str, runtime: str) -> None:
    if not APP_ID.fullmatch(app_id):
        raise ValueError("id must be a lowercase app-* slug")
    if not title.strip() or "REPLACE" in title or not owner.strip():
        raise ValueError("title and owner must be meaningful")
    parsed = urlsplit(repository_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("repository URL must be HTTPS with no credentials")
    manifest_path = root / "config/component.json"
    state_path = root / "PROJECT_STATE.yaml"
    citation_path = root / "CITATION.cff"
    readme_path = root / "README.md"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("type") != "app":
        raise ValueError("not an app template")
    old_id = manifest.get("component_id", "")
    if not (old_id.startswith("REPLACE") or old_id == app_id):
        raise ValueError("repository already initialised to a different component")
    state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    citation = yaml.safe_load(citation_path.read_text(encoding="utf-8"))
    authors = citation.get("authors", [])
    if not any(
        isinstance(a, dict)
        and a.get("given-names") == "Mateusz"
        and a.get("family-names") == "Pomianek"
        for a in authors
    ):
        raise ValueError("required author missing from CITATION.cff")
    manifest.update(
        component_id=app_id, display_name=title.strip(), owner=owner.strip(),
        repository_url=repository_url, documentation_url=repository_url,
        runtime=runtime.strip(), platforms=[platform],
    )
    state.update(
        component_id=app_id, owner=owner.strip(),
        source_version=manifest["version"], lifecycle="scaffold",
    )
    state["blockers"] = [
        item for item in state.get("blockers", [])
        if item != "replace_template_metadata"
    ]
    citation["title"] = title.strip()
    citation["version"] = manifest["version"]
    old_readme = readme_path.read_text(encoding="utf-8")
    lines = old_readme.splitlines(keepends=True)
    if not lines or not lines[0].startswith("# "):
        raise ValueError("README must start with an H1 heading")
    lines[0] = "# " + title.strip() + "\n"
    writes = {
        manifest_path: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        state_path: yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
        citation_path: yaml.safe_dump(citation, sort_keys=False, allow_unicode=True),
        readme_path: "".join(lines),
    }
    for path, content in writes.items():
        if path.read_text(encoding="utf-8") != content:
            path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--owner", default="Mateusz Pomianek")
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--runtime", default="Python 3.12")
    parser.add_argument("--platform", choices=("desktop", "web", "android", "sensor", "unity"), required=True)
    args = parser.parse_args()
    try:
        initialise(args.root.resolve(), args.id, args.title, args.owner,
                   args.repo_url, args.platform, args.runtime)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    print("INITIALISED:", args.id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
