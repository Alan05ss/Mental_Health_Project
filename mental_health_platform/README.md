# MindBridge — Student Mental Health Support Platform
## Course Project — Systems Analysis & Design 2026-I
### Universidad Distrital Francisco José de Caldas

---

## Team
| Name | Code |
|--------|--------|
| Alan Santiago Agudelo Sarmiento | 20222020170 |
| Juan David Cardozo Trujillo | 20231020155 |
| Julian Ernesto Romero Gutierrez | 20231020164 |
| Nicolas Alexander Sierra Contreras | 20222020197 |

**Professor:** Eng. Carlos Andrés Sierra, M.Sc.

---

## Description

Functional prototype of the **Student Mental Health Support Platform**, implementing
all the modules designed in the previous Workshops:

| Module | Origin Workshop | Status |
|--------|----------------|--------|
| Registration and authentication | W2 — User Registration | ✅ Implemented |
| Peer counselor matching | W2 — Matching Engine | ✅ Implemented |
| Anonymous chat | W2 — Anonymous Communication | ✅ Implemented |
| Appointment scheduling | W2 — Appointment Scheduling | ✅ Implemented |
| Resource library | W2 — Resource Library | ✅ Implemented |
| Admin dashboard | W3 — Monitoring & Quality | ✅ Implemented |

---

## Requirements

- Python 3.8 or higher
- `tkinter` library (included in standard Python on Windows/macOS)
- On Ubuntu/Debian: `sudo apt install python3-tk`

---

## Installation and execution

```bash
# 1. Clone or unzip the project
cd mental_health_platform

# 2. (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Run
python3 app.py

The SQLite database (data/platform.db) is automatically created with test data.
---

## Demo accounts

| Username | Password | Role |
|---------|-----------|-----|
| `student1` | `pass123` | Student |
| `student2` | `pass123` | Student |
| `peer1`    | `pass123` | Peer counselor |
| `peer2`    | `pass123` | Peer counselor |
| `admin`    | `admin123` | Administrator |

---

## Arquitectura del prototipo

```
mental_health_platform/
├── app.py          ← Graphical interface (Tkinter) — Presentation Layer
├── database.py     ← Data logic (SQLite) — Application and Infrastructure Layers
├── data/
│   └── platform.db ← SQLite database (automatically generated)
└── README.md
```

### Architectural layers (Workshop 2)

```
┌─────────────────────────────────────────────────┐
│  PRESENTATION  →  app.py (Tkinter GUI)          │
│  • AuthWindow  • MainApp  • Views per module    │
├─────────────────────────────────────────────────┤
│  APPLICATION   →  Modules in app.py + db ops    │
│  • Matching Engine (greedy lowest-load)         │
│  • Anonymous Chat  • Appointment Scheduler      │
│  • Resource Library  • Admin Dashboard          │
├─────────────────────────────────────────────────┤
│  INFRASTRUCTURE →  database.py (SQLite)         │
│  • 6 relational tables  • SHA-256 Hashing       │
│  • Seed data  • Real-time Stats                 │
└─────────────────────────────────────────────────┘
```

---

## Workshop 4 Parameters (validated in the prototype)

```python
NUM_STUDENTS         = 3   (demo, scalable)
NUM_PEER_COUNSELORS  = 3   (demo, scalable)
BURNOUT_THRESHOLD    = 20  sessions per counselor
TRUST_LEVEL          = 0.85 (anonymous aliases + password hashing)
```

The Admin Dashboard shows in real-time:

-Average counselor load vs burnout threshold
-Active match rate
-Validation of all architecture modules

---

## Main system flow

```
Student → Registration/Login → Matching (greedy lowest-load)
        → Anonymous chat ↔ Peer counselor
        → Professional appointment (scheduling)
        → Resource library
```

---

## Implemented privacy principles

-✅ SHA-256 password hashing (never in plain text)
-✅ Anonymous aliases separated from the real name
-✅ Privacy reminder on the home screen
-✅ Chat identified only by alias, not by name
-✅ Local database (no data sent to external servers)

---

## Repository

https://github.com/Alan05ss/Mental_Health_Project.git

---

## References

- ISO/IEC 25010:2011 — Software Quality Models
- NIST Privacy Framework (2020)
- Workshops 1–4, Ing. Carlos A. Sierra, UDFJC 2026-I
