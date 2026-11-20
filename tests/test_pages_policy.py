"""Public Pages cannot include private docs or agent/editorial notes."""
from __future__ import annotations

import hashlib
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

    def test_built_site_rejects_unapproved_inline_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            site = root / "site"
            site.mkdir()
            (site / "index.html").write_text(
                "<script>const x = 'REPLACE';</script><h1>Aplikacja</h1>",
                encoding="utf-8")
            self.assertIn("PAGES BUILD UNAPPROVED INLINE SCRIPT: index.html",
                          check_built_site(root))

    def test_built_site_rejects_injected_theme_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site/js").mkdir(parents=True)
            (root / "site/index.html").write_text("<h1>Public</h1>", encoding="utf-8")
            (root / "site/js/unreviewed.js").write_text("alert(1)", encoding="utf-8")
            self.assertIn("PAGES BUILD UNEXPECTED FILE: js/unreviewed.js",
                          check_built_site(root))

    def test_built_site_rejects_tampered_pinned_asset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site/js").mkdir(parents=True)
            (root / "site/index.html").write_text("<h1>Public</h1>", encoding="utf-8")
            (root / "site/js/base.js").write_text("/* different */", encoding="utf-8")
            self.assertIn("PAGES BUILD THEME HASH MISMATCH: js/base.js",
                          check_built_site(root))

    def test_built_site_rejects_remote_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site").mkdir()
            (root / "site/index.html").write_text(
                '<script src="https://cdn.example.org/script.js"></script>',
                encoding="utf-8")
            self.assertIn("PAGES BUILD UNAPPROVED SCRIPT: index.html",
                          check_built_site(root))

    def test_built_site_accepts_only_reviewed_mkdocs_inline_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site").mkdir()
            (root / "site/index.html").write_text(
                '<script>\nvar base_url = ".",\nshortcuts = '
                '{"help": 191, "next": 78, "previous": 80, "search": 83};'
                '</script><h1>Public</h1>', encoding="utf-8")
            self.assertEqual([], check_built_site(root))

    def test_built_site_rejects_event_handler(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site").mkdir()
            (root / "site/index.html").write_text(
                '<button onclick="alert(1)">X</button>', encoding="utf-8")
            self.assertIn("PAGES BUILD EVENT HANDLER: index.html",
                          check_built_site(root))

    def test_pages_image_requires_approved_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "pages/photo.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x00IEND" + b"\x00" * 4)
            policy_path = root / "config/pages-policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["public_files"].append("photo.png")
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            self.assertIn("PAGES IMAGE HASH UNAPPROVED: photo.png", check_pages(root))
            policy["approved_image_sha256"]["photo.png"] = hashlib.sha256(
                (root / "pages/photo.png").read_bytes()).hexdigest()
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            self.assertEqual([], check_pages(root))

    def test_png_exif_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            png = (b"\x89PNG\r\n\x1a\n" +
                   b"\x00\x00\x00\x04eXIfGPS!" + b"\x00" * 4 +
                   b"\x00\x00\x00\x00IEND" + b"\x00" * 4)
            (root / "pages/photo.png").write_bytes(png)
            policy_path = root / "config/pages-policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["public_files"].append("photo.png")
            policy["approved_image_sha256"]["photo.png"] = hashlib.sha256(png).hexdigest()
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            self.assertIn("PAGES IMAGE METADATA: photo.png", check_pages(root))

    def test_cdn_highlighting_is_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            cfg = root / "mkdocs.yml"
            cfg.write_text(cfg.read_text(encoding="utf-8").replace(
                "highlightjs: false", "highlightjs: true"), encoding="utf-8")
            self.assertIn("PAGES CONFIG: reviewed local-only theme required",
                          check_pages(root))

    def test_built_site_accepts_builtin_search_form_without_attributes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site").mkdir()
            (root / "site/index.html").write_text(
                '<form><input type="search" id="mkdocs-search-query"></form>',
                encoding="utf-8")
            self.assertEqual([], check_built_site(root))

    def test_built_site_rejects_nonlocal_form(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(Path(tmp))
            (root / "site").mkdir()
            (root / "site/index.html").write_text(
                '<form action="https://elsewhere.example/" method="post"></form>',
                encoding="utf-8")
            self.assertIn("PAGES BUILD ACTIVE TAG: index.html",
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
