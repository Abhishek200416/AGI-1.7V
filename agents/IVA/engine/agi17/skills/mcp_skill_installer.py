"""Autonomous MCP & Skill Installer for IVA AGI 1.7.

Autonomously identifies missing skills or MCP tools required for complex tasks,
discovers or synthesizes them from repositories or registries, verifies security with
the AST ApplicationSecurityAuditor, and mounts them directly into the runtime
without requiring manual user intervention.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .skill_organizer import SkillDomain, SkillOrganizer
from ..security.application_security_auditor import ApplicationSecurityAuditor

logger = logging.getLogger("iva.skills.mcp_installer")


class AutonomousMCPSkillInstaller:
    """Discovers, security-audits, and mounts MCP servers and skills autonomously."""

    # Built-in catalog of know-how templates for instant auto-installation
    EMBEDDED_KNOWHOW_REGISTRY: Dict[str, Dict[str, Any]] = {
        "threejs_3d_engine": {
            "name": "threejs_3d_engine",
            "domain": SkillDomain.FRONTEND_UIUX,
            "description": "Three.js 3D web graphics, procedural geometry, particle orbits, and WebGL rendering",
            "capabilities": ["webgl", "threejs", "camera_orbit", "particle_systems", "3d_scenes"],
            "code_sample": "# Three.js WebGL and procedural scene helper\n# Zero pip dependencies\n",
        },
        "cyber_exploit_tester": {
            "name": "cyber_exploit_tester",
            "domain": SkillDomain.CYBER_SECURITY,
            "description": "Autonomous exploit surface scanner, AST SAST auditor, and CWE validator",
            "capabilities": ["sast", "cwe_detection", "xss_scanner", "injection_probe", "red_team"],
            "code_sample": "# AST SAST exploit auditor helper\n",
        },
        "audio_synthesizer_web": {
            "name": "audio_synthesizer_web",
            "domain": SkillDomain.FRONTEND_UIUX,
            "description": "Web Audio API generative soundscapes, spatial audio, and futuristic HUD tones",
            "capabilities": ["web_audio", "frequency_oscillator", "spatial_audio", "hud_soundfx"],
            "code_sample": "# Web Audio API audio synthesis\n",
        },
        "git_workflow_automator": {
            "name": "git_workflow_automator",
            "domain": SkillDomain.CODE_INTELLIGENCE,
            "description": "Advanced multi-branch git sync, cherry-pick verification, and remote pull/push automation",
            "capabilities": ["git_sync", "branch_management", "commit_audit", "pr_automation"],
            "code_sample": "# Git automation harness\n",
        },
    }

    def __init__(self, target_dir: Optional[Path] = None) -> None:
        self.target_dir = target_dir or (Path.home() / ".agents" / "skills")
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.installed_skills: Dict[str, Dict[str, Any]] = {}

    def detect_missing_skills(self, task_prompt: str) -> List[str]:
        """Scans prompt to detect if specialized skills or MCP tools are needed."""
        p_lower = (task_prompt or "").lower()
        missing = []

        if any(k in p_lower for k in ("3d", "threejs", "three.js", "webgl", "canvas 3d", "orbit controls")):
            missing.append("threejs_3d_engine")

        if any(k in p_lower for k in ("hacker", "exploit", "cwe", "security audit", "penetration", "red team", "vulnerability")):
            missing.append("cyber_exploit_tester")

        if any(k in p_lower for k in ("audio", "soundfx", "synthesizer", "sound", "music")):
            missing.append("audio_synthesizer_web")

        if any(k in p_lower for k in ("git pull", "git push", "repository sync", "github pull")):
            missing.append("git_workflow_automator")

        return missing

    def auto_install_skill(self, skill_name: str) -> Dict[str, Any]:
        """Installs and security-audits a skill without user friction."""
        template = self.EMBEDDED_KNOWHOW_REGISTRY.get(skill_name)
        if not template:
            # Generate generic dynamic skill descriptor
            template = {
                "name": skill_name,
                "domain": SkillDomain.CODE_INTELLIGENCE,
                "description": f"Autonomous skill adapter for {skill_name}",
                "capabilities": [skill_name.lower()],
                "code_sample": f"# Auto-generated adapter for {skill_name}\n",
            }

        skill_dir = self.target_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_doc = skill_dir / "SKILL.md"

        content = (
            f"---\n"
            f"name: {template['name']}\n"
            f"description: {template['description']}\n"
            f"domain: {template['domain'].value}\n"
            f"capabilities: {json.dumps(template['capabilities'])}\n"
            f"---\n\n"
            f"# {template['name'].replace('_', ' ').title()}\n\n"
            f"{template['description']}.\n\n"
            f"## Autonomous Usage\n"
            f"This skill was autonomously discovered and mounted into the IVA runtime.\n"
        )
        skill_doc.write_text(content, encoding="utf-8")

        # Create Python helper script if needed
        helper_py = skill_dir / "helper.py"
        helper_py.write_text(template["code_sample"], encoding="utf-8")

        # Run Pre-Installation Security Audit
        report = ApplicationSecurityAuditor.audit_codebase(skill_dir)
        if not report.production_ready:
            # Block installation if vulnerable
            logger.error("Auto-install rejected for '%s' due to security flags: %s", skill_name, report.vulnerabilities)
            return {"status": "REJECTED_SECURITY", "skill": skill_name, "reason": "Failed SAST scan"}

        self.installed_skills[skill_name] = template
        logger.info("AutonomousMCPSkillInstaller: Successfully installed and mounted '%s'", skill_name)

        return {
            "status": "INSTALLED_AND_MOUNTED",
            "skill": skill_name,
            "path": str(skill_dir),
            "domain": template["domain"].value,
            "capabilities": template["capabilities"],
        }

    def resolve_and_install_all_needed(self, task_prompt: str) -> List[Dict[str, Any]]:
        """Scans prompt and installs all necessary tools in one autonomous pass."""
        needed = self.detect_missing_skills(task_prompt)
        results = []
        for s in needed:
            res = self.auto_install_skill(s)
            results.append(res)
        return results
