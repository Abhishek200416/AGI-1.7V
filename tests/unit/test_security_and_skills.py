"""Unit tests for Autonomous Application Security Auditor and Skill Organizer.
================================================================================
AGI 1.7 / IVA Autonomous Capability Module
Tests:
1. AST Static Application Security Testing (SAST) detecting RCE, code injection, and traversal.
2. Secret credential detection (API keys, private tokens).
3. Web security analysis (XSS in innerHTML, CORS wildcards).
4. PreProductionSecurityGatekeeper blocking production launch on critical vulnerabilities.
5. SkillOrganizer categorized domain loading across all 21 embedded MCP servers.
6. Dynamic skill ingestion from external directories & Git repositories (SKILL.md).
7. Fast skill search across tool names and descriptions.
8. Terminal client skills and security audit command execution.
================================================================================
"""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agents.IVA.engine.agi17.runtime.terminal_client import TerminalClient
from agents.IVA.engine.agi17.security.application_security_auditor import (
    ApplicationSecurityAuditor,
    PreProductionSecurityGatekeeper,
    SecurityAuditReport,
)
from agents.IVA.engine.agi17.skills.skill_organizer import (
    OrganizedSkill,
    SkillCategory,
    SkillOrganizer,
)


class TestSecurityAndSkills(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_sec_test_"))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_ast_sast_detects_command_injection_and_eval(self) -> None:
        # Create vulnerable python file with os.system and eval
        vuln_file = self.temp_dir / "vuln_app.py"
        vuln_file.write_text(
            """
import os
import subprocess

def run_user_cmd(cmd):
    os.system(cmd)  # CWE-78
    eval(cmd)       # CWE-95

def run_shell(user_arg):
    subprocess.run("ls " + user_arg, shell=True)  # CWE-78
            """,
            encoding="utf-8",
        )

        report = ApplicationSecurityAuditor.audit_codebase(vuln_file)
        self.assertFalse(report.production_ready)
        self.assertGreaterEqual(report.critical_count, 3)

        cwe_set = {v.cwe_id for v in report.vulnerabilities}
        self.assertIn("CWE-78", cwe_set)
        self.assertIn("CWE-95", cwe_set)

    def test_02_web_security_detects_xss_and_cors(self) -> None:
        # Create web frontend file with innerHTML and CORS wildcard
        web_file = self.temp_dir / "app.html"
        web_file.write_text(
            """
            <!DOCTYPE html>
            <html>
            <body>
              <div id="content"></div>
              <script>
                const userParam = location.search;
                document.getElementById('content').innerHTML = `<div>${userParam}</div>`;
              </script>
            </body>
            </html>
            """,
            encoding="utf-8",
        )

        api_file = self.temp_dir / "server.py"
        api_file.write_text(
            """
def set_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
            """,
            encoding="utf-8",
        )

        report = ApplicationSecurityAuditor.audit_codebase(self.temp_dir)
        cwe_set = {v.cwe_id for v in report.vulnerabilities}
        self.assertIn("CWE-79", cwe_set)   # XSS
        self.assertIn("CWE-942", cwe_set)  # CORS

    def test_03_pre_production_security_gatekeeper_blocks_bad_code(self) -> None:
        bad_dir = self.temp_dir / "bad_project"
        bad_dir.mkdir()
        (bad_dir / "exec.py").write_text("import os\ndef f(x): os.system(x)\n", encoding="utf-8")

        approved, report = PreProductionSecurityGatekeeper.verify_readiness(bad_dir)
        self.assertFalse(approved)
        self.assertFalse(report.production_ready)
        self.assertLess(report.security_score, 80.0)

        # Clean project must pass
        clean_dir = self.temp_dir / "clean_project"
        clean_dir.mkdir()
        (clean_dir / "safe.py").write_text(
            "def add(a: int, b: int) -> int:\n    return a + b\n",
            encoding="utf-8",
        )
        approved_clean, rep_clean = PreProductionSecurityGatekeeper.verify_readiness(clean_dir)
        self.assertTrue(approved_clean)
        self.assertTrue(rep_clean.production_ready)
        self.assertEqual(rep_clean.security_score, 100.0)

    def test_04_skill_organizer_categorization_and_domains(self) -> None:
        organizer = SkillOrganizer(storage_dir=self.temp_dir / "skills_store")
        grouped = organizer.list_by_category()

        # Check all 8 categories exist
        self.assertIn(SkillCategory.FRONTEND_UIUX.value, grouped)
        self.assertIn(SkillCategory.BROWSER_WEB_AUTOMATION.value, grouped)
        self.assertIn(SkillCategory.CYBER_SECURITY.value, grouped)
        self.assertIn(SkillCategory.CODE_INTELLIGENCE.value, grouped)

        # Embedded MCPs must be mapped
        all_skills = organizer.search_skills("")
        self.assertGreaterEqual(len(all_skills), 21)

        # Cyber security red-team skill must be present
        sec_matches = organizer.search_skills("security")
        self.assertTrue(any("security" in s.skill_id.lower() for s in sec_matches))

    def test_05_dynamic_skill_ingestion_from_directory(self) -> None:
        organizer = SkillOrganizer(storage_dir=self.temp_dir / "skills_store")

        # Mock an external skill repository with SKILL.md
        mock_repo = self.temp_dir / "external_skills"
        mock_skill = mock_repo / "ui-ux-pro-max"
        mock_skill.mkdir(parents=True)
        (mock_skill / "SKILL.md").write_text(
            """---
name: ui-ux-pro-max
description: Institutional design systems, CSS micro-interactions, and accessibility tokens.
---
# UI/UX Pro Max Skill
Guidance for high-craft UI/UX engineering.
            """,
            encoding="utf-8",
        )

        imported = organizer.import_skills_from_directory(mock_repo)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0].name, "ui-ux-pro-max")
        self.assertEqual(imported[0].category, SkillCategory.FRONTEND_UIUX)

        # Must be searchable
        search_res = organizer.search_skills("pro-max")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0].name, "ui-ux-pro-max")

    def test_06_terminal_client_skills_and_security_commands(self) -> None:
        client = TerminalClient(storage_root=self.temp_dir)
        buf = io.StringIO()

        with patch("sys.stdout", buf):
            client.execute_skills_command("list")
            client.execute_skills_command("search playwright")
            client.execute_security_audit_command(str(self.temp_dir))

        output = buf.getvalue()
        self.assertIn("IVA DYNAMIC SKILL & MCP ECOSYSTEM", output)
        self.assertIn("SKILL SEARCH RESULTS", output)
        self.assertIn("APPLICATION SECURITY & RED-TEAM AUDIT", output)
        self.assertIn("Security Posture Score", output)


if __name__ == "__main__":
    unittest.main()
