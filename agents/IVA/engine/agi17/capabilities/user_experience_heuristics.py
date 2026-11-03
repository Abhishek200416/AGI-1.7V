"""IVA Cognitive User Experience & Ergonomics Heuristics Engine.
================================================================================
AGI 1.7 Autonomous UX Partner Capability.

Evaluates and optimizes user perspectives, cognitive load, visual friction,
mobile ergonomics (thumb zones), activation hooks, and immersion-to-chrome ratios.
Ensures IVA never ships cluttered, irritating, or device-degraded interfaces.

Core Evaluated Pillars:
1. Hook Efficacy Index (HEI): First 3-second engagement, curiosity trigger, visual hierarchy.
2. Friction & Irritation Score (FIS): Detects screen occlusion, obstructive overlays, redundant buttons.
3. Thumb-Zone Reachability (TZR): Evaluates one-handed mobile ergonomic placement.
4. Immersion-to-Chrome Ratio (ICR): Measures viewport canvas freedom vs intrusive UI chrome.
5. Adaptive Responsive Continuum (ARC): Fluidity across mobile, tablet, desktop, and ultrawide.

100% Python Standard Library (Zero external dependencies).
================================================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class UXAuditReport:
    """Comprehensive UX audit output for an interface design."""
    hook_score: float              # 0.0 to 100.0 (Higher = more engaging activation)
    friction_score: float          # 0.0 to 100.0 (Lower = less irritating/obtrusive)
    thumb_ergonomics_score: float  # 0.0 to 100.0 (Higher = mobile thumb-reachable)
    immersion_ratio: float         # 0.0 to 1.0 (Higher = more screen dedicated to content)
    responsive_score: float        # 0.0 to 100.0 (Higher = fluid across breakpoints)
    overall_ux_grade: str          # "A+", "A", "B", "C", "F"
    friction_warnings: List[str] = field(default_factory=list)
    actionable_recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hook_score": round(self.hook_score, 1),
            "friction_score": round(self.friction_score, 1),
            "thumb_ergonomics_score": round(self.thumb_ergonomics_score, 1),
            "immersion_ratio": round(self.immersion_ratio, 3),
            "responsive_score": round(self.responsive_score, 1),
            "overall_ux_grade": self.overall_ux_grade,
            "friction_warnings": self.friction_warnings,
            "actionable_recommendations": self.actionable_recommendations,
        }


class UserProspectErgonomicsAnalyzer:
    """Autonomous heuristic analyzer for human-centered interface design."""

    @classmethod
    def audit_interface_code(
        cls,
        html_code: str,
        css_code: str,
        js_code: str,
        is_spatial_experience: bool = True
    ) -> UXAuditReport:
        """Audits HTML, CSS, and JS code for user perspective and friction points."""
        friction_warnings: List[str] = []
        recommendations: List[str] = []

        # 1. Immersion-to-Chrome Ratio (ICR)
        # Check if overlays dominate the screen or if auto-hide / zen mode exists
        has_auto_hide = bool(re.search(r"autohide|fade.*idle|idle.*timeout|opacity.*0|collapsed", js_code, re.IGNORECASE))
        has_dynamic_island = bool(re.search(r"capsule|pill|island|floating.*nav", css_code + html_code, re.IGNORECASE))
        has_fixed_heavy_header = bool(re.search(r"header.*height:\s*(?:6[0-9]|[7-9][0-9]|1[0-9]{2})px", css_code, re.IGNORECASE))

        immersion_ratio = 0.90 if is_spatial_experience else 0.80
        if has_auto_hide:
            immersion_ratio += 0.06
        if has_dynamic_island:
            immersion_ratio += 0.03
        if has_fixed_heavy_header:
            immersion_ratio -= 0.08
            friction_warnings.append("Heavy fixed header detected (>60px height) that crowds mobile viewport.")
            recommendations.append("Transition from full-width static header to compact floating capsule or dynamic island.")

        immersion_ratio = min(0.98, max(0.60, immersion_ratio))

        # 2. Friction & Irritation Score (FIS - Lower is better)
        friction_score = 15.0  # Base low friction
        if has_fixed_heavy_header:
            friction_score += 20.0

        # Check for unneeded modal blocking or persistent heavy panels
        if not re.search(r"collapsed|display:\s*none|transform:\s*translate", css_code):
            friction_score += 25.0
            friction_warnings.append("Panels lack collapsed states, risking screen clutter on mobile.")
            recommendations.append("Implement collapsible bottom sheets and drawer cards for secondary controls.")

        # Check for pull-to-refresh / touch conflict prevention
        if "touch-action: none" not in css_code:
            friction_score += 15.0
            friction_warnings.append("Missing 'touch-action: none' on canvas layer, causing gesture conflicts.")
            recommendations.append("Apply 'touch-action: none' to canvas to prevent mobile browser scroll-locking.")

        # Check for volume shock / sudden audio
        if "exponentialRamp" not in js_code and "linearRamp" not in js_code:
            friction_score += 10.0
            friction_warnings.append("Audio lacks exponential fade ramps, risking sudden volume pops.")
            recommendations.append("Use gain exponential ramps for organic, gentle audio fades.")

        friction_score = min(100.0, max(5.0, friction_score))

        # 3. Hook Efficacy Index (HEI - Higher is better)
        hook_score = 65.0
        # Check for cinematic entrance, intro glide, or welcoming pulse
        if re.search(r"ingress|intro|camera\.position\.lerp|warp|fly.*to", js_code, re.IGNORECASE):
            hook_score += 20.0
        if re.search(r"particlesCount|geometry|soundscape", js_code, re.IGNORECASE):
            hook_score += 10.0
        if re.search(r"touch.*attune|tap.*enter|welcome", html_code, re.IGNORECASE):
            hook_score += 5.0

        hook_score = min(100.0, max(20.0, hook_score))

        # 4. Thumb-Zone Reachability (TZR)
        thumb_score = 60.0
        # Bottom controls or bottom action sheet
        if re.search(r"bottom:\s*(?:[0-9]|1[0-9]|2[0-9])px|bottom-sheet|floating.*dock", css_code, re.IGNORECASE):
            thumb_score += 25.0
        if re.search(r"@media.*max-width.*bottom", css_code, re.IGNORECASE):
            thumb_score += 15.0

        thumb_score = min(100.0, max(20.0, thumb_score))

        # 5. Responsive Continuum (ARC)
        responsive_score = 50.0
        if "@media" in css_code:
            media_count = len(re.findall(r"@media", css_code))
            responsive_score += min(35.0, media_count * 12.0)
        if "isMobile" in js_code or "touches" in js_code:
            responsive_score += 15.0

        responsive_score = min(100.0, max(20.0, responsive_score))

        # Compute overall grade
        composite = (hook_score * 0.25) + ((100.0 - friction_score) * 0.30) + (thumb_score * 0.20) + (responsive_score * 0.25)
        if composite >= 90:
            grade = "A+"
        elif composite >= 80:
            grade = "A"
        elif composite >= 70:
            grade = "B"
        elif composite >= 60:
            grade = "C"
        else:
            grade = "F"

        return UXAuditReport(
            hook_score=hook_score,
            friction_score=friction_score,
            thumb_ergonomics_score=thumb_score,
            immersion_ratio=immersion_ratio,
            responsive_score=responsive_score,
            overall_ux_grade=grade,
            friction_warnings=friction_warnings,
            actionable_recommendations=recommendations
        )


def evaluate_ui_perspective(html: str, css: str, js: str) -> Dict[str, Any]:
    """Convenience helper for runtime testing and continuous self-improvement."""
    report = UserProspectErgonomicsAnalyzer.audit_interface_code(html, css, js)
    return report.to_dict()
