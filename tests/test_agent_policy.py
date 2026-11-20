"""Structural regression checks for the scoped agent governance contract."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ("android", "desktop", "sensor", "unity", "web")


class AgentPolicyTests(unittest.TestCase):
    def test_parent_and_profile_instructions_present(self):
        self.assertTrue((ROOT / "AGENTS.md").is_file())
        self.assertTrue((ROOT / ".github/AGENT_WORKFLOW.md").is_file())
        for profile in PROFILES:
            with self.subTest(profile=profile):
                path = ROOT / "profiles" / profile / "AGENTS.md"
                self.assertTrue(path.is_file())
                content = path.read_text(encoding="utf-8")
                self.assertIn("../../AGENTS.md", content)
                self.assertIn("../../.github/AGENT_WORKFLOW.md", content)
                self.assertIn("README.md", content)

    def test_root_requires_evidence_and_release_boundary(self):
        policy = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in ("R0", "R1", "R2", "R3", "PASS", "NOT_RUN",
                         "DoR", "DoD", "Research Autopilot",
                         "dokładnym HEAD SHA", "nie jest GitHub"):
            with self.subTest(required=required):
                self.assertIn(required, policy)

    def test_workflow_makes_delivery_states_explicit(self):
        workflow = (ROOT / ".github/AGENT_WORKFLOW.md").read_text(encoding="utf-8")
        for required in ("Definition of Ready", "Definition of Done",
                         "ISSUE", "DoR", "DoD", "review", "merge",
                         "runtime", "NOT_APPLICABLE"):
            with self.subTest(required=required):
                self.assertIn(required.lower(), workflow.lower())


if __name__ == "__main__":
    unittest.main()
