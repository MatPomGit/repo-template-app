"""Fail-closed, offline checks for the app template and release evidence.

Install the pinned validation dependencies from requirements-ci.txt.
The scaffold phase checks structure and synthetic contracts, not application quality.
Release evidence must be generated outside the committed template to avoid a
circular requirement to commit the hash of the commit containing that same hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
import re
import subprocess
import sys
from pathlib import Path

from validate_documentation import check_documentation
from validate_pages import check_pages

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError as exc:
    raise SystemExit(
        "Missing validation dependency: install with "
        "'python -m pip install -r requirements-ci.txt' "
        f"({exc.name})"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_KIND = "app"
REQUIRED = (
    "README.md", "AGENTS.md", "ARCHITECTURE.md", "PROJECT_STATE.yaml",
    "CODE_OF_CONDUCT.md", "GOVERNANCE.md", "SUPPORT.md",
    "SECURITY.md", "LICENSE", "CITATION.cff",
    "CHANGELOG.md", "TEMPLATE_SETUP.md", "mkdocs.yml", ".gitignore",
    ".gitattributes", ".github/ACTIONS_POLICY.md",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/work-item.md",
    ".github/workflows/quality.yml", "requirements-ci.txt",
    ".github/AGENT_WORKFLOW.md", "tests/test_agent_policy.py",
    "profiles/android/AGENTS.md", "profiles/desktop/AGENTS.md",
    "profiles/sensor/AGENTS.md", "profiles/unity/AGENTS.md",
    "profiles/web/AGENTS.md",
    "config/component.json", "config/release-gate.json",
    "config/documentation-policy.json", "config/pages-policy.json",
    "pages/index.md", "scripts/validate_pages.py", "tests/test_pages_policy.py",
    "docs/index.md",
    "docs/documentation.md", "docs/architecture/README.md",
    "docs/architecture/components.md", "docs/architecture/data-flow.md",
    "docs/architecture/deployment.md", "docs/security/threat-model.md",
    "docs/security/incident-response.md", "docs/adr/README.md",
    "docs/adr/0002-security-boundaries.md", "docs/operations/runbook.md",
    "scripts/validate_documentation.py", "tests/test_documentation_policy.py",
    "docs/contracts.md", "docs/compatibility.md", "docs/consumers.md",
    "docs/dependencies.md", "docs/testing.md", "docs/installation.md",
    "docs/privacy.md", "docs/releases.md", "docs/pages.md",
    "docs/adr/0001-contract.md", "docs/hardware.md",
    "src/README.md", "examples/README.md", "examples/event.synthetic.json",
    "contracts/events.schema.json", "tests/test_contract.py",
    "scripts/validate_repository.py",
)
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
UTC_RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)$")
BAD_SEGMENTS = {"secrets", "credentials", "participants", "raw", "private", "processed-private"}
IGNORED_DIRS = {".git", ".venv", ".venv-ci", "venv", "__pycache__", "node_modules", "dist", "build", "site", "outputs"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".cff", ".toml", ".txt", ".ini", ".cfg", ".sh", ".ps1", ".xml"}
TOKEN_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9_]{36,}(?![A-Za-z0-9_])"),
    re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}(?![A-Za-z0-9])"),
)


def load_json(path: Path, errors: list[str], label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        errors.append("MALFORMED JSON: " + label)
        return {}
    if not isinstance(value, dict):
        errors.append("INVALID JSON ROOT: " + label)
        return {}
    return value


def load_yaml(path: Path, errors: list[str], label: str) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError, yaml.YAMLError):
        errors.append("MALFORMED YAML: " + label)
        return {}
    if not isinstance(value, dict):
        errors.append("INVALID YAML ROOT: " + label)
        return {}
    return value


def git_root(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            text=True, capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and Path(result.stdout.strip()).resolve() == root.resolve()


def tracked_files(root: Path):
    """Inspect only versioned files when Git is available; never traverse .git."""
    if git_root(root):
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z"],
                capture_output=True, timeout=10, check=False,
            )
            if result.returncode == 0:
                return [root / Path(s.decode("utf-8")) for s in result.stdout.split(b"\0") if s]
        except (OSError, UnicodeError, subprocess.TimeoutExpired):
            pass
    return [
        p for p in root.rglob("*")
        if p.is_file() or p.is_symlink()
        if not any(part in IGNORED_DIRS for part in p.relative_to(root).parts)
    ]


def scan_security(root: Path) -> list[str]:
    """High-confidence checks, NOT a comprehensive privacy or secret audit."""
    errors: list[str] = []
    for file in tracked_files(root):
        try:
            rel = file.relative_to(root)
        except ValueError:
            errors.append("UNSAFE PATH: outside repository")
            continue
        parts = [s.lower() for s in rel.parts]
        basename = rel.name.lower()
        if (
            any(s in BAD_SEGMENTS for s in parts[:-1])
            or basename == ".env"
            or (basename.startswith(".env.") and basename != ".env.example")
            or file.suffix.lower() in {".pem", ".p12", ".pfx", ".key"}
        ):
            errors.append("UNSAFE TRACKED PATH: " + rel.as_posix())
            continue
        if file.is_symlink():
            errors.append("UNSAFE SYMLINK: " + rel.as_posix())
            continue
        if file.suffix.lower() not in TEXT_SUFFIXES and basename not in {".gitignore", ".gitattributes", "license"}:
            continue
        try:
            if file.stat().st_size > 2_000_000:
                errors.append("OVERSIZED TEXT FILE: " + rel.as_posix())
                continue
            body = file.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append("UNREADABLE TRACKED TEXT: " + rel.as_posix())
            continue
        if any(pattern.search(body) for pattern in TOKEN_PATTERNS):
            errors.append("POTENTIAL SECRET: " + rel.as_posix())
    return errors


def local_path(root: Path, relative: object) -> Path | None:
    """Restrict evidence paths to existing regular files under the checkout."""
    if not isinstance(relative, str) or not relative.strip():
        return None
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts or "." in p.parts:
        return None
    try:
        resolved_root = root.resolve()
        target = (root / p).resolve(strict=True)
        if resolved_root not in target.parents or not target.is_file() or target.is_symlink():
            return None
        return target
    except (OSError, RuntimeError):
        return None


def git_revision(root: Path) -> tuple[str | None, bool]:
    """HEAD and whether tracked working files exactly match that commit."""
    if not git_root(root):
        return None, False
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True, capture_output=True, timeout=10, check=False,
        )
        dirty = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--"],
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, False
    sha = head.stdout.strip()
    return (sha if head.returncode == 0 and SHA40.fullmatch(sha) else None,
            dirty.returncode == 0)


def validate_schema(root: Path, schema: dict, errors: list[str]) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("CONTRACT: unsupported JSON Schema dialect")
        return
    # Validate the schema itself before inspecting nested keywords.
    # Invalid keyword types must produce a controlled failure, not a traceback.
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError:
        errors.append("CONTRACT: invalid JSON Schema")
        return
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        errors.append("CONTRACT: missing properties map")
        return
    version_property = properties.get("schema_version")
    if not isinstance(version_property, dict) or version_property.get("const") != 1:
        errors.append("CONTRACT: event schema_version must be 1")
    mandatory = {"schema_version", "event_id", "session_id", "timestamp_utc",
                 "source", "event_type", "quality", "payload"}
    declared = schema.get("required")
    if not isinstance(declared, list) or not mandatory.issubset(set(
        item for item in declared if isinstance(item, str)
    )):
        errors.append("CONTRACT: required event fields missing")
    if schema.get("additionalProperties") is not False:
        errors.append("CONTRACT: additionalProperties must be false")
    try:
        event = load_json(root / "examples/event.synthetic.json", errors,
                          "examples/event.synthetic.json")
        if event:
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            problems = list(validator.iter_errors(event))
            if problems:
                errors.append("EVENT SCHEMA: synthetic example invalid")
            # JSON Schema's format checker may silently skip date-time without
            # optional format dependencies. Enforce UTC/RFC3339 independently.
            timestamp = event.get("timestamp_utc")
            if not isinstance(timestamp, str) or not UTC_RFC3339.fullmatch(timestamp):
                errors.append("EVENT SCHEMA: synthetic example invalid")
            else:
                try:
                    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if parsed.utcoffset().total_seconds() != 0:
                        errors.append("EVENT SCHEMA: synthetic example invalid")
                except (ValueError, AttributeError, OverflowError):
                    errors.append("EVENT SCHEMA: synthetic example invalid")
            if event.get("quality") != "synthetic":
                errors.append("EVENT QUALITY: example must remain synthetic")
    except SchemaError:
        errors.append("CONTRACT: invalid JSON Schema")


def check(root: Path = ROOT, phase: str = "scaffold", evidence: Path | None = None) -> list[str]:
    root = Path(root).resolve()
    errors: list[str] = []
    if phase not in {"scaffold", "release"}:
        return ["UNSUPPORTED PHASE"]
    for rel in REQUIRED:
        path = root / rel
        if not path.is_file() or path.is_symlink() or not path.stat().st_size:
            errors.append("MISSING OR EMPTY: " + rel)
    if errors:
        return errors

    c = load_json(root / "config/component.json", errors, "config/component.json")
    template_gate = load_json(root / "config/release-gate.json", errors,
                              "config/release-gate.json")
    schema = load_json(root / "contracts/events.schema.json", errors,
                       "contracts/events.schema.json")
    state = load_yaml(root / "PROJECT_STATE.yaml", errors, "PROJECT_STATE.yaml")
    citation = load_yaml(root / "CITATION.cff", errors, "CITATION.cff")
    if errors:
        return errors

    if c.get("type") != EXPECTED_KIND:
        errors.append("WRONG KIND: config/component.json:type")
    if c.get("schema_version") != 1 or state.get("schema_version") != 1:
        errors.append("SCHEMA: manifest or state schema_version must be 1")
    if c.get("template_version") != state.get("template_version"):
        errors.append("TEMPLATE VERSION: manifest/state mismatch")
    if not isinstance(c.get("template_version"), str) or not SEMVER.fullmatch(c["template_version"]):
        errors.append("TEMPLATE VERSION: invalid SemVer")
    if state.get("repository_type") != EXPECTED_KIND:
        errors.append("WRONG KIND: PROJECT_STATE.yaml:repository_type")
    if not SEMVER.fullmatch(str(c.get("version", ""))):
        errors.append("VERSION: invalid SemVer")
    if str(state.get("source_version")) != str(c.get("version")):
        errors.append("VERSION: state/source version mismatch")
    if template_gate.get("schema_version") != 1:
        errors.append("RELEASE GATE: invalid schema_version")
    if not str(c.get("component_id", "")).startswith("REPLACE"):
        if state.get("component_id") != c.get("component_id"):
            errors.append("COMPONENT ID: manifest/state mismatch")
    if not str(c.get("owner", "")).startswith("REPLACE"):
        if state.get("owner") != c.get("owner"):
            errors.append("OWNER: manifest/state mismatch")
    people = citation.get("authors", [])
    if not isinstance(people, list) or not any(
        isinstance(person, dict)
        and person.get("given-names") == "Mateusz"
        and person.get("family-names") == "Pomianek"
        for person in people
    ):
        errors.append("AUTHOR: Mateusz Pomianek must remain in CITATION.cff")
    if citation.get("type") != "software":
        errors.append("CITATION: expected software type")
    if citation.get("title") != c.get("display_name"):
        errors.append("CITATION: title/manifest mismatch")
    if citation.get("version") != c.get("version"):
        errors.append("CITATION: version/manifest mismatch")
    if c.get("export_contract") != "contracts/events.schema.json":
        errors.append("CONTRACT: export_contract path mismatch")
    if not isinstance(c.get("source_paths"), list) or not c.get("source_paths"):
        errors.append("SOURCES: non-empty source_paths required")
    validate_schema(root, schema, errors)
    errors.extend(check_documentation(root))
    errors.extend(check_pages(root))
    errors.extend(scan_security(root))

    if phase == "release":
        gate = (load_json(Path(evidence), errors, "external release evidence")
                if evidence is not None else template_gate)
        if gate.get("schema_version") != 1:
            errors.append("EVIDENCE: unsupported schema_version")
        for field in ("component_id", "display_name", "owner", "repository_url",
                      "license_spdx", "runtime"):
            value = c.get(field)
            if not isinstance(value, str) or not value.strip() or "REPLACE" in value or value == "UNDECIDED":
                errors.append("UNCONFIGURED: config/component.json:" + field)
        if c.get("release_status") not in {"ready", "released"}:
            errors.append("NOT_RELEASED: component not ready")
        if state.get("release_status") not in {"ready", "released"}:
            errors.append("NOT_RELEASED: PROJECT_STATE not ready")
        if state.get("release_status") != c.get("release_status"):
            errors.append("RELEASE STATUS: manifest/state mismatch")
        if not isinstance(c.get("platforms"), list) or not c.get("platforms"):
            errors.append("PLATFORMS: none declared")
        if c.get("data_classification") in (None, "", "unassessed"):
            errors.append("DATA GOVERNANCE: classification not assessed")
        if c.get("network_egress") in (None, "", "unassessed"):
            errors.append("DATA GOVERNANCE: egress not assessed")
        if c.get("hardware_required"):
            if not c.get("equipment_refs"):
                errors.append("EQUIPMENT: equipment_refs absent")
            if gate.get("hardware_verified") is not True:
                errors.append("HARDWARE: verification not declared")
            hw = local_path(root, gate.get("hardware_report_path"))
            if hw is None:
                errors.append("HARDWARE: evidence file missing")

        license_text = (root / "LICENSE").read_text(encoding="utf-8").strip()
        if ("UNDECIDED" in license_text.upper() or "TEMPLATE ONLY" in license_text.upper()
                or "NO PUBLIC LICENSE GRANTED" in license_text.upper()
                or len(license_text) < 80):
            errors.append("LICENSE: placeholder or missing license text")
        declared_spdx = c.get("license_spdx")
        expected_headings = {"MIT": "MIT License", "Apache-2.0": "Apache License",
                             "BSD-3-Clause": "Redistribution and use"}
        if not isinstance(declared_spdx, str) or declared_spdx not in expected_headings:
            errors.append("LICENSE: unsupported SPDX identifier; manual review required")
        elif expected_headings[declared_spdx].lower() not in license_text.lower():
            errors.append("LICENSE: SPDX declaration inconsistent with text")

        mandatory = (
            "tests_executed", "license_reviewed", "privacy_reviewed",
            "dependency_audit_passed", "installation_verified",
            "compatibility_documented", "publisher_approved",
        )
        for field in mandatory:
            if gate.get(field) is not True:
                errors.append("GATE BLOCKED: " + field)

        current_sha, clean = git_revision(root)
        tested_sha = gate.get("tested_commit_sha")
        if current_sha is None:
            errors.append("RELEASE: Git checkout and HEAD required")
        if not clean:
            errors.append("RELEASE: tracked working tree not clean")
        if not isinstance(tested_sha, str) or not SHA40.fullmatch(tested_sha):
            errors.append("MISSING TESTED SHA")
        elif current_sha is not None and current_sha != tested_sha:
            errors.append("TESTED SHA MISMATCH: must match HEAD")

        report_file = local_path(root, gate.get("test_report_path"))
        if report_file is None:
            errors.append("MISSING LOCAL TEST EVIDENCE")
        else:
            report = load_json(report_file, errors, "test report")
            if report.get("schema_version") != 1:
                errors.append("TEST REPORT: unsupported schema_version")
            report_sha = gate.get("test_report_sha256")
            if (not isinstance(report_sha, str) or not SHA256.fullmatch(report_sha)
                    or hashlib.sha256(report_file.read_bytes()).hexdigest() != report_sha):
                errors.append("TEST REPORT: SHA256 mismatch or missing")
            if report.get("tested_commit_sha") != tested_sha or report.get("status") != "passed":
                errors.append("TEST REPORT: wrong SHA or non-passing result")
            checks = report.get("checks")
            required_checks = {"unit", "contract", "installation", "dependencies",
                               "compatibility", "privacy"}
            if not isinstance(checks, dict) or any(checks.get(k) != "passed" for k in required_checks):
                errors.append("TEST REPORT: mandatory checks not passed")

        artifact_file = local_path(root, gate.get("release_artifact_path"))
        digest = gate.get("release_artifact_sha256")
        if artifact_file is None:
            errors.append("MISSING RELEASE ARTIFACT")
        elif not isinstance(digest, str) or not SHA256.fullmatch(digest):
            errors.append("MISSING RELEASE ARTIFACT SHA256")
        else:
            hash_value = hashlib.sha256()
            with artifact_file.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    hash_value.update(block)
            if hash_value.hexdigest() != digest:
                errors.append("ARTIFACT CHECKSUM MISMATCH")

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--phase", choices=("scaffold", "release"), default="scaffold")
    parser.add_argument(
        "--evidence", type=Path, default=None,
        help="Uncommitted evidence JSON for release; keep outside version control",
    )
    args = parser.parse_args()
    errors = check(args.root, args.phase, args.evidence)
    for error in errors:
        print("ERROR:", error)
    label = ("scaffold" if args.phase == "scaffold"
             else "release-evidence consistency (NOT publication approval)")
    print(("FAIL" if errors else "PASS") + ": app " + label)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
