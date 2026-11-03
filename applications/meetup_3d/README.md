# 🌐 NexusMeet 3D — Spatial Engineering Meetups Application
## Enterprise Full-Stack 3D WebGL Application Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Runtime Dependencies](https://img.shields.io/badge/Dependencies-0_Required_(Stdlib)-brightgreen.svg)](../../pyproject.toml)
[![3D Engine](https://img.shields.io/badge/Graphics-Three.js_WebGL-blueviolet.svg)](https://threejs.org/)
[![REST Tests](https://img.shields.io/badge/Tests-4%2F4_Passing_(100%25)-success.svg)](tests/)

---

### 1. Executive Summary & Design Contract
**NexusMeet 3D** is an enterprise-grade, full-stack spatial web application engineered to showcase technical engineering gatherings, AI symposiums, and quantitative forums. It blends an asynchronous Python standard-library REST backend with a reactive 60fps Three.js WebGL canvas featuring smooth camera scroll rigging, glowing 3D meetup nodes, and interactive RSVP capabilities.

Designed following modern big-tech software engineering standards:
- **Clean Separation of Concerns**: Strict boundary between domain models, thread-safe persistence, REST routing, and client-side rendering.
- **Zero Third-Party PyPI Dependencies**: Built 100% on native Python standard library (`http.server`, `socketserver`, `json`, `dataclasses`).
- **Production 3D Graphics**: Camera spline interpolation, particle constellation, wireframe orbital rings, and dynamic lighting tied to meetup categories.
- **Fail-Closed Validation**: Automated pre-trade style checks on RSVP capacity, duplicate email prevention, and CORS headers.

---

### 2. Architecture & Directory Hierarchy
```text
applications/meetup_3d/
├── backend/
│   ├── __init__.py
│   ├── server.py              # Multi-threaded HTTP REST API & static file router (Port 8095)
│   ├── models.py              # Typed domain contracts (MeetupEvent, Attendee, Coordinate3D)
│   └── database.py            # Thread-safe persistent JSON repository with initial data seeds
├── frontend/
│   ├── index.html             # Semantic HTML5, accessible HUD header, 3D Canvas mount
│   ├── css/
│   │   └── styles.css         # Glassmorphic design system, CSS custom properties, responsive breakpoints
│   └── js/
│       ├── app.js             # Core application controller, REST API integration, RSVP state
│       └── three_scene.js     # Spatial Three.js scene manager, camera scroll rigging, node rotations
├── tests/
│   ├── __init__.py
│   └── test_backend_api.py    # Automated integration test suite (HTTP 200, RSVP flow, CORS)
├── run_app.py                 # Automated launcher script with browser auto-open
├── run_app.bat                # Windows 1-click batch launcher
└── README.md                  # This technical architecture document
```

---

### 3. REST API Contract

#### `GET /api/health`
Returns system heartbeat and active status.
```json
{
  "status": "UP",
  "service": "Meetup-3D-Enterprise-API",
  "version": "1.0.0",
  "timestamp": 1793693000.12
}
```

#### `GET /api/meetups`
Retrieves all registered meetup events with 3D spatial coordinates.
```json
{
  "success": true,
  "count": 4,
  "events": [
    {
      "event_id": "meetup-01",
      "title": "Global Autonomous Agents & Cognitive AI Summit",
      "subtitle": "Frontier Multi-Agent Coordination, AST CI-Repair & Sovereign Lead Engineering",
      "category": "Autonomous Systems",
      "date_str": "Thursday, November 12, 2026",
      "capacity": 300,
      "rsvp_count": 2,
      "coordinates_3d": { "x": -3.5, "y": 1.5, "z": -2.0 },
      "glow_color": "#00f0ff"
    }
  ]
}
```

#### `POST /api/meetups/<event_id>/rsvp`
Registers an attendee for an event.
- **Request Body**: `{"name": "Elena Rostova", "email": "elena@graphics.lab"}`
- **Success (HTTP 201)**:
```json
{
  "success": true,
  "message": "RSVP Confirmed for 'Global Autonomous Agents & Cognitive AI Summit'!",
  "attendee": {
    "attendee_id": "att-1793693000123",
    "name": "Elena Rostova",
    "email": "elena@graphics.lab"
  }
}
```
- **Error (HTTP 400)**: Duplicate email or capacity exhaustion.

---

### 4. How to Run & Verify

#### Launch Application:
- **Windows**:
  ```powershell
  py -3 applications/meetup_3d/run_app.py
  # Or double-click: applications/meetup_3d/run_app.bat
  ```
- **Linux / macOS**:
  ```bash
  python3 applications/meetup_3d/run_app.py
  ```

#### Run Automated Test Suite:
```powershell
py -3 -m unittest applications/meetup_3d/tests/test_backend_api.py
```
*(Runs 4 automated integration tests across health check, 3D coordinate validation, RSVP workflows, and static asset streaming).*
