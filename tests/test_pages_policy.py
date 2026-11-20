"""Public Pages cannot include private docs or agent/editorial notes."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_pages import check_pages, check_built_site


class PagesPolicyTests(unittest.TestCase):
    def fixture(self, dest: Path) -> Path:
        shutil.copytree(
            ROOT, dest, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", ".venv", ".venv-ci",
                                          "__pycache__", "site", "outputs"),
        )
        return dest

    def test_baseline_public_source(self):
        self.assertEqual([], check_pages(ROOT))
        self.assertTrue((ROOT / "docs/architecture/README.md").is_file())
        self.assertFalse((ROOT / "pages/AGENTS.md").exists())
        self.assertFalse((ROOT / "CONTRIBUTING.md").exists())

    def test_docs_as_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            cfg = root / "mkdocs.yml"
            cfg.write_text(cfg.read_text().replace("docs_dir: pages", "docs_dir: docs"))
            self.assertIn("PAGES CONFIG: docs_dir/pages and site_dir/site required",
                          check_pages(root))

    def test_unlisted_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/draft.md").write_text("Public draft", encoding="utf-8")
            self.assertIn("PAGES NOT APPROVED: draft.md", check_pages(root))

    def test_agent_command_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text("Agent: wykonaj tę analizę", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md", check_pages(root))

    def test_editorial_note_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text("Uwagi redakcyjne: poprawić", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md", check_pages(root))

    def test_contribution_prompt_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text("How to contribute to this project", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md", check_pages(root))

    def test_link_to_internal_docs_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text("[Private](../docs/privacy.md)", encoding="utf-8")
            self.assertIn("PAGES INTERNAL REFERENCE: index.md", check_pages(root))

    def test_unreviewed_plugin_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            cfg = root / "mkdocs.yml"
            cfg.write_text(cfg.read_text() + "plugins: [search]\n")
            self.assertIn("PAGES CONFIG: unreviewed configuration keys",
                          check_pages(root))

    def test_private_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/private.md").symlink_to(root / "AGENTS.md")
            self.assertIn("PAGES SYMLINK: private.md", check_pages(root))

    def test_traversal_in_allowlist_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            p = root / "config/pages-policy.json"
            data = json.loads(p.read_text())
            data["public_files"].append("../docs/index.md")
            p.write_text(json.dumps(data))
            self.assertIn("PAGES POLICY: invalid public file allowlist", check_pages(root))

    def test_direct_agent_note_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text("Dla agenta: zmień opis", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md", check_pages(root))

    def test_contributing_document_cannot_be_allowlisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            cfg = root / "config/pages-policy.json"
            data = json.loads(cfg.read_text(encoding="utf-8"))
            data["public_files"].append("CONTRIBUTING.md")
            cfg.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("PAGES POLICY: invalid public file allowlist", check_pages(root))

    def test_not_run_editorial_marker_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text("Funkcja: NOT_RUN", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md", check_pages(root))

    def test_polish_ai_directive_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text(
                "Asystencie AI, zaktualizuj ten opis.", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md",
                          check_pages(root))

    def test_english_ai_directive_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text(
                "AI assistant: rewrite this page.", encoding="utf-8")
            self.assertIn("PAGES EDITORIAL OR AGENT CONTENT: index.md",
                          check_pages(root))

    def test_normal_ai_subject_is_not_an_instruction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/index.md").write_text(
                "# Wykorzystanie sztucznej inteligencji w diagnostyce\n",
                encoding="utf-8")
            self.assertEqual([], check_pages(root))

    def test_active_markup_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            for payload in (
                "<script>alert(1)</script>", "<img src=x onerror=alert(1)>",
                "[X](javascript:alert(1))",
            ):
                with self.subTest(payload=payload):
                    (root / "pages/index.md").write_text(payload, encoding="utf-8")
                    self.assertIn("PAGES UNSAFE ACTIVE CONTENT: index.md",
                                  check_pages(root))

    def test_built_site_rejects_extra_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            output = root / "site"
            output.mkdir()
            (output / "index.html").write_text("<h1>Aplikacja</h1>", encoding="utf-8")
            (output / "private.html").write_text("Private", encoding="utf-8")
            self.assertIn("PAGES BUILD UNEXPECTED FILE: private.html",
                          check_built_site(root))

    def test_built_site_rejects_agent_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            output = root / "site"
            output.mkdir()
            (output / "index.html").write_text(
                "<h1>Asystencie AI, zaktualizuj treść.</h1>", encoding="utf-8")
            self.assertIn("PAGES BUILD EDITORIAL CONTENT: index.html",
                          check_built_site(root))

    def test_built_site_missing_index_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site").mkdir()
            self.assertIn("PAGES BUILD MISSING HTML: index.html",
                          check_built_site(root))

    def test_built_site_minimal_index_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            site = root / "site"
            site.mkdir()
            (site / "index.html").write_text("<h1>Aplikacja</h1>", encoding="utf-8")
            self.assertEqual([], check_built_site(root))



if __name__ == "__main__":
    unittest.main()
