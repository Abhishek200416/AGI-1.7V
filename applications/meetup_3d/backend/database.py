"""Meetup 3D Application — Thread-Safe Persistent Storage & Initial Data Seeds.
================================================================================
Manages meetup listings, attendee RSVPs, and 3D spatial anchors.
================================================================================
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Attendee, Coordinate3D, MeetupEvent


class MeetupRepository:
    """Thread-safe JSON repository for meetup records and RSVPs."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.storage_path = storage_path or (Path(__file__).resolve().parent / "meetups_data.json")
        self._lock = threading.Lock()
        self._events: Dict[str, MeetupEvent] = {}
        self._load_or_seed()

    def _seed_events(self) -> None:
        seeds = [
            MeetupEvent(
                event_id="meetup-01",
                title="Global Autonomous Agents & Cognitive AI Summit",
                subtitle="Frontier Multi-Agent Coordination, AST CI-Repair & Sovereign Lead Engineering",
                description="Join 250+ systems architects, lead AI researchers, and autonomous agent engineers for an intensive evening of technical demonstrations, real-time code synthesis, and multi-agent debate.",
                category="Autonomous Systems",
                date_str="Thursday, November 12, 2026",
                time_str="18:30 - 21:30 IST",
                location="Bengaluru Tech Pavilion & Global Live Stream",
                capacity=300,
                coordinates_3d=Coordinate3D(-3.5, 1.5, -2.0),
                glow_color="#00f0ff",
                tags=["Autonomous Agents", "AST Refactoring", "Cognitive Memory", "Multi-Agent"],
                attendees=[
                    Attendee("att-1", "Iva AI Partner", "iva@antigravity.internal"),
                    Attendee("att-2", "Abhishek Lead", "abhishek@operator.internal"),
                ],
            ),
            MeetupEvent(
                event_id="meetup-02",
                title="WebGL 3D Web & Immersive Experience Lab",
                subtitle="Three.js Shaders, 3D Scroll Rigging, and Spatial Canvas Engineering",
                description="Deep-dive into 60fps WebGL rendering pipelines, GPU compute shaders, camera spline interpolation, and building Apple-grade 3D scrolling interfaces for next-generation web applications.",
                category="WebGL & 3D",
                date_str="Saturday, November 21, 2026",
                time_str="17:00 - 20:00 IST",
                location="Creative Tech Foundry & Hybrid Virtual Stage",
                capacity=200,
                coordinates_3d=Coordinate3D(3.8, -1.0, -6.5),
                glow_color="#a855f7",
                tags=["Three.js", "WebGL", "3D Scrolling", "GLSL Shaders"],
                attendees=[
                    Attendee("att-3", "Elena Rostova", "elena@graphics.lab"),
                ],
            ),
            MeetupEvent(
                event_id="meetup-03",
                title="Institutional Quantitative Alpha & Microstructure Forum",
                subtitle="Multivariate Hawkes Processes, SVI Volatility Smiles, and High-Density Execution",
                description="Quantitative portfolio managers, algorithmic researchers, and derivative traders unpack order flow toxicity, tick-level microstructure, and friction-aware risk budgeting in Indian equity indices.",
                category="Quant Finance",
                date_str="Tuesday, December 01, 2026",
                time_str="19:00 - 21:45 IST",
                location="Financial District Exchange Center, Mumbai",
                capacity=150,
                coordinates_3d=Coordinate3D(-3.2, -3.8, -11.0),
                glow_color="#eab308",
                tags=["Hawkes Processes", "SVI Volatility", "Bayesian Kelly", "Microstructure"],
                attendees=[],
            ),
            MeetupEvent(
                event_id="meetup-04",
                title="Sovereign AI Founders Hackathon & Product Showcase",
                subtitle="Build, Deploy, and Pitch Autonomous Full-Stack Applications in 36 Hours",
                description="Fast-paced engineering hackathon where builders ship live, full-stack production systems powered by 100-specialist agent architectures with verified unit test suites and zero pip friction.",
                category="AI & ML",
                date_str="Friday - Sunday, December 11-13, 2026",
                time_str="Starts Friday 18:00 IST",
                location="Innovation Hub, Hyderabad & Global Discord",
                capacity=500,
                coordinates_3d=Coordinate3D(3.5, -6.2, -16.0),
                glow_color="#22c55e",
                tags=["Hackathon", "Full-Stack", "Fast Deployment", "Enterprise Architecture"],
                attendees=[
                    Attendee("att-4", "Marcus Vance", "marcus@founder.io"),
                ],
            ),
        ]
        self._events = {e.event_id: e for e in seeds}
        self._save()

    def _load_or_seed(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                loaded = {}
                for item in data.get("events", []):
                    coords = Coordinate3D(**item.get("coordinates_3d", {"x": 0, "y": 0, "z": 0}))
                    atts = [Attendee(**a) for a in item.get("attendees", [])]
                    item["coordinates_3d"] = coords
                    item["attendees"] = atts
                    item.pop("rsvp_count", None)
                    item.pop("is_full", None)
                    event = MeetupEvent(**item)
                    loaded[event.event_id] = event
                if loaded:
                    self._events = loaded
                    return
            except Exception:
                pass
        self._seed_events()

    def _save(self) -> None:
        data = {
            "events": [e.to_dict() for e in self._events.values()],
            "last_updated": time.time(),
        }
        self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_all_events(self) -> List[MeetupEvent]:
        with self._lock:
            return list(self._events.values())

    def get_event_by_id(self, event_id: str) -> Optional[MeetupEvent]:
        with self._lock:
            return self._events.get(event_id)

    def register_rsvp(self, event_id: str, name: str, email: str) -> Tuple[bool, str, Optional[Attendee]]:
        """Registers a user for a meetup event."""
        clean_name = (name or "").strip()
        clean_email = (email or "").strip().lower()

        if not clean_name or not clean_email or "@" not in clean_email:
            return (False, "Valid name and email address are required.", None)

        with self._lock:
            event = self._events.get(event_id)
            if not event:
                return (False, f"Event '{event_id}' not found.", None)

            if event.is_full:
                return (False, "Sorry, this event has reached full capacity.", None)

            for a in event.attendees:
                if a.email == clean_email:
                    return (False, "You are already registered for this meetup!", a)

            att_id = f"att-{int(time.time() * 1000)}"
            new_attendee = Attendee(
                attendee_id=att_id,
                name=clean_name,
                email=clean_email,
                registered_at=time.time(),
            )
            event.attendees.append(new_attendee)
            self._save()
            return (True, f"RSVP Confirmed for '{event.title}'!", new_attendee)
