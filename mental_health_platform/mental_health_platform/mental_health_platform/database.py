"""
database.py — Infrastructure Layer
Student Mental Health Support Platform
Universidad Distrital Francisco José de Caldas — 2026-I
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "platform.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables and seed initial data."""
    conn = get_connection()
    c = conn.cursor()

    # Users table (students + peer counselors + admin)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('student','peer_counselor','admin')),
            full_name   TEXT NOT NULL,
            anon_alias  TEXT UNIQUE NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            is_active   INTEGER DEFAULT 1
        )
    """)

    # Peer counselor profiles
    c.execute("""
        CREATE TABLE IF NOT EXISTS counselor_profiles (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER UNIQUE REFERENCES users(id),
            specialties     TEXT DEFAULT '',
            bio             TEXT DEFAULT '',
            sessions_done   INTEGER DEFAULT 0,
            available       INTEGER DEFAULT 1,
            max_sessions    INTEGER DEFAULT 20
        )
    """)

    # Matching requests
    c.execute("""
        CREATE TABLE IF NOT EXISTS match_requests (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      INTEGER REFERENCES users(id),
            counselor_id    INTEGER REFERENCES users(id),
            topic           TEXT NOT NULL,
            urgency         TEXT DEFAULT 'normal' CHECK(urgency IN ('low','normal','high')),
            status          TEXT DEFAULT 'pending' CHECK(status IN ('pending','active','closed')),
            created_at      TEXT DEFAULT (datetime('now'))
        )
    """)

    # Chat messages (anonymous)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id    INTEGER REFERENCES match_requests(id),
            sender_id   INTEGER REFERENCES users(id),
            content     TEXT NOT NULL,
            sent_at     TEXT DEFAULT (datetime('now'))
        )
    """)

    # Appointments with professional counselors
    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      INTEGER REFERENCES users(id),
            counselor_name  TEXT NOT NULL,
            date_time       TEXT NOT NULL,
            notes           TEXT DEFAULT '',
            status          TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled','completed','cancelled')),
            created_at      TEXT DEFAULT (datetime('now'))
        )
    """)

    # Resource library
    c.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            category    TEXT NOT NULL,
            content     TEXT NOT NULL,
            author      TEXT DEFAULT 'Platform Team',
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    _seed_data(conn)
    conn.close()


def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _seed_data(conn):
    c = conn.cursor()

    # Check if already seeded
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        return

    users = [
        ("admin",    _hash_password("admin123"),   "admin",          "Platform Admin",    "admin_sys"),
        ("student1", _hash_password("pass123"),    "student",        "Ana García",        "AnonStudent_01"),
        ("student2", _hash_password("pass123"),    "student",        "Carlos López",      "AnonStudent_02"),
        ("student3", _hash_password("pass123"),    "student",        "María Torres",      "AnonStudent_03"),
        ("peer1",    _hash_password("pass123"),    "peer_counselor", "Juan Pérez",        "PeerSupport_A"),
        ("peer2",    _hash_password("pass123"),    "peer_counselor", "Laura Gómez",       "PeerSupport_B"),
        ("peer3",    _hash_password("pass123"),    "peer_counselor", "Diego Ramírez",     "PeerSupport_C"),
    ]
    c.executemany(
        "INSERT INTO users (username, password, role, full_name, anon_alias) VALUES (?,?,?,?,?)",
        users
    )

    # Counselor profiles
    c.execute("SELECT id FROM users WHERE role='peer_counselor'")
    peer_ids = [r[0] for r in c.fetchall()]
    profiles = [
        (peer_ids[0], "Anxiety, Academic stress", "Psychology Student, 3rd year"),
        (peer_ids[1], "Mild depression, Loneliness",    "Social Work Student, 4th year"),
        (peer_ids[2], "Stress, Time management", "Engineering Student, 5th year"),
    ]
    c.executemany(
        "INSERT INTO counselor_profiles (user_id, specialties, bio) VALUES (?,?,?)",
        profiles
    )

    # Seed resources
    resources = [
        ("Breathing Techniques for Stress", "Anxiety",
         "Diaphragmatic breathing activates the parasympathetic nervous system...\n\n"
         "4-7-8 Technique:\n• Inhale through the nose for 4 seconds\n"
         "• Hold the breath for 7 seconds\n• Exhale slowly for 8 seconds\n"
         "• Repeat 4 times\n\nThis technique reduces cortisol and heart rate "
         "in minutes. Ideal before exams.", "Clinical Team"),

        ("Stress-Free Study Guide", "Academic Performance",
         "Proven strategies to study efficiently:\n\n"
         "• Pomodoro Technique: 25 min of studying + 5 min break\n"
         "• Mind maps to connect concepts\n"
         "• Spaced repetition: review material at 1, 3, 7, and 21 days\n"
         "• Quality sleep: sleep consolidates memory\n\n"
         "Remember: rest is part of the learning process.", "Academic Department"),

        ("How to Talk About Mental Health", "Support Resources",
         "Breaking the silence is the first step:\n\n"
         "• You are not alone: 88% of college students experience anxiety\n"
         "• Asking for help is strength, not weakness\n"
         "• Start with simple phrases: 'I have been feeling overwhelmed'\n"
         "• This platform guarantees your anonymity\n\n"
         "Additional resources:\n• Hotline 106 (Colombia) — 24/7 care\n"
         "• University Well-being — your faculty", "Well-being Team"),

        ("Mindfulness in 5 Minutes", "Well-being",
         "Mindfulness reduces anxiety by up to 40% with regular practice.\n\n"
         "Quick exercise:\n1. Sit comfortably and close your eyes\n"
         "2. Notice 5 things you can physically feel right now\n"
         "3. Observe your thoughts without judging them\n"
         "4. Gently return to the present when your mind wanders\n"
         "5. Take a deep breath and open your eyes\n\nPractice this every morning.", "Well-being"),

        ("Warning Signs and When to Seek Professional Help", "Crisis",
         "Recognize when you need additional support:\n\n"
         "Moderate signs (talk to a peer counselor):\n"
         "• Difficulty concentrating for more than 2 weeks\n"
         "• Changes in sleep or appetite\n• Constant feeling of emptiness\n\n"
         "Signs that require professional attention:\n"
         "• Thoughts of self-harm\n• Inability to perform daily activities\n"
         "• Frequent panic episodes\n\nIn case of a crisis call 106 now.", "Clinical Team"),
    ]
    c.executemany(
        "INSERT INTO resources (title, category, content, author) VALUES (?,?,?,?)",
        resources
    )

    conn.commit()


# ── User operations ────────────────────────────────────────────────────────────

def register_user(username, password, role, full_name, anon_alias, specialties="", bio=""):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password, role, full_name, anon_alias) VALUES (?,?,?,?,?)",
            (username, _hash_password(password), role, full_name, anon_alias)
        )
        user_id = c.lastrowid
        if role == "peer_counselor":
            c.execute(
                "INSERT INTO counselor_profiles (user_id, specialties, bio) VALUES (?,?,?)",
                (user_id, specialties, bio)
            )
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError as e:
        return False, "The user or alias already exists"
    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=? AND is_active=1",
        (username, _hash_password(password))
    )
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_available_counselors():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.anon_alias, cp.specialties, cp.bio, cp.sessions_done, cp.max_sessions
        FROM users u
        JOIN counselor_profiles cp ON u.id = cp.user_id
        WHERE u.role='peer_counselor' AND u.is_active=1
          AND cp.available=1 AND cp.sessions_done < cp.max_sessions
        ORDER BY cp.sessions_done ASC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Matching operations ────────────────────────────────────────────────────────

def create_match_request(student_id, counselor_id, topic, urgency="normal"):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO match_requests (student_id, counselor_id, topic, urgency, status) VALUES (?,?,?,?,'active')",
        (student_id, counselor_id, topic, urgency)
    )
    match_id = c.lastrowid
    c.execute("UPDATE counselor_profiles SET sessions_done = sessions_done + 1 WHERE user_id=?", (counselor_id,))
    conn.commit()
    conn.close()
    return match_id


def get_student_matches(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT mr.*, u.anon_alias as counselor_alias
        FROM match_requests mr
        JOIN users u ON mr.counselor_id = u.id
        WHERE mr.student_id=?
        ORDER BY mr.created_at DESC
    """, (student_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_counselor_matches(counselor_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT mr.*, u.anon_alias as student_alias
        FROM match_requests mr
        JOIN users u ON mr.student_id = u.id
        WHERE mr.counselor_id=? AND mr.status='active'
        ORDER BY mr.created_at DESC
    """, (counselor_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def close_match(match_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE match_requests SET status='closed' WHERE id=?", (match_id,))
    conn.commit()
    conn.close()


# ── Messaging operations ───────────────────────────────────────────────────────

def send_message(match_id, sender_id, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (match_id, sender_id, content) VALUES (?,?,?)",
        (match_id, sender_id, content)
    )
    conn.commit()
    conn.close()


def get_messages(match_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT m.content, m.sent_at, u.anon_alias, u.role
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.match_id=?
        ORDER BY m.sent_at ASC
    """, (match_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Appointment operations ─────────────────────────────────────────────────────

def create_appointment(student_id, counselor_name, date_time, notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO appointments (student_id, counselor_name, date_time, notes) VALUES (?,?,?,?)",
        (student_id, counselor_name, date_time, notes)
    )
    conn.commit()
    conn.close()


def get_student_appointments(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM appointments WHERE student_id=? ORDER BY date_time ASC",
        (student_id,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cancel_appointment(appt_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE appointments SET status='cancelled' WHERE id=?", (appt_id,))
    conn.commit()
    conn.close()


# ── Resource operations ────────────────────────────────────────────────────────

def get_all_resources(category=None):
    conn = get_connection()
    c = conn.cursor()
    if category:
        c.execute("SELECT * FROM resources WHERE category=? ORDER BY title", (category,))
    else:
        c.execute("SELECT * FROM resources ORDER BY category, title")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_resource_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM resources ORDER BY category")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def add_resource(title, category, content, author="Admin"):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO resources (title, category, content, author) VALUES (?,?,?,?)",
        (title, category, content, author)
    )
    conn.commit()
    conn.close()


# ── Admin / stats ──────────────────────────────────────────────────────────────

def get_platform_stats():
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM users WHERE role='student'");        stats["students"]     = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE role='peer_counselor'"); stats["counselors"]   = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM match_requests");                    stats["matches"]      = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM match_requests WHERE status='active'"); stats["active_matches"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM appointments WHERE status='scheduled'"); stats["appointments"]= c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM messages");                          stats["messages"]     = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM resources");                         stats["resources"]    = c.fetchone()[0]
    c.execute("SELECT AVG(sessions_done) FROM counselor_profiles");      stats["avg_load"]     = round(c.fetchone()[0] or 0, 1)
    conn.close()
    return stats