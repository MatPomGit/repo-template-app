"""Idempotent offline metadata initializer for a newly created app-* repository.

Does not assign a license, assert runtime validation, or publish the application.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
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
    if (not title.strip() or "REPLACE" in title or not owner.strip()
            or not runtime.strip() or any(
                "\n" in s or "\r" in s for s in (title, owner, runtime)
            )):
        raise ValueError("title, owner and runtime must be meaningful single-line values")
    # Reused verbatim in a public Markdown heading and MkDocs metadata.
    if (len(title.strip()) > 140
            or re.search(r"[<>\[\]!*\\]", title)
            or chr(96) in title
            or any(ord(ch) < 32 or 127 <= ord(ch) <= 159 for ch in title)
            or re.search(r"\b(?:javascript|vbscript|data|file)\s*:", title, re.I)):
        raise ValueError("title must be plain text without markup or control characters")
    parsed = urlsplit(repository_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("repository URL must be HTTPS with no credentials")
    manifest_path = root / "config/component.json"
    state_path = root / "PROJECT_STATE.yaml"
    citation_path = root / "CITATION.cff"
    readme_path = root / "README.md"
    mkdocs_path = root / "mkdocs.yml"
    public_index = root / "pages/index.md"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("type") != "app":
        raise ValueError("not an app template")
    if manifest.get("release_status") != "scaffold":
        raise ValueError("initializer is restricted to scaffold projects")
    old_id = manifest.get("component_id", "")
    if not (old_id.startswith("REPLACE") or old_id == app_id):
        raise ValueError("repository already initialised to a different component")
    state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    citation = yaml.safe_load(citation_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or not isinstance(citation, dict):
        raise ValueError("PROJECT_STATE and CITATION must be YAML mappings")
    if state.get("release_status") != "not_released":
        raise ValueError("initializer cannot modify a project with release status")
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
    mkdocs = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8"))
    if not isinstance(mkdocs, dict) or mkdocs.get("docs_dir") != "pages":
        raise ValueError("MkDocs source must remain the isolated pages directory")
    index_lines = public_index.read_text(encoding="utf-8").splitlines(keepends=True)
    if not index_lines or not index_lines[0].startswith("# "):
        raise ValueError("public index must begin with an H1 heading")
    index_lines[0] = "# " + title.strip() + "\n"
    mkdocs["site_name"] = title.strip()
    writes = {
        manifest_path: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        state_path: yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
        citation_path: yaml.safe_dump(citation, sort_keys=False, allow_unicode=True),
        readme_path: "".join(lines),
        mkdocs_path: yaml.safe_dump(mkdocs, sort_keys=False, allow_unicode=True),
        public_index: "".join(index_lines),
    }
    _commit_consistent_metadata(writes)


def _stage_file(path: Path, data: bytes) -> Path:
    """Write and fsync replacement bytes beside the destination for os.replace."""
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.app-stage-", dir=path.parent)
    staged = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        staged.unlink(missing_ok=True)
        raise
    return staged


def _commit_consistent_metadata(writes: dict[Path, str]) -> None:
    """Stage all changes first; restore already-replaced files on normal I/O failures.

    Each replacement is atomic on the same filesystem. Multi-file power-loss
    atomicity cannot be guaranteed; rerun the initializer after host recovery.
    """
    originals: dict[Path, bytes] = {}
    staged: dict[Path, Path] = {}
    try:
        for path, content in writes.items():
            if path.is_symlink() or not path.is_file():
                raise ValueError("initializer target must be a regular file: " + str(path))
            old = path.read_bytes()
            new = content.encode("utf-8")
            if old != new:
                originals[path] = old
                staged[path] = _stage_file(path, new)

        applied: list[Path] = []
        try:
            for path, temporary in staged.items():
                os.replace(temporary, path)
                applied.append(path)
        except OSError as exc:
            failures: list[str] = []
            for path in reversed(applied):
                temporary = None
                try:
                    temporary = _stage_file(path, originals[path])
                    os.replace(temporary, path)
                except OSError as rollback_exc:
                    failures.append(f"{path}: {rollback_exc}")
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
            if failures:
                raise OSError(
                    "initializer failed; MANUAL RECOVERY REQUIRED for: "
                    + "; ".join(failures)
                ) from exc
            raise OSError("initializer failed; previous metadata restored") from exc
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


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
