"""
posting_safety.py — the gate that stands between "generated" and "posted".

Design decision: posting defaults to **SAFE MODE** — a manual approval workflow
that updates local queue/log/calendar files and *never opens a network socket*.
Real publishing requires explicitly disabling safe mode AND a per-platform
unlock. Skeleton publishers refuse otherwise. This is a product decision, not a
missing feature: an always-on content engine should never auto-post by default.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PostingSafety:
    safe_mode: bool = True
    platform_unlocks: Optional[Dict[str, bool]] = None

    def queue_for_approval(self, asset: Any) -> Dict[str, Any]:
        """Stage an asset for a human to approve. Never posts."""
        return {
            "action": "queued_for_approval",
            "asset_id": getattr(asset, "asset_id", "?"),
            "format": getattr(asset, "format", "?"),
            "safe_mode": self.safe_mode,
            "note": "awaiting human approval — no network call made",
        }

    def can_publish(self, platform: str) -> bool:
        if self.safe_mode:
            return False
        return bool((self.platform_unlocks or {}).get(platform, False))

    def publish(self, asset: Any, platform: str) -> Dict[str, Any]:
        """Refuses unless safe mode is off AND the platform is unlocked."""
        if not self.can_publish(platform):
            return {
                "action": "refused",
                "platform": platform,
                "reason": "SAFE MODE on" if self.safe_mode else f"{platform} not unlocked",
            }
        # Real publisher omitted from this public subset.
        return {"action": "would_publish", "platform": platform,
                "asset_id": getattr(asset, "asset_id", "?")}
