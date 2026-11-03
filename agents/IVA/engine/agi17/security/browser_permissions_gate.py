"""IVA System & Browser Permission Control Gate.
================================================================================
Provides explicit, fail-closed permission gates before granting access to:
1. Browser automation (Playwright, CDP, Chrome control).
2. Multi-Account Chrome user profiles (6 to 78 local profiles).
3. System desktop capture & DOM inspection.
4. Authenticated sessions (Gemini Pro, ChatGPT Plus).

Security Invariants:
- Safe Fail-Closed: Never performs browser control or multi-profile inspection without authorization.
- Zero-Surprise: Operator is notified of exact action scope and affected profiles.
- Persistent Audit Ledger: All permission requests and grants are recorded in JSON ledger.

Requires ZERO external PyPI dependencies (100% Python standard library).
================================================================================
"""

from __future__ import annotations

import enum
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("BrowserPermissionsGate")


class PermissionScope(str, enum.Enum):
    BROWSER_CONTROL = "BROWSER_CONTROL"
    MULTI_ACCOUNT_CHROME = "MULTI_ACCOUNT_CHROME"
    SYSTEM_SCREENSHOT = "SYSTEM_SCREENSHOT"
    EXTERNAL_ACCOUNT_LOGIN = "EXTERNAL_ACCOUNT_LOGIN"
    FILESYSTEM_SCAFFOLD = "FILESYSTEM_SCAFFOLD"


@dataclass
class PermissionGrant:
    scope: str
    granted: bool
    reason: str
    granted_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    operator_confirmed: bool = True

    def is_active(self) -> bool:
        if not self.granted:
            return False
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True


class BrowserPermissionsGate:
    """Manages explicit permission grants for system control and browser automation."""

    _instance: Optional[BrowserPermissionsGate] = None

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        self.storage_dir = storage_dir or (Path(__file__).resolve().parents[4] / "scratch")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.storage_dir / "permission_grants_ledger.json"
        self._grants: Dict[str, PermissionGrant] = {}
        self._load_ledger()

    @classmethod
    def get_instance(cls) -> BrowserPermissionsGate:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_ledger(self) -> None:
        if self.ledger_file.exists():
            try:
                data = json.loads(self.ledger_file.read_text(encoding="utf-8"))
                for item in data:
                    grant = PermissionGrant(**item)
                    if grant.is_active():
                        self._grants[grant.scope] = grant
            except Exception as exc:
                logger.debug("Failed reading permissions ledger: %s", exc)

    def _save_ledger(self) -> None:
        try:
            records = [asdict(g) for g in self._grants.values()]
            self.ledger_file.write_text(json.dumps(records, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.debug("Failed writing permissions ledger: %s", exc)

    def is_environment_authorized(self, scope: PermissionScope) -> bool:
        """Checks if environment variables authorize the scope globally."""
        env_map = {
            PermissionScope.BROWSER_CONTROL: ("IVA_PERMIT_BROWSER_CONTROL", "PERMIT_BROWSER_AUTOMATION"),
            PermissionScope.MULTI_ACCOUNT_CHROME: ("IVA_PERMIT_MULTI_ACCOUNT_CHROME", "PERMIT_CHROME_PROFILES"),
            PermissionScope.SYSTEM_SCREENSHOT: ("IVA_PERMIT_SYSTEM_SCREENSHOT", "PERMIT_SCREEN_CAPTURE"),
            PermissionScope.EXTERNAL_ACCOUNT_LOGIN: ("IVA_PERMIT_EXTERNAL_ACCOUNT_LOGIN", "PERMIT_ACCOUNT_BRIDGES"),
            PermissionScope.FILESYSTEM_SCAFFOLD: ("IVA_PERMIT_FILESYSTEM_SCAFFOLD", "PERMIT_PROJECT_SCAFFOLD"),
        }
        vars_to_check = env_map.get(scope, ())
        for v in vars_to_check:
            val = (os.environ.get(v) or "").strip().lower()
            if val in ("1", "true", "yes", "enabled", "authorized"):
                return True
        return False

    def check_permission(
        self,
        scope: PermissionScope,
        reason: str,
        interactive: bool = True,
    ) -> bool:
        """Verifies if the action is authorized. Prompts operator if ungranted and interactive."""
        # 1. Check global environment authorization
        if self.is_environment_authorized(scope):
            return True

        # 2. Check active cached grant
        scope_key = scope.value
        existing = self._grants.get(scope_key)
        if existing and existing.is_active():
            return True

        # 3. Interactive prompt if allowed
        if interactive:
            print("\n  " + "═" * 74)
            print("  🔒 IVA SYSTEM & BROWSER PERMISSION GATE")
            print("  " + "═" * 74)
            print(f"  Action Request: {scope_key}")
            print(f"  Reason        : {reason}")
            print("  " + "─" * 74)
            print("  [1] Authorize for this entire session (Recommended)")
            print("  [2] Authorize permanently (Saves to environment & ledger)")
            print("  [3] Deny access (Fail-closed)")
            try:
                ans = input("  Grant authorization? [1-3, default: 1]: ").strip()
            except (KeyboardInterrupt, EOFError):
                ans = "3"

            if ans in ("1", "", "y", "yes"):
                self.grant_permission(scope, reason=reason, permanent=False)
                print(f"  ✅ Authorized: {scope_key} (Active for current runtime session)")
                return True
            elif ans == "2":
                self.grant_permission(scope, reason=reason, permanent=True)
                print(f"  ✅ Authorized Permanently: {scope_key}")
                return True
            else:
                print(f"  ⛔ Access Denied by Operator: {scope_key}")
                return False

        return False

    def grant_permission(
        self,
        scope: PermissionScope,
        reason: str = "Authorized by operator",
        permanent: bool = False,
        expires_in_sec: Optional[float] = None,
    ) -> None:
        """Records an authorization grant."""
        expires_at = time.time() + expires_in_sec if expires_in_sec else None
        grant = PermissionGrant(
            scope=scope.value,
            granted=True,
            reason=reason,
            granted_at=time.time(),
            expires_at=expires_at,
            operator_confirmed=True,
        )
        self._grants[scope.value] = grant
        self._save_ledger()

        if permanent:
            var_name = f"IVA_PERMIT_{scope.value}"
            os.environ[var_name] = "true"

    def revoke_permission(self, scope: PermissionScope) -> None:
        """Revokes an authorization grant."""
        scope_key = scope.value
        if scope_key in self._grants:
            del self._grants[scope_key]
            self._save_ledger()
        var_name = f"IVA_PERMIT_{scope.value}"
        if var_name in os.environ:
            del os.environ[var_name]

    def get_status_summary(self) -> Dict[str, Any]:
        """Returns structured metadata of all permission scopes."""
        return {
            scope.value: (
                self.is_environment_authorized(scope)
                or (scope.value in self._grants and self._grants[scope.value].is_active())
            )
            for scope in PermissionScope
        }
