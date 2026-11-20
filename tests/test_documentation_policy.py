"""Regression checks for documentation char limits and fail-closed policy."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_documentation import check_documentation


class DocumentationPolicyTests(unittest.TestCase):
    def fixture(self, destination: Path) -> Path:
        shutil.copytree(
            ROOT, destination, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", ".venv", ".venv-ci",
                                          "__pycache__", "site", "outputs"),
        )
        return destination

    def test_current_documents_respect_character_budgets(self):
        self.assertEqual([], check_documentation(ROOT))

    def test_unicode_codepoints_not_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            policy = root / "config/documentation-policy.json"
            value = json.loads(policy.read_text(encoding="utf-8"))
            value["exact_limits"]["SUPPORT.md"] = 100
            policy.write_text(json.dumps(value), encoding="utf-8")
            (root / "SUPPORT.md").write_text("ą" * 100, encoding="utf-8")
            self.assertEqual([], check_documentation(root))

    def test_too_long_document_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            policy = json.loads((root / "config/documentation-policy.json").read_text())
            ceiling = policy["exact_limits"]["ARCHITECTURE.md"]
            (root / "ARCHITECTURE.md").write_text("a" * (ceiling + 1), encoding="utf-8")
            self.assertTrue(any("DOC LENGTH EXCEEDED: ARCHITECTURE.md" in error
                                for error in check_documentation(root)))

    def test_missing_required_document_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "CODE_OF_CONDUCT.md").unlink()
            self.assertIn("DOC MISSING: CODE_OF_CONDUCT.md", check_documentation(root))

    def test_new_adr_is_limited_by_glob(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            path = root / "docs/adr/0003-extra.md"
            path.write_text("a" * 10001, encoding="utf-8")
            self.assertTrue(any("DOC LENGTH EXCEEDED: docs/adr/0003-extra.md" in e
                                for e in check_documentation(root)))

    def test_invalid_limit_type_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            path = root / "config/documentation-policy.json"
            obj = json.loads(path.read_text(encoding="utf-8"))
            obj["exact_limits"]["README.md"] = True
            path.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("DOC POLICY: invalid limit or path README.md",
                          check_documentation(root))

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            path = root / "config/documentation-policy.json"
            obj = json.loads(path.read_text(encoding="utf-8"))
            obj["exact_limits"]["../outside.md"] = 500
            path.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("DOC POLICY: invalid limit or path ../outside.md",
                          check_documentation(root))

    def test_bad_policy_version_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            path = root / "config/documentation-policy.json"
            obj = json.loads(path.read_text(encoding="utf-8"))
            obj["schema_version"] = 999
            path.write_text(json.dumps(obj), encoding="utf-8")
            self.assertIn("DOC POLICY: unsupported schema_version",
                          check_documentation(root))


if __name__ == "__main__":
    unittest.main()
