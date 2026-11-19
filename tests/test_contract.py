"""Contract, security and release-gate tests; no hardware or participant data."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
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
                         '"type":"not-a-valid-type"}', encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
