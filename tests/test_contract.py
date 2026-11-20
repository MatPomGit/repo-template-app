"""Contract, security and release-gate tests; no hardware or participant data."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_repository import check


class ContractTests(unittest.TestCase):
    def fixture(self, destination: Path) -> Path:
        shutil.copytree(
            ROOT, destination, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", ".venv", ".venv-ci",
                                          "__pycache__", "site", "outputs"),
        )
        return destination

    def test_scaffold_passes(self):
        self.assertEqual([], check(ROOT, "scaffold"))

    def test_release_remains_blocked_by_default(self):
        errors = check(ROOT, "release")
        self.assertIn("GATE BLOCKED: tests_executed", errors)
        self.assertIn("LICENSE: placeholder or missing license text", errors)

    def test_missing_required_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "README.md").unlink()
            self.assertTrue(any("README.md" in e for e in check(root, "scaffold")))

    def test_wrong_component_kind_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "config/component.json"
            obj = json.loads(p.read_text(encoding="utf-8"))
            obj["type"] = "lib"
            p.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("WRONG KIND: config/component.json:type", check(root))

    def test_synthetic_event_without_required_field_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "examples/event.synthetic.json"
            obj = json.loads(p.read_text(encoding="utf-8"))
            del obj["session_id"]
            p.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("EVENT SCHEMA: synthetic example invalid", check(root))

    def test_invalid_timestamp_fails_format_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "examples/event.synthetic.json"
            obj = json.loads(p.read_text(encoding="utf-8"))
            obj["timestamp_utc"] = "not-an-rfc3339-timestamp"
            p.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("EVENT SCHEMA: synthetic example invalid", check(root))

    def test_schema_without_properties_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "contracts/events.schema.json"
            p.write_text('{"$schema":"https://json-schema.org/draft/2020-12/schema",'
                         '"type":"object"}', encoding="utf-8")
            self.assertIn("CONTRACT: missing properties map", check(root))

    def test_invalid_json_schema_keyword_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "contracts/events.schema.json"
            value = json.loads(p.read_text(encoding="utf-8"))
            value["type"] = "not-a-json-schema-type"
            p.write_text(json.dumps(value), encoding="utf-8")
            self.assertIn("CONTRACT: invalid JSON Schema", check(root))

    def test_non_utc_event_timestamp_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "examples/event.synthetic.json"
            value = json.loads(p.read_text(encoding="utf-8"))
            value["timestamp_utc"] = "2026-11-19T10:00:00+02:00"
            p.write_text(json.dumps(value), encoding="utf-8")
            self.assertIn("EVENT SCHEMA: synthetic example invalid", check(root))

    def test_private_raw_path_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            path = root / "data/raw/participants.csv"
            path.parent.mkdir(parents=True)
            path.write_text("synthetic-only\n", encoding="utf-8")
            self.assertTrue(any("UNSAFE TRACKED PATH: data/raw/participants.csv" in e
                                for e in check(root)))

    def test_secret_pattern_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "unsafe.txt"
            p.write_text("ghp_" + "X" * 40, encoding="utf-8")
            self.assertIn("POTENTIAL SECRET: unsafe.txt", check(root))

    def test_citation_must_keep_primary_author(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "CITATION.cff"
            p.write_text('cff-version: 1.2.0\ntype: software\nauthors:\n'
                         '  - family-names: Someone\n    given-names: Else\n',
                         encoding="utf-8")
            self.assertIn("AUTHOR: Mateusz Pomianek must remain in CITATION.cff",
                          check(root))

    def test_project_state_must_agree_on_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "PROJECT_STATE.yaml"
            p.write_text(p.read_text(encoding="utf-8").replace(
                'source_version: 0.1.0', 'source_version: 9.9.9'), encoding="utf-8")
            self.assertIn("VERSION: state/source version mismatch", check(root))

    def release_fixture(self, root: Path, checksum: str) -> Path:
        self.fixture(root)
        config_path = root / "config/component.json"
        comp = json.loads(config_path.read_text(encoding="utf-8"))
        comp.update({
            "component_id": "app-example", "display_name": "Example",
            "owner": "Mateusz Pomianek",
            "repository_url": "https://github.com/MatPomGit/app-example",
            "license_spdx": "MIT", "runtime": "Python 3.12",
            "release_status": "ready", "platforms": ["linux"],
            "data_classification": "synthetic", "network_egress": "none",
        })
        config_path.write_text(json.dumps(comp), encoding="utf-8")
        citation_path = root / "CITATION.cff"
        citation_path.write_text(
            citation_path.read_text(encoding="utf-8")
            .replace('title: "REPLACE_APP_TITLE"', 'title: "Example"'),
            encoding="utf-8",
        )
        state = root / "PROJECT_STATE.yaml"
        state.write_text(state.read_text(encoding="utf-8")
                         .replace("REPLACE_COMPONENT_ID", "app-example")
                         .replace("REPLACE_OWNER", "Mateusz Pomianek")
                         .replace("release_status: not_released", "release_status: ready"),
                         encoding="utf-8")
        (root / "LICENSE").write_text(
            "MIT License\n\nCopyright 2026 Mateusz Pomianek\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a "
            "copy of this software to use and distribute the software, subject to "
            "the appropriate terms and conditions.\n", encoding="utf-8"
        )
        artifact = root / "outputs/app-example.zip"
        artifact.parent.mkdir(exist_ok=True)
        artifact.write_bytes(b"synthetic package fixture")
        report = {
            "schema_version": 1,
            "tested_commit_sha": "a" * 40, "status": "passed",
            "checks": {key: "passed" for key in (
                "unit", "contract", "installation", "dependencies",
                "compatibility", "privacy"
            )},
        }
        (root / "outputs/test-report.json").write_text(json.dumps(report), encoding="utf-8")
        gate = {
            "schema_version": 1, "tests_executed": True,
            "license_reviewed": True, "privacy_reviewed": True,
            "dependency_audit_passed": True, "installation_verified": True,
            "compatibility_documented": True, "publisher_approved": True,
            "hardware_verified": False, "hardware_report_path": None,
            "tested_commit_sha": "a" * 40,
            "test_report_path": "outputs/test-report.json",
            "test_report_sha256": hashlib.sha256(
                (root / "outputs/test-report.json").read_bytes()
            ).hexdigest(),
            "release_artifact_path": "outputs/app-example.zip",
            "release_artifact_sha256": checksum,
        }
        evidence = root / "outputs/release-evidence.json"
        evidence.write_text(json.dumps(gate), encoding="utf-8")
        return evidence

    def test_artifact_checksum_mismatch_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = self.release_fixture(root, "0" * 64)
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                result = check(root, "release", evidence)
            self.assertIn("ARTIFACT CHECKSUM MISMATCH", result)

    def test_mismatched_tested_sha_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            with patch("validate_repository.git_revision", return_value=("b" * 40, True)):
                result = check(root, "release", evidence)
            self.assertIn("TESTED SHA MISMATCH: must match HEAD", result)

    def test_consistent_fixture_validates_only_declared_evidence(self):
        """Positive gate fixture checks consistency, not third-party attestations."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                result = check(root, "release", evidence)
            self.assertEqual([], result)

    def test_reference_cli_smoke_schema(self):
        from jsonschema import Draft202012Validator, FormatChecker
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "src/example_cli.py"), "--output", str(out)],
                text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            event = json.loads(out.read_text(encoding="utf-8"))
            schema = json.loads((ROOT / "contracts/events.schema.json").read_text(encoding="utf-8"))
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(event)
            self.assertEqual("synthetic", event["quality"])

    def test_initializer_idempotent_and_coherent(self):
        from init_app import initialise
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            args = (root, "app-e4-fixture", "App E4 Fixture", "Mateusz Pomianek",
                    "https://github.com/MatPomGit/app-e4-fixture", "desktop", "Python 3.12")
            initialise(*args)
            first = {p: (root / p).read_bytes() for p in (
                "README.md", "CITATION.cff", "PROJECT_STATE.yaml", "config/component.json",
                "mkdocs.yml", "pages/index.md"
            )}
            initialise(*args)
            self.assertEqual(first, {p: (root / p).read_bytes() for p in first})
            self.assertEqual([], check(root, "scaffold"))
            self.assertEqual("scaffold",
                json.loads((root / "config/component.json").read_text())["release_status"])
            self.assertEqual("App E4 Fixture", yaml.safe_load(
                (root / "mkdocs.yml").read_text())["site_name"])
            self.assertTrue((root / "pages/index.md").read_text(
                encoding="utf-8").startswith("# App E4 Fixture"))

    def test_initializer_rollback_after_partial_replace_failure(self):
        """A failed middle replacement must not leave mixed component metadata."""
        import os
        from init_app import initialise
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            paths = (
                "config/component.json", "PROJECT_STATE.yaml", "CITATION.cff",
                "README.md", "mkdocs.yml", "pages/index.md",
            )
            before = {name: (root / name).read_bytes() for name in paths}
            args = (root, "app-e4-rollback", "App Rollback", "Mateusz Pomianek",
                    "https://github.com/MatPomGit/app-e4-rollback",
                    "desktop", "Python 3.12")
            real_replace = os.replace
            calls = 0

            def fail_third_replace(src, dest):
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("injected replacement failure")
                return real_replace(src, dest)

            with patch("init_app.os.replace", side_effect=fail_third_replace):
                with self.assertRaisesRegex(OSError, "previous metadata restored"):
                    initialise(*args)
            self.assertEqual(before, {
                name: (root / name).read_bytes() for name in paths
            })
            self.assertFalse(list(root.rglob("*.app-stage-*")))
            initialise(*args)
            self.assertEqual([], check(root, "scaffold"))

    def test_initializer_does_not_change_files_when_staging_fails(self):
        from init_app import initialise
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            before = (root / "config/component.json").read_bytes()
            args = (root, "app-e4-staging", "App Stage", "Mateusz Pomianek",
                    "https://github.com/MatPomGit/app-e4-staging",
                    "desktop", "Python 3.12")
            with patch("init_app.os.fsync", side_effect=OSError("staging failed")):
                with self.assertRaisesRegex(OSError, "staging failed"):
                    initialise(*args)
            self.assertEqual(before, (root / "config/component.json").read_bytes())
            self.assertFalse(list(root.rglob("*.app-stage-*")))

    def test_initializer_does_not_overwrite_existing_component(self):
        from init_app import initialise
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            args = (root, "app-first", "First", "Mateusz Pomianek",
                    "https://github.com/MatPomGit/app-first", "desktop", "Python 3.12")
            initialise(*args)
            with self.assertRaisesRegex(ValueError, "already initialised"):
                initialise(root, "app-second", *args[2:])

    def test_invalid_semver_leading_zero_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "config/component.json"
            c = json.loads(p.read_text(encoding="utf-8"))
            c["version"] = "01.2.3"
            p.write_text(json.dumps(c), encoding="utf-8")
            self.assertIn("VERSION: invalid SemVer", check(root))

    def test_citation_title_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "CITATION.cff"
            p.write_text(p.read_text(encoding="utf-8").replace(
                'title: "REPLACE_APP_TITLE"', 'title: "Mismatched"'), encoding="utf-8")
            self.assertIn("CITATION: title/manifest mismatch", check(root))

    def test_release_unsupported_spdx_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            path = root / "config/component.json"
            c = json.loads(path.read_text(encoding="utf-8"))
            c["license_spdx"] = "UNKNOWN-LICENSE"
            path.write_text(json.dumps(c), encoding="utf-8")
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                self.assertIn("LICENSE: unsupported SPDX identifier; manual review required",
                              check(root, "release", evidence))

    def test_release_state_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            path = root / "PROJECT_STATE.yaml"
            path.write_text(path.read_text(encoding="utf-8")
                            .replace("release_status: ready", "release_status: released"),
                            encoding="utf-8")
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                self.assertIn("RELEASE STATUS: manifest/state mismatch",
                              check(root, "release", evidence))

    def test_release_evidence_schema_missing_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            obj = json.loads(evidence.read_text(encoding="utf-8"))
            del obj["schema_version"]
            evidence.write_text(json.dumps(obj), encoding="utf-8")
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                self.assertIn("EVIDENCE: unsupported schema_version",
                              check(root, "release", evidence))

    def test_release_report_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            report_file = root / "outputs/test-report.json"
            report_file.write_text(report_file.read_text(encoding="utf-8") + "\n",
                                   encoding="utf-8")
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                self.assertIn("TEST REPORT: SHA256 mismatch or missing",
                              check(root, "release", evidence))

    def test_boolean_schema_version_rejected_without_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "contracts/events.schema.json"
            obj = json.loads(p.read_text(encoding="utf-8"))
            obj["properties"]["schema_version"] = False
            p.write_text(json.dumps(obj), encoding="utf-8")
            errors = check(root)
            self.assertIn("CONTRACT: event schema_version must be 1", errors)

    def test_non_scalar_spdx_rejected_without_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            p = root / "config/component.json"
            obj = json.loads(p.read_text(encoding="utf-8"))
            obj["license_spdx"] = ["MIT"]
            p.write_text(json.dumps(obj), encoding="utf-8")
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                errors = check(root, "release", evidence)
            self.assertIn("LICENSE: unsupported SPDX identifier; manual review required", errors)

    def test_initializer_refuses_ready_project(self):
        from init_app import initialise
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            args = (root, "app-fixture", "App Fixture", "Mateusz Pomianek",
                    "https://github.com/MatPomGit/app-fixture", "desktop", "Python 3.12")
            initialise(*args)
            p = root / "config/component.json"
            obj = json.loads(p.read_text(encoding="utf-8"))
            obj["release_status"] = "ready"
            p.write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "restricted to scaffold"):
                initialise(*args)

    def test_initializer_rejects_markup_title_without_writing(self):
        from init_app import initialise
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            before = (root / "pages/index.md").read_bytes()
            for title in ("<script>alert(1)</script>", "A [link](https://x.test)",
                          "A ![image](https://x.test)", "Markdown *emphasis*",
                          "Bad " + chr(96) + "code" + chr(96), "X javascript:alert(1)"):
                with self.subTest(title=title):
                    with self.assertRaisesRegex(ValueError, "plain text"):
                        initialise(root, "app-fixture", title, "Mateusz Pomianek",
                                   "https://github.com/MatPomGit/app-fixture",
                                   "desktop", "Python 3.12")
                    self.assertEqual(before, (root / "pages/index.md").read_bytes())

    def test_initializer_rejects_multiline_title_without_writing(self):
        from init_app import initialise
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            before = (root / "config/component.json").read_bytes()
            with self.assertRaisesRegex(ValueError, "single-line"):
                initialise(root, "app-fixture", "Title\nInjected", "Mateusz Pomianek",
                           "https://github.com/MatPomGit/app-fixture", "desktop", "Python 3.12")
            self.assertEqual(before, (root / "config/component.json").read_bytes())

    def test_release_wrong_supported_spdx_text_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checksum = hashlib.sha256(b"synthetic package fixture").hexdigest()
            evidence = self.release_fixture(root, checksum)
            path = root / "config/component.json"
            obj = json.loads(path.read_text(encoding="utf-8"))
            obj["license_spdx"] = "Apache-2.0"
            path.write_text(json.dumps(obj), encoding="utf-8")
            with patch("validate_repository.git_revision", return_value=("a" * 40, True)):
                errors = check(root, "release", evidence)
            self.assertIn("LICENSE: SPDX declaration inconsistent with text", errors)


if __name__ == "__main__":
    unittest.main()
