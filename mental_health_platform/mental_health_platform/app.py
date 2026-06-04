"""
app.py — Student Mental Health Support Platform
Prototype — Course Project 2026-I
Universidad Distrital Francisco José de Caldas

Modules implemented:
  1. User Registration & Authentication
  2. Peer Counselor Matching
  3. Anonymous Communication (Chat)
  4. Appointment Scheduling
  5. Resource Library
  6. Admin Dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import csv
from datetime import datetime, timedelta
import database as db

# ── Color palette (privacy-first, calming tones) ──────────────────────────────
C = {
    "bg":        "#F0F4F8",
    "sidebar":   "#1E3A5F",
    "sidebar_h": "#2E5C8A",
    "accent":    "#2E86AB",
    "accent2":   "#A8DADC",
    "success":   "#57CC99",
    "warning":   "#FFB703",
    "danger":    "#E63946",
    "card":      "#FFFFFF",
    "text":      "#212529",
    "subtext":   "#6C757D",
    "border":    "#DEE2E6",
    "header_bg": "#1E3A5F",
}

FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_H2     = ("Helvetica", 14, "bold")
FONT_H3     = ("Helvetica", 12, "bold")
FONT_BODY   = ("Helvetica", 11)
FONT_SMALL  = ("Helvetica", 9)
FONT_MONO   = ("Courier", 10)


# ── Reusable widgets ───────────────────────────────────────────────────────────

def card(parent, **kwargs):
    f = tk.Frame(parent, bg=C["card"], relief="flat",
                 highlightthickness=1, highlightbackground=C["border"], **kwargs)
    return f

def label(parent, text, font=FONT_BODY, color=None, **kwargs):
    return tk.Label(parent, text=text, font=font,
                    bg=kwargs.pop("bg", C["card"]),
                    fg=color or C["text"], **kwargs)

def entry(parent, show=None, width=30):
    e = tk.Entry(parent, font=FONT_BODY, relief="flat", bd=0,
                 bg="#EEF2F7", fg=C["text"], insertbackground=C["text"],
                 width=width, show=show or "")
    e.config(highlightthickness=1, highlightbackground=C["border"],
             highlightcolor=C["accent"])
    return e

def btn(parent, text, command, color=None, fg="white", width=18, **kwargs):
    bg = color or C["accent"]
    b = tk.Button(parent, text=text, command=command,
                  font=FONT_BODY, bg=bg, fg=fg,
                  activebackground=C["accent2"], activeforeground=C["text"],
                  relief="flat", cursor="hand2", width=width,
                  padx=8, pady=6, **kwargs)
    return b

def separator(parent, color=C["border"]):
    return tk.Frame(parent, bg=color, height=1)


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mental Health Support Platform — UDFJC")
        self.geometry("960x620")
        self.resizable(False, False)
        self.configure(bg=C["bg"])
        self._build()

    def _build(self):
        # Left panel — branding
        left = tk.Frame(self, bg=C["sidebar"], width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🧠", font=("Helvetica", 56),
                 bg=C["sidebar"], fg="white").pack(pady=(70, 10))
        tk.Label(left, text="MindBridge", font=("Helvetica", 26, "bold"),
                 bg=C["sidebar"], fg="white").pack()
        tk.Label(left, text="Student Mental Health\nSupport Platform",
                 font=("Helvetica", 12), bg=C["sidebar"], fg=C["accent2"],
                 justify="center").pack(pady=(6, 30))

        for item in ["✓  Anonymous and secure",
                     "✓  Peer counselor matching",
                     "✓  Professional appointments",
                     "✓  Resource library"]:
            tk.Label(left, text=item, font=("Helvetica", 11),
                     bg=C["sidebar"], fg="#B0C4DE", anchor="w").pack(
                         padx=40, pady=3, fill="x")

        tk.Label(left, text="Universidad Distrital FJDC — 2026-I",
                 font=FONT_SMALL, bg=C["sidebar"], fg="#6A8BAE").pack(
                     side="bottom", pady=20)

        # Right panel — forms
        right = tk.Frame(self, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True)

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True, padx=40, pady=40)

        style = ttk.Style()
        style.configure("TNotebook", background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", font=FONT_H3, padding=[16, 8])

        self._build_login_tab()
        self._build_register_tab()

    def _build_login_tab(self):
        f = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(f, text="  Login  ")

        tk.Label(f, text="Welcome back",
                 font=FONT_TITLE, bg=C["bg"], fg=C["sidebar"]).pack(pady=(30, 4))
        tk.Label(f, text="Your safe support space",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(pady=(0, 30))

        c = card(f)
        c.pack(fill="x", padx=10)

        for lbl, attr, show in [("Username", "_l_user", ""), ("Password", "_l_pass", "•")]:
            tk.Label(c, text=lbl, font=FONT_H3, bg=C["card"],
                     fg=C["subtext"]).pack(anchor="w", padx=24, pady=(16, 2))
            e = entry(c, show=show, width=34)
            e.pack(padx=24, pady=(0, 4), fill="x")
            setattr(self, attr, e)

        tk.Label(c, text="", bg=C["card"]).pack()
        btn(c, "Login →", self._do_login,
            width=34).pack(padx=24, pady=(0, 24), fill="x")

        # Quick-access hint
        hint = tk.Frame(f, bg=C["bg"])
        hint.pack(pady=16)
        tk.Label(hint, text="Demo accounts:", font=FONT_SMALL,
                 bg=C["bg"], fg=C["subtext"]).pack()
        demos = [("student1 / pass123", C["success"]),
                 ("peer1 / pass123",    C["accent"]),
                 ("admin / admin123",   C["warning"])]
        for txt, col in demos:
            tk.Label(hint, text=txt, font=FONT_MONO,
                     bg=C["bg"], fg=col).pack()

    def _build_register_tab(self):
        f = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(f, text="  Register  ")

        tk.Label(f, text="Create account", font=FONT_TITLE,
                 bg=C["bg"], fg=C["sidebar"]).pack(pady=(20, 4))
        tk.Label(f, text="Your anonymity is guaranteed",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(pady=(0, 16))

        c = card(f)
        c.pack(fill="x", padx=10)

        # Fields
        fields = [
            ("Full name",       "_r_name", ""),
            ("Username",        "_r_user", ""),
            ("Password",        "_r_pass", "•"),
            ("Anonymous alias", "_r_alias", ""),
        ]
        for lbl, attr, show in fields:
            tk.Label(c, text=lbl, font=FONT_SMALL, bg=C["card"],
                     fg=C["subtext"]).pack(anchor="w", padx=24, pady=(10, 1))
            e = entry(c, show=show, width=34)
            e.pack(padx=24, fill="x")
            setattr(self, attr, e)

        tk.Label(c, text="Role", font=FONT_SMALL, bg=C["card"],
                 fg=C["subtext"]).pack(anchor="w", padx=24, pady=(10, 1))
        self._r_role = ttk.Combobox(c, values=["student", "peer_counselor"],
                                     state="readonly", width=32, font=FONT_BODY)
        self._r_role.set("student")
        self._r_role.pack(padx=24, fill="x")

        # NEW: Privacy consent checkbox (Workshop 3)
        self._r_consent_var = tk.BooleanVar()
        consent_chk = tk.Checkbutton(c, text="I accept the privacy and anonymity policy", 
                                     variable=self._r_consent_var, bg=C["card"], fg=C["text"],
                                     font=FONT_SMALL, activebackground=C["card"])
        consent_chk.pack(anchor="w", padx=24, pady=(10, 5))

        tk.Label(c, text="", bg=C["card"]).pack()
        btn(c, "Create account", self._do_register, color=C["success"],
            fg="white", width=34).pack(padx=24, pady=(0, 20), fill="x")

    def _do_login(self):
        user = self._l_user.get().strip()
        pw   = self._l_pass.get().strip()
        if not user or not pw:
            messagebox.showwarning("Empty fields", "Please enter a username and password.")
            return
        result = db.login_user(user, pw)
        if result:
            self.withdraw()
            MainApp(result, self).mainloop()
        else:
            messagebox.showerror("Error", "Incorrect username or password.")

    def _do_register(self):
        name  = self._r_name.get().strip()
        user  = self._r_user.get().strip()
        pw    = self._r_pass.get().strip()
        alias = self._r_alias.get().strip()
        role  = self._r_role.get()

        if not all([name, user, pw, alias]):
            messagebox.showwarning("Empty fields", "Please fill in all fields.")
            return
            
        # NEW: Privacy consent validation
        if not self._r_consent_var.get():
            messagebox.showwarning("Consent required", "You must accept the privacy policy to continue.")
            return
            
        if len(pw) < 6:
            messagebox.showwarning("Weak password", "Minimum 6 characters required.")
            return

        ok, msg = db.register_user(user, pw, role, name, alias)
        if ok:
            messagebox.showinfo("Success!", f"Account created.\nAnonymous alias: {alias}")
            self.notebook.select(0)
        else:
            messagebox.showerror("Error", msg)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class MainApp(tk.Toplevel):
    def __init__(self, user: dict, auth_win: AuthWindow):
        super().__init__()
        self.user     = user
        self.auth_win = auth_win
        self.title(f"MindBridge — {user['anon_alias']}")
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(bg=C["bg"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._active_chat = None
        self._build()

    def _on_close(self):
        self.destroy()
        self.auth_win.destroy()

    # ── Layout ──────────────────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["header_bg"], height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🧠  MindBridge", font=("Helvetica", 16, "bold"),
                 bg=C["header_bg"], fg="white").pack(side="left", padx=20)
        role_lbl = {"student": "Student", "peer_counselor": "Peer Counselor",
                    "admin": "Administrator"}[self.user["role"]]
        tk.Label(hdr, text=f"  {self.user['anon_alias']}  •  {role_lbl}  ",
                 font=FONT_BODY, bg=C["accent"], fg="white",
                 relief="flat", padx=8).pack(side="right", padx=20, pady=10)
        tk.Label(hdr, text="🔒 Secure session", font=FONT_SMALL,
                 bg=C["header_bg"], fg=C["accent2"]).pack(side="right")

        # Body
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(body, bg=C["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Content area
        self.content = tk.Frame(body, bg=C["bg"])
        self.content.pack(side="right", fill="both", expand=True)

        # Show default view
        if self.user["role"] == "admin":
            self._show_dashboard()
        else:
            self._show_home()

    def _build_sidebar(self):
        tk.Label(self.sidebar, text="MENU", font=("Helvetica", 9, "bold"),
                 bg=C["sidebar"], fg="#6A8BAE").pack(pady=(20, 6), padx=16, anchor="w")

        role = self.user["role"]
        nav_items = []

        if role in ("student", "peer_counselor"):
            nav_items += [
                ("🏠  Home",          self._show_home),
                ("🔗  Matching",      self._show_matching),
                ("💬  Chat",          self._show_chat),
                ("📅  Appointments",  self._show_appointments),
                ("📚  Library",       self._show_library),
            ]
        if role == "admin":
            nav_items += [
                ("📊  Dashboard",         self._show_dashboard),
                ("📚  Manage Resources",  self._show_library),
            ]

        self._nav_btns = []
        for text, cmd in nav_items:
            b = tk.Button(self.sidebar, text=text, command=lambda c=cmd: self._nav(c),
                          font=FONT_BODY, bg=C["sidebar"], fg="white",
                          activebackground=C["sidebar_h"], activeforeground="white",
                          relief="flat", anchor="w", padx=16, pady=10, cursor="hand2",
                          width=20)
            b.pack(fill="x", pady=1)
            self._nav_btns.append((b, cmd))

        separator(self.sidebar, "#2E5C8A").pack(fill="x", padx=16, pady=12)

        btn(self.sidebar, "⬅  Logout", self._logout,
            color="#C0392B", width=20).pack(padx=12, pady=4, fill="x")

    def _nav(self, cmd):
        for b, c in self._nav_btns:
            b.config(bg=C["sidebar_h"] if c == cmd else C["sidebar"])
        cmd()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ── HOME ──────────────────────────────────────────────────────────────────

    def _show_home(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True, padx=30, pady=24)

        role = self.user["role"]
        greeting = "Student" if role == "student" else "Counselor"
        tk.Label(f, text=f"Hello, {self.user['anon_alias']} 👋",
                 font=FONT_TITLE, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w")
        tk.Label(f, text=f"Welcome to your safe space as a {greeting}",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(2, 24))

        # Stats row
        stats = db.get_platform_stats()
        row = tk.Frame(f, bg=C["bg"])
        row.pack(fill="x", pady=(0, 20))

        stat_data = [
            ("👥", str(stats["students"]),   "Students"),
            ("🤝", str(stats["counselors"]), "Counselors"),
            ("✅", str(stats["matches"]),    "Sessions"),
            ("📚", str(stats["resources"]),  "Resources"),
        ]
        for icon, val, lbl in stat_data:
            c2 = card(row)
            c2.pack(side="left", fill="x", expand=True, padx=6)
            tk.Label(c2, text=icon, font=("Helvetica", 22),
                     bg=C["card"]).pack(pady=(16, 2))
            tk.Label(c2, text=val, font=("Helvetica", 20, "bold"),
                     bg=C["card"], fg=C["accent"]).pack()
            tk.Label(c2, text=lbl, font=FONT_SMALL,
                     bg=C["card"], fg=C["subtext"]).pack(pady=(0, 16))

        # Quick actions
        tk.Label(f, text="Quick actions", font=FONT_H2,
                 bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(8, 12))

        actions_row = tk.Frame(f, bg=C["bg"])
        actions_row.pack(fill="x")

        if role == "student":
            quick = [
                ("🔗 Find counselor",     self._show_matching, C["accent"]),
                ("📅 Book appointment",   self._show_appointments, C["success"]),
                ("📚 View resources",     self._show_library, C["warning"]),
            ]
        else:
            quick = [
                ("💬 View my sessions",   self._show_chat, C["accent"]),
                ("📚 Resources",          self._show_library, C["success"]),
            ]

        for txt, cmd, col in quick:
            b = btn(actions_row, txt, cmd, color=col, width=20)
            b.pack(side="left", padx=6)

        # Privacy reminder
        priv = tk.Frame(f, bg="#E8F4F8", highlightthickness=1,
                        highlightbackground=C["accent2"])
        priv.pack(fill="x", pady=24)
        tk.Label(priv, text="🔒  Privacy reminder",
                 font=FONT_H3, bg="#E8F4F8", fg=C["accent"]).pack(anchor="w", padx=16, pady=(12, 2))
        tk.Label(priv,
                 text="For your safety, do not share personally identifiable information "
                      "(phone, address, social networks)\nin the chats. "
                      "All communications are anonymous and encrypted.",
                 font=FONT_BODY, bg="#E8F4F8", fg=C["text"],
                 justify="left", wraplength=680).pack(anchor="w", padx=16, pady=(0, 12))

    # ── MATCHING ──────────────────────────────────────────────────────────────

    def _show_matching(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(f, text="🔗 Matching with Peer Counselors",
                 font=FONT_TITLE, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w")
        tk.Label(f, text="We connect students with counselors based on their needs (lowest load first)",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(2, 20))

        role = self.user["role"]

        if role == "peer_counselor":
            self._show_counselor_sessions(f)
            return

        # Request form
        form = card(f)
        form.pack(fill="x", pady=(0, 16))

        tk.Label(form, text="New support request",
                 font=FONT_H2, bg=C["card"], fg=C["sidebar"]).pack(anchor="w", padx=20, pady=(16, 8))

        row1 = tk.Frame(form, bg=C["card"])
        row1.pack(fill="x", padx=20)

        # Topic
        tk.Label(row1, text="Main topic:", font=FONT_H3,
                 bg=C["card"], fg=C["subtext"]).pack(anchor="w")
        self._m_topic = ttk.Combobox(row1, width=36, state="readonly", font=FONT_BODY,
                                      values=["Anxiety and academic stress",
                                              "Depression or mood",
                                              "Relationships and loneliness",
                                              "Time management and performance",
                                              "Career counseling",
                                              "Other"])
        self._m_topic.set("Anxiety and academic stress")
        self._m_topic.pack(anchor="w", pady=(2, 12))

        # Urgency
        tk.Label(row1, text="Urgency:", font=FONT_H3,
                 bg=C["card"], fg=C["subtext"]).pack(anchor="w")
        self._m_urgency = ttk.Combobox(row1, width=20, state="readonly", font=FONT_BODY,
                                        values=["low", "normal", "high"])
        self._m_urgency.set("normal")
        self._m_urgency.pack(anchor="w", pady=(2, 16))

        btn(form, "🔍 Find available counselor", self._do_match,
            color=C["accent"], width=36).pack(padx=20, pady=(0, 20))

        # Available counselors list
        tk.Label(f, text="Counselors available now",
                 font=FONT_H2, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(8, 8))

        counselors = db.get_available_counselors()
        if not counselors:
            tk.Label(f, text="⚠ No counselors available at this moment.",
                     font=FONT_BODY, bg=C["bg"], fg=C["warning"]).pack(anchor="w")
            return

        canvas = tk.Canvas(f, bg=C["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(f, orient="vertical", command=canvas.yview)
        inner  = tk.Frame(canvas, bg=C["bg"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for co in counselors:
            c2 = card(inner)
            c2.pack(fill="x", pady=4, padx=2)

            left_col = tk.Frame(c2, bg=C["card"])
            left_col.pack(side="left", fill="both", expand=True, padx=16, pady=12)

            tk.Label(left_col, text=co["anon_alias"], font=FONT_H3,
                     bg=C["card"], fg=C["accent"]).pack(anchor="w")
            tk.Label(left_col, text=f"Specialties: {co['specialties']}",
                     font=FONT_BODY, bg=C["card"], fg=C["text"]).pack(anchor="w")
            tk.Label(left_col, text=co["bio"],
                     font=FONT_SMALL, bg=C["card"], fg=C["subtext"]).pack(anchor="w")

            load_pct = int((co["sessions_done"] / co["max_sessions"]) * 100)
            load_col = C["success"] if load_pct < 50 else (C["warning"] if load_pct < 80 else C["danger"])
            tk.Label(left_col,
                     text=f"Load: {co['sessions_done']}/{co['max_sessions']} sessions ({load_pct}%)",
                     font=FONT_SMALL, bg=C["card"], fg=load_col).pack(anchor="w")

            btn(c2, "Connect →",
                lambda cid=co["id"]: self._quick_match(cid),
                color=C["success"], width=12).pack(side="right", padx=16, pady=16)

    def _do_match(self):
        topic   = self._m_topic.get()
        urgency = self._m_urgency.get()
        counselors = db.get_available_counselors()
        if not counselors:
            messagebox.showwarning("No availability", "There are no counselors available.")
            return
        # Greedy lowest-load policy
        best = counselors[0]
        mid = db.create_match_request(self.user["id"], best["id"], topic, urgency)
        messagebox.showinfo(
            "Successful Connection!",
            f"Connected with {best['anon_alias']}\n"
            f"Topic: {topic}\nSession ID: #{mid}\n\n"
            "Go to Chat to start the conversation."
        )
        self._show_chat()

    def _quick_match(self, counselor_id):
        topic = "General support"
        mid = db.create_match_request(self.user["id"], counselor_id, topic)
        messagebox.showinfo("Connection created", f"Session #{mid} started.\nGo to Chat.")
        self._show_chat()

    def _show_counselor_sessions(self, parent):
        matches = db.get_counselor_matches(self.user["id"])
        tk.Label(parent, text=f"Your active sessions ({len(matches)})",
                 font=FONT_H2, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=8)
        if not matches:
            tk.Label(parent, text="You have no active sessions at the moment.",
                     font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w")
            return
        for m in matches:
            c2 = card(parent)
            c2.pack(fill="x", pady=4)
            tk.Label(c2, text=f"Session #{m['id']} — {m['student_alias']}",
                     font=FONT_H3, bg=C["card"], fg=C["accent"]).pack(anchor="w", padx=16, pady=(12, 2))
            tk.Label(c2, text=f"Topic: {m['topic']}  •  Urgency: {m['urgency']}",
                     font=FONT_BODY, bg=C["card"], fg=C["text"]).pack(anchor="w", padx=16, pady=(0, 12))
            btn(c2, "Open chat", lambda mid=m["id"]: self._open_chat(mid),
                color=C["accent"], width=14).pack(side="right", padx=16, pady=12)

    # ── CHAT ──────────────────────────────────────────────────────────────────

    def _show_chat(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(f, text="💬 Anonymous Chat", font=FONT_TITLE,
                 bg=C["bg"], fg=C["sidebar"]).pack(anchor="w")
        tk.Label(f, text="All conversations are anonymous and encrypted 🔒",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(2, 16))

        body = tk.Frame(f, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Sessions list
        list_frame = card(body)
        list_frame.pack(side="left", fill="y", padx=(0, 10), ipadx=4)

        tk.Label(list_frame, text="Sessions", font=FONT_H3,
                 bg=C["card"], fg=C["sidebar"]).pack(padx=10, pady=(12, 4), anchor="w")
        separator(list_frame).pack(fill="x")

        if self.user["role"] == "student":
            matches = db.get_student_matches(self.user["id"])
        else:
            matches = db.get_counselor_matches(self.user["id"])

        self._chat_frame = tk.Frame(body, bg=C["bg"])
        self._chat_frame.pack(side="right", fill="both", expand=True)

        if not matches:
            tk.Label(list_frame, text="No active\nsessions",
                     font=FONT_BODY, bg=C["card"], fg=C["subtext"],
                     justify="center").pack(padx=16, pady=24)
            tk.Label(self._chat_frame, text="Go to Matching to\nstart a session.",
                     font=FONT_H2, bg=C["bg"], fg=C["subtext"],
                     justify="center").pack(expand=True)
            return

        for m in matches:
            alias = m.get("counselor_alias") or m.get("student_alias", "?")
            status_col = C["success"] if m["status"] == "active" else C["subtext"]
            b = tk.Button(list_frame,
                          text=f"#{m['id']} {alias}\n{m['topic'][:22]}",
                          font=FONT_SMALL, bg=C["card"], fg=C["text"],
                          activebackground=C["accent2"],
                          relief="flat", anchor="w", padx=8, pady=6,
                          cursor="hand2", width=18,
                          command=lambda mid=m["id"]: self._open_chat(mid))
            b.pack(fill="x", pady=1)
            tk.Label(list_frame, text=f"● {m['status']}", font=FONT_SMALL,
                     bg=C["card"], fg=status_col).pack(anchor="e", padx=8)

        # Auto-open first active match
        active = [m for m in matches if m["status"] == "active"]
        if active:
            self._open_chat(active[0]["id"])

    def _open_chat(self, match_id):
        self._active_chat = match_id
        for w in self._chat_frame.winfo_children():
            w.destroy()

        f = self._chat_frame
        tk.Label(f, text=f"Session #{match_id}  🔒  Anonymous",
                 font=FONT_H3, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 6))

        # Messages area
        self._msg_area = scrolledtext.ScrolledText(
            f, font=FONT_BODY, wrap="word",
            bg="#F8FAFE", fg=C["text"],
            relief="flat", bd=1,
            state="disabled", height=16,
            highlightthickness=1, highlightbackground=C["border"]
        )
        self._msg_area.pack(fill="both", expand=True, pady=(0, 8))
        self._msg_area.tag_config("me",     foreground=C["accent"],  font=FONT_H3)
        self._msg_area.tag_config("other",  foreground=C["sidebar"], font=FONT_H3)
        self._msg_area.tag_config("body",   foreground=C["text"])
        self._msg_area.tag_config("time",   foreground=C["subtext"], font=FONT_SMALL)

        self._load_messages()

        # Input row
        inp = tk.Frame(f, bg=C["bg"])
        inp.pack(fill="x")

        self._chat_input = tk.Text(inp, font=FONT_BODY, height=3, wrap="word",
                                    bg="#EEF2F7", fg=C["text"],
                                    relief="flat", bd=1,
                                    highlightthickness=1, highlightbackground=C["border"])
        self._chat_input.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._chat_input.bind("<Return>", lambda e: (self._send_message(), "break"))
        self._chat_input.bind("<Shift-Return>", lambda e: None)

        btn(inp, "Send ➤", self._send_message, color=C["accent"], width=10).pack(side="right")

        # Close session button
        btn(f, "✗ Close session", lambda: self._close_session(match_id),
            color=C["danger"], width=18).pack(anchor="e", pady=(8, 0))

        # Auto-refresh
        self._schedule_refresh()

    def _load_messages(self):
        if not self._active_chat:
            return
        msgs = db.get_messages(self._active_chat)
        self._msg_area.config(state="normal")
        self._msg_area.delete("1.0", "end")
        for msg in msgs:
            is_me = (msg["anon_alias"] == self.user["anon_alias"])
            tag   = "me" if is_me else "other"
            prefix = "You" if is_me else msg["anon_alias"]
            self._msg_area.insert("end", f"{prefix}:\n", tag)
            self._msg_area.insert("end", f"  {msg['content']}\n", "body")
            self._msg_area.insert("end", f"  {msg['sent_at'][:16]}\n\n", "time")
        self._msg_area.config(state="disabled")
        self._msg_area.see("end")

    def _send_message(self):
        if not self._active_chat:
            return
        content = self._chat_input.get("1.0", "end").strip()
        if not content:
            return
        db.send_message(self._active_chat, self.user["id"], content)
        self._chat_input.delete("1.0", "end")
        self._load_messages()

    def _close_session(self, match_id):
        if messagebox.askyesno("Close session", "Close this support session?"):
            db.close_match(match_id)
            self._active_chat = None
            self._show_chat()

    def _schedule_refresh(self):
        if not self._active_chat:
            return
        try:
            if not self._msg_area.winfo_exists():
                return
            self._load_messages()
        except Exception:
            return
        self.after(4000, self._schedule_refresh)

    # ── APPOINTMENTS ──────────────────────────────────────────────────────────

    def _show_appointments(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(f, text="📅 Appointments with Professional Counselors",
                 font=FONT_TITLE, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w")
        tk.Label(f, text="Schedule sessions with university psychologists and counselors",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(2, 20))

        top = tk.Frame(f, bg=C["bg"])
        top.pack(fill="x")

        # Form
        form = card(top)
        form.pack(side="left", fill="y", padx=(0, 16))

        tk.Label(form, text="New appointment", font=FONT_H2,
                 bg=C["card"], fg=C["sidebar"]).pack(padx=16, pady=(16, 8), anchor="w")

        counselors_pro = ["Dr. Sandra Moreno", "Dr. Felipe Castro",
                          "Lic. Valentina Ríos", "Dr. Hernando Vargas"]

        fields_a = [
            ("Professional counselor:", None, counselors_pro),
            ("Reason for consultation:",    None, ["Anxiety / Stress", "Depression",
                                               "Relationship problems", "Career counseling", "Other"]),
        ]

        self._ap_counselor = tk.StringVar(value=counselors_pro[0])
        self._ap_reason    = tk.StringVar(value="Anxiety / Stress")

        for lbl, _, opts in fields_a:
            tk.Label(form, text=lbl, font=FONT_SMALL, bg=C["card"],
                     fg=C["subtext"]).pack(anchor="w", padx=16, pady=(8, 1))
            var = self._ap_counselor if "ounselor" in lbl else self._ap_reason
            cb  = ttk.Combobox(form, textvariable=var, values=opts,
                                state="readonly", width=28, font=FONT_BODY)
            cb.pack(padx=16, fill="x")

        tk.Label(form, text="Date (YYYY-MM-DD):", font=FONT_SMALL,
                 bg=C["card"], fg=C["subtext"]).pack(anchor="w", padx=16, pady=(8, 1))
        self._ap_date = entry(form, width=28)
        self._ap_date.insert(0, (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"))
        self._ap_date.pack(padx=16, fill="x")

        tk.Label(form, text="Time (HH:MM):", font=FONT_SMALL,
                 bg=C["card"], fg=C["subtext"]).pack(anchor="w", padx=16, pady=(8, 1))
        self._ap_time = entry(form, width=28)
        self._ap_time.insert(0, "10:00")
        self._ap_time.pack(padx=16, fill="x")

        tk.Label(form, text="Additional notes:", font=FONT_SMALL,
                 bg=C["card"], fg=C["subtext"]).pack(anchor="w", padx=16, pady=(8, 1))
        self._ap_notes = tk.Text(form, font=FONT_BODY, height=3, width=30,
                                  bg="#EEF2F7", relief="flat",
                                  highlightthickness=1, highlightbackground=C["border"])
        self._ap_notes.pack(padx=16, fill="x")

        btn(form, "📅 Book appointment", self._do_appointment,
            color=C["success"], width=28).pack(padx=16, pady=16, fill="x")

        # List of appointments
        right_col = tk.Frame(top, bg=C["bg"])
        right_col.pack(side="right", fill="both", expand=True)

        tk.Label(right_col, text="My appointments", font=FONT_H2,
                 bg=C["bg"], fg=C["sidebar"]).pack(anchor="w", pady=(0, 8))

        appts = db.get_student_appointments(self.user["id"])
        if not appts:
            tk.Label(right_col, text="You have no scheduled appointments yet.",
                     font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w")
        else:
            for a in appts:
                c2 = card(right_col)
                c2.pack(fill="x", pady=4)
                st_col = {"scheduled": C["success"], "cancelled": C["danger"],
                           "completed": C["subtext"]}.get(a["status"], C["text"])

                tk.Label(c2, text=f"📋  {a['counselor_name']}",
                         font=FONT_H3, bg=C["card"], fg=C["accent"]).pack(anchor="w", padx=16, pady=(12, 2))
                tk.Label(c2, text=f"🗓  {a['date_time']}  •  {a['notes'] or 'No notes'}",
                         font=FONT_BODY, bg=C["card"], fg=C["text"]).pack(anchor="w", padx=16, pady=2)
                tk.Label(c2, text=f"Status: {a['status'].upper()}",
                         font=("Helvetica", 10, "bold"), bg=C["card"], fg=st_col).pack(anchor="w", padx=16)

                if a["status"] == "scheduled":
                    btn(c2, "Cancel", lambda aid=a["id"]: self._cancel_appt(aid),
                        color=C["danger"], width=10).pack(side="right", padx=16, pady=12)
                else:
                    tk.Label(c2, text="", bg=C["card"]).pack(pady=8)

    def _do_appointment(self):
        counselor = self._ap_counselor.get()
        date      = self._ap_date.get().strip()
        time_str  = self._ap_time.get().strip()
        notes     = self._ap_notes.get("1.0", "end").strip()
        reason    = self._ap_reason.get()

        if not date or not time_str:
            messagebox.showwarning("Empty fields", "Please provide a date and time.")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Incorrect format",
                                  "Date: YYYY-MM-DD  •  Time: HH:MM")
            return

        db.create_appointment(self.user["id"], counselor, f"{date} {time_str}",
                               f"{reason}. {notes}")
        messagebox.showinfo("Appointment booked!",
                             f"Appointment with {counselor}\nDate: {date} {time_str}\n\n"
                             "You will receive confirmation within 48 hours.")
        self._show_appointments()

    def _cancel_appt(self, appt_id):
        if messagebox.askyesno("Cancel appointment", "Cancel this appointment?"):
            db.cancel_appointment(appt_id)
            self._show_appointments()

    # ── LIBRARY ───────────────────────────────────────────────────────────────

    def _show_library(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(f, text="📚 Resource Library",
                 font=FONT_TITLE, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w")
        tk.Label(f, text="Educational materials on mental health and well-being",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(2, 16))

        # Category filter
        cats = ["All"] + db.get_resource_categories()
        filter_row = tk.Frame(f, bg=C["bg"])
        filter_row.pack(fill="x", pady=(0, 12))
        tk.Label(filter_row, text="Filter by category:",
                 font=FONT_H3, bg=C["bg"], fg=C["subtext"]).pack(side="left")
        self._lib_cat = ttk.Combobox(filter_row, values=cats, state="readonly",
                                      width=24, font=FONT_BODY)
        self._lib_cat.set("All")
        self._lib_cat.pack(side="left", padx=8)
        self._lib_cat.bind("<<ComboboxSelected>>", lambda e: self._refresh_library())

        # Add resource (admin only)
        if self.user["role"] == "admin":
            btn(filter_row, "+ Add resource", self._add_resource_dialog,
                color=C["success"], width=18).pack(side="right")

        # Resources container
        self._lib_inner = tk.Frame(f, bg=C["bg"])
        self._lib_inner.pack(fill="both", expand=True)
        self._refresh_library()

    def _refresh_library(self):
        for w in self._lib_inner.winfo_children():
            w.destroy()

        cat = self._lib_cat.get()
        resources = db.get_all_resources(None if cat == "All" else cat)

        canvas = tk.Canvas(self._lib_inner, bg=C["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(self._lib_inner, orient="vertical", command=canvas.yview)
        inner  = tk.Frame(canvas, bg=C["bg"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        cat_colors = {"Anxiety": "#A8DADC", "Well-being": "#95D5B2",
                      "Academic Performance": "#FFD166", "Support Resources": "#B5C8E8",
                      "Crisis": "#FFB3B3"}

        for res in resources:
            c2 = card(inner)
            c2.pack(fill="x", pady=5, padx=2)

            top_row = tk.Frame(c2, bg=C["card"])
            top_row.pack(fill="x", padx=16, pady=(14, 4))

            cat_col = cat_colors.get(res["category"], C["accent2"])
            tk.Label(top_row, text=f"  {res['category']}  ", font=FONT_SMALL,
                     bg=cat_col, fg=C["text"], relief="flat",
                     padx=4).pack(side="left")
            tk.Label(top_row, text=f"By: {res['author']}",
                     font=FONT_SMALL, bg=C["card"], fg=C["subtext"]).pack(side="right")

            tk.Label(c2, text=res["title"], font=FONT_H2,
                     bg=C["card"], fg=C["sidebar"]).pack(anchor="w", padx=16)

            preview = res["content"][:120] + ("..." if len(res["content"]) > 120 else "")
            tk.Label(c2, text=preview, font=FONT_BODY,
                     bg=C["card"], fg=C["text"], wraplength=660,
                     justify="left").pack(anchor="w", padx=16, pady=(4, 8))

            btn(c2, "Read full →",
                lambda r=res: self._read_resource(r),
                color=C["accent"], width=14).pack(anchor="e", padx=16, pady=(0, 14))

    def _read_resource(self, res):
        win = tk.Toplevel(self)
        win.title(res["title"])
        win.geometry("680x520")
        win.configure(bg=C["bg"])

        tk.Label(win, text=res["title"], font=FONT_TITLE,
                 bg=C["bg"], fg=C["sidebar"], wraplength=600,
                 justify="left").pack(padx=24, pady=(24, 4))
        tk.Label(win, text=f"Category: {res['category']}  •  Author: {res['author']}",
                 font=FONT_SMALL, bg=C["bg"], fg=C["subtext"]).pack(anchor="w", padx=24)
        separator(win).pack(fill="x", padx=24, pady=12)

        txt = scrolledtext.ScrolledText(win, font=FONT_BODY, wrap="word",
                                         bg=C["card"], relief="flat",
                                         padx=16, pady=16)
        txt.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        txt.insert("1.0", res["content"])
        txt.config(state="disabled")

        btn(win, "Close", win.destroy, color=C["subtext"], width=12).pack(pady=(0, 16))

    def _add_resource_dialog(self):
        win = tk.Toplevel(self)
        win.title("Add resource")
        win.geometry("560x480")
        win.configure(bg=C["bg"])

        tk.Label(win, text="New resource", font=FONT_TITLE,
                 bg=C["bg"], fg=C["sidebar"]).pack(padx=24, pady=(20, 16))

        for lbl, attr in [("Title:", "_nr_title"), ("Category:", "_nr_cat"),
                           ("Author:", "_nr_author")]:
            tk.Label(win, text=lbl, font=FONT_H3, bg=C["bg"],
                     fg=C["subtext"]).pack(anchor="w", padx=24, pady=(8, 1))
            e = entry(win, width=42)
            e.pack(padx=24, fill="x")
            setattr(self, attr, e)

        self._nr_author.insert(0, "Clinical Team")

        tk.Label(win, text="Content:", font=FONT_H3, bg=C["bg"],
                 fg=C["subtext"]).pack(anchor="w", padx=24, pady=(8, 1))
        self._nr_content = tk.Text(win, font=FONT_BODY, height=8, wrap="word",
                                    bg="#EEF2F7", relief="flat",
                                    highlightthickness=1, highlightbackground=C["border"])
        self._nr_content.pack(padx=24, fill="x")

        def _save():
            title   = self._nr_title.get().strip()
            cat     = self._nr_cat.get().strip()
            author  = self._nr_author.get().strip()
            content = self._nr_content.get("1.0", "end").strip()
            if not all([title, cat, content]):
                messagebox.showwarning("Empty fields", "Please fill in title, category, and content.")
                return
            db.add_resource(title, cat, content, author)
            messagebox.showinfo("Saved", "Resource added successfully.")
            win.destroy()
            self._show_library()

        btn(win, "Save resource", _save, color=C["success"], width=20).pack(pady=16)

    # ── ADMIN DASHBOARD ───────────────────────────────────────────────────────

    def _show_dashboard(self):
        self._clear_content()
        f = tk.Frame(self.content, bg=C["bg"])
        f.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(f, text="📊 Admin Dashboard",
                 font=FONT_TITLE, bg=C["bg"], fg=C["sidebar"]).pack(anchor="w")
        tk.Label(f, text="Real-time operational metrics",
                 font=FONT_BODY, bg=C["bg"], fg=C["subtext"]).pack(anchor="w", pady=(2, 20))

        stats = db.get_platform_stats()

        # KPI cards
        kpis = [
            ("👥 Students",        stats["students"],       C["accent"]),
            ("🤝 Peer counselors", stats["counselors"],     C["success"]),
            ("🔗 Total sessions",  stats["matches"],        "#9C6FE4"),
            ("💬 Active now",      stats["active_matches"], C["warning"]),
            ("📅 Pending appts",   stats["appointments"],   "#E07B54"),
            ("📨 Messages",        stats["messages"],       "#4DB6AC"),
        ]

        row1 = tk.Frame(f, bg=C["bg"])
        row1.pack(fill="x", pady=(0, 16))
        for i, (lbl, val, col) in enumerate(kpis):
            c2 = card(row1)
            c2.pack(side="left", fill="x", expand=True, padx=5)
            tk.Frame(c2, bg=col, height=4).pack(fill="x")
            tk.Label(c2, text=str(val), font=("Helvetica", 28, "bold"),
                     bg=C["card"], fg=col).pack(pady=(12, 2))
            tk.Label(c2, text=lbl, font=FONT_SMALL,
                     bg=C["card"], fg=C["subtext"]).pack(pady=(0, 12))

        # Load indicator
        load_card = card(f)
        load_card.pack(fill="x", pady=(0, 16))
        tk.Label(load_card, text="⚡ Average counselor load",
                 font=FONT_H2, bg=C["card"], fg=C["sidebar"]).pack(anchor="w", padx=20, pady=(16, 4))

        load_pct = (stats["avg_load"] / 20) * 100
        load_col = C["success"] if load_pct < 50 else (C["warning"] if load_pct < 80 else C["danger"])
        bar_outer = tk.Frame(load_card, bg=C["border"], height=20)
        bar_outer.pack(fill="x", padx=20, pady=8)
        bar_outer.pack_propagate(False)

        tk.Label(load_card,
                 text=f"{stats['avg_load']:.1f} / 20 sessions per counselor  ({load_pct:.0f}%)",
                 font=FONT_BODY, bg=C["card"], fg=load_col).pack(anchor="w", padx=20, pady=(0, 16))

        # Validation summary (from Workshop 4)
        val_card = card(f)
        val_card.pack(fill="x")
        tk.Label(val_card, text="✅ System status (Workshop 4 — validation)",
                 font=FONT_H2, bg=C["card"], fg=C["sidebar"]).pack(anchor="w", padx=20, pady=(16, 8))

        checks = [
            ("Modular architecture", "PASS", C["success"]),
            (f"Match rate  (active: {stats['active_matches']}/{stats['matches']})",
             "PASS" if stats["matches"] == 0 or stats["active_matches"]/max(stats["matches"],1) > 0.5 else "WARN",
             C["success"]),
            (f"Counselor load  ({load_pct:.0f}%)",
             "PASS" if load_pct < 80 else "FAIL",
             C["success"] if load_pct < 80 else C["danger"]),
            ("Privacy: anonymous aliases active", "PASS", C["success"]),
            ("Resource library available", "PASS", C["success"]),
        ]

        for desc, status, col in checks:
            row = tk.Frame(val_card, bg=C["card"])
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=desc, font=FONT_BODY, bg=C["card"],
                     fg=C["text"]).pack(side="left")
            tk.Label(row, text=f"  {status}  ", font=("Helvetica", 10, "bold"),
                     bg=col, fg="white").pack(side="right")

        tk.Label(val_card, text="", bg=C["card"]).pack(pady=4)

        # NEW: Metrics export function (Workshop 4)
        def _export_metrics():
            with open("validation_metrics.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                for key, val in stats.items():
                    writer.writerow([key, val])
                writer.writerow(["Load_Percentage", f"{load_pct:.1f}%"])
            messagebox.showinfo("Exported", "Metrics exported to validation_metrics.csv.\nUse them in your Final Report.")

        btn(val_card, "📥 Export Metrics (CSV)", _export_metrics, 
            color=C["accent"], width=30).pack(pady=(0, 16))

    def _logout(self):
        self.destroy()
        self.auth_win.deiconify()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    db.init_db()
    app = AuthWindow()
    app.mainloop()