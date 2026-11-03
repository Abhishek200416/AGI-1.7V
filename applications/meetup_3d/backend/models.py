"""Meetup 3D Application — Domain Data Models.
================================================================================
Typed data contracts for events, locations, 3D spatial anchors, and attendees.
================================================================================
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Coordinate3D:
    x: float
    y: float
    z: float


@dataclass
class Attendee:
    attendee_id: str
    name: str
    email: str
    registered_at: float = field(default_factory=time.time)


@dataclass
class MeetupEvent:
    event_id: str
    title: str
    subtitle: str
    description: str
    category: str  # "AI & ML", "WebGL & 3D", "Quant Finance", "Autonomous Systems"
    date_str: str
    time_str: str
    location: str
    capacity: int
    attendees: List[Attendee] = field(default_factory=list)
    coordinates_3d: Coordinate3D = field(default_factory=lambda: Coordinate3D(0.0, 0.0, 0.0))
    glow_color: str = "#00f0ff"
    tags: List[str] = field(default_factory=list)

    @property
    def rsvp_count(self) -> int:
        return len(self.attendees)

    @property
    def is_full(self) -> bool:
        return len(self.attendees) >= self.capacity

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["rsvp_count"] = self.rsvp_count
        d["is_full"] = self.is_full
        return d
