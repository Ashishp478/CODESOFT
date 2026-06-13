import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json, csv, sqlite3, os, hashlib, threading, time, random
from datetime import datetime, timedelta, date
from calendar import monthcalendar, month_abbr
import re

# ══════════════════════════════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════════════════════════════
DB = "todo.db"

def init_db():
    con = sqlite3.connect(DB)
    c = con.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT
    );
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT, description TEXT, notes TEXT,
        due_date TEXT, priority TEXT, status TEXT,
        category TEXT, recurrence TEXT,
        created_at TEXT, completed_at TEXT,
        deleted INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    con.commit(); con.close()

def db():
    return sqlite3.connect(DB)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ══════════════════════════════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "BG":"#0e0e16","CARD":"#181824","CARD2":"#1e1e2e","SIDEBAR":"#13131f",
        "BORDER":"#2e2e44","TEXT":"#e0e0f0","MUTED":"#7070a0","ACCENT":"#7c6fff",
        "ACCENT2":"#ff6b9d","SUCCESS":"#06d6a0","WARN":"#ffb703","DANGER":"#ef476f",
        "HIGH":"#ef476f","MED":"#ffb703","LOW":"#06d6a0",
        "PENDING":"#7c6fff","INPROG":"#ffb703","DONE":"#06d6a0",
        "ENTRY":"#23233a","SEL":"#7c6fff",
    },
    "light": {
        "BG":"#f5f5ff","CARD":"#ffffff","CARD2":"#eeeeff","SIDEBAR":"#e8e8ff",
        "BORDER":"#d0d0e8","TEXT":"#1a1a2e","MUTED":"#7070a0","ACCENT":"#5b4fff",
        "ACCENT2":"#e0507a","SUCCESS":"#059669","WARN":"#d97706","DANGER":"#dc2626",
        "HIGH":"#dc2626","MED":"#d97706","LOW":"#059669",
        "PENDING":"#5b4fff","INPROG":"#d97706","DONE":"#059669",
        "ENTRY":"#f0f0ff","SEL":"#5b4fff",
    }
}

FONT_TITLE = ("Georgia", 20, "bold")
FONT_HEAD  = ("Georgia", 14, "bold")
FONT_MED   = ("Georgia", 11, "bold")
FONT_BODY  = ("Courier New", 10)
FONT_SMALL = ("Courier New", 9)
FONT_TINY  = ("Arial", 8)
FONT_BTN   = ("Georgia", 10, "bold")
FONT_SCORE = ("Georgia", 24, "bold")

PRIORITIES  = ["High", "Medium", "Low"]
STATUSES    = ["Pending", "In Progress", "Completed"]
CATEGORIES  = ["Work", "Personal", "Study", "Shopping", "Health", "Other"]
RECURRENCES = ["None", "Daily", "Weekly", "Monthly"]
SORT_OPTIONS= ["Due Date", "Priority", "Status", "Category", "Title"]

PRIO_ORDER = {"High": 0, "Medium": 1, "Low": 2}
STAT_ORDER = {"Pending": 0, "In Progress": 1, "Completed": 2}


# ══════════════════════════════════════════════════════════════════════
#  LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════
class LoginScreen:
    def __init__(self, root, on_login):
        self.root = root
        self.on_login = on_login
        self.T = THEMES["dark"]
        root.configure(bg=self.T["BG"])
        self._build()

    def _build(self):
        T = self.T
        for w in self.root.winfo_children(): w.destroy()

        outer = tk.Frame(self.root, bg=T["BG"])
        outer.place(relx=0.5, rely=0.5, anchor="center")

        # Logo area
        tk.Label(outer, text="✅", bg=T["BG"], fg=T["ACCENT"],
                 font=("Segoe UI Emoji", 48)).pack(pady=(0,4))
        tk.Label(outer, text="TaskMaster Pro", bg=T["BG"], fg=T["TEXT"],
                 font=FONT_TITLE).pack()
        tk.Label(outer, text="Your advanced productivity companion",
                 bg=T["BG"], fg=T["MUTED"], font=FONT_SMALL).pack(pady=(2,24))

        card = tk.Frame(outer, bg=T["CARD"], padx=36, pady=28,
                        highlightbackground=T["BORDER"], highlightthickness=1)
        card.pack()

        self._tab = tk.StringVar(value="login")
        tab_row = tk.Frame(card, bg=T["CARD2"])
        tab_row.pack(fill="x", pady=(0,20))
        for val, lbl in [("login","Login"),("register","Register")]:
            tk.Radiobutton(tab_row, text=lbl, variable=self._tab, value=val,
                bg=T["CARD2"], fg=T["TEXT"], selectcolor=T["ACCENT"],
                activebackground=T["CARD2"], font=FONT_BTN,
                indicatoron=0, relief="flat", padx=20, pady=6,
                command=self._refresh_tab).pack(side="left", expand=True, fill="x")

        self.form = tk.Frame(card, bg=T["CARD"])
        self.form.pack(fill="x")
        self._refresh_tab()

    def _refresh_tab(self):
        T = self.T
        for w in self.form.winfo_children(): w.destroy()
        tab = self._tab.get()

        def lbl(text):
            tk.Label(self.form, text=text, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_SMALL).pack(anchor="w", pady=(8,2))

        def ent(show=None):
            v = tk.StringVar()
            tk.Entry(self.form, textvariable=v, bg=T["ENTRY"], fg=T["TEXT"],
                     insertbackground=T["TEXT"], font=FONT_BODY, relief="flat",
                     bd=6, width=26, show=show or "").pack(fill="x", ipady=4)
            return v

        lbl("Username")
        self.v_user = ent()
        lbl("Password")
        self.v_pass = ent(show="●")
        if tab == "register":
            lbl("Confirm Password")
            self.v_pass2 = ent(show="●")

        self.err_lbl = tk.Label(self.form, text="", bg=T["CARD"],
                                fg=T["DANGER"], font=FONT_TINY)
        self.err_lbl.pack(pady=(8,0))

        cmd = self._do_login if tab == "login" else self._do_register
        btn_text = "Login →" if tab == "login" else "Create Account →"
        tk.Button(self.form, text=btn_text, command=cmd,
                  bg=T["ACCENT"], fg="white", font=FONT_BTN,
                  relief="flat", bd=0, cursor="hand2",
                  padx=20, pady=8, activebackground=T["ACCENT"]).pack(
                  fill="x", pady=(16,0))

    def _do_login(self):
        u, p = self.v_user.get().strip(), self.v_pass.get()
        con = db(); c = con.cursor()
        row = c.execute("SELECT id FROM users WHERE username=? AND password=?",
                        (u, hash_pw(p))).fetchone()
        con.close()
        if row:
            self.on_login(row[0], u)
        else:
            self.err_lbl.config(text="❌ Invalid username or password")

    def _do_register(self):
        u  = self.v_user.get().strip()
        p  = self.v_pass.get()
        p2 = self.v_pass2.get()
        if not u or not p:
            self.err_lbl.config(text="❌ Username and password required"); return
        if p != p2:
            self.err_lbl.config(text="❌ Passwords don't match"); return
        try:
            con = db(); c = con.cursor()
            c.execute("INSERT INTO users(username,password) VALUES(?,?)",
                      (u, hash_pw(p)))
            uid = c.lastrowid; con.commit(); con.close()
            self.on_login(uid, u)
        except sqlite3.IntegrityError:
            self.err_lbl.config(text="❌ Username already taken")


# ══════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════
class TodoApp:
    def __init__(self, root, user_id, username):
        self.root = root
        self.user_id  = user_id
        self.username = username
        self.theme_name = tk.StringVar(value="dark")
        self.T = THEMES["dark"]
        self.search_var   = tk.StringVar()
        self.sort_var     = tk.StringVar(value="Due Date")
        self.filter_cat   = tk.StringVar(value="All")
        self.filter_prio  = tk.StringVar(value="All")
        self.filter_stat  = tk.StringVar(value="All")
        self.active_tab   = tk.StringVar(value="tasks")
        self.pomodoro_running = False
        self.pomo_seconds = 25 * 60
        self._pomo_id     = None
        self._notif_id    = None
        self._build()
        self._start_reminder_thread()

    # ── Build Main Layout ─────────────────────────────────────────────
    def _build(self):
        T = self.T
        self.root.configure(bg=T["BG"])
        for w in self.root.winfo_children(): w.destroy()
        self.root.geometry("1200x750")
        self.root.title(f"TaskMaster Pro — {self.username}")

        # Main container
        main = tk.Frame(self.root, bg=T["BG"])
        main.pack(fill="both", expand=True)

        # Sidebar
        self._build_sidebar(main)

        # Content area
        self.content = tk.Frame(main, bg=T["BG"])
        self.content.pack(side="left", fill="both", expand=True)

        self._show_tab("tasks")

    def _build_sidebar(self, parent):
        T = self.T
        self.sidebar = tk.Frame(parent, bg=T["SIDEBAR"], width=220,
                                highlightbackground=T["BORDER"], highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        tk.Label(self.sidebar, text="✅ TaskMaster", bg=T["SIDEBAR"],
                 fg=T["ACCENT"], font=FONT_HEAD).pack(pady=(20,4))
        tk.Label(self.sidebar, text=f"👤 {self.username}",
                 bg=T["SIDEBAR"], fg=T["MUTED"], font=FONT_SMALL).pack()
        tk.Frame(self.sidebar, bg=T["BORDER"], height=1).pack(fill="x", padx=14, pady=14)

        nav_items = [
            ("tasks",    "📋", "My Tasks"),
            ("add",      "➕", "Add Task"),
            ("calendar", "📅", "Calendar"),
            ("stats",    "📊", "Statistics"),
            ("history",  "🕐", "History"),
            ("pomodoro", "🍅", "Pomodoro"),
            ("settings", "⚙️", "Settings"),
        ]
        self.nav_btns = {}
        for key, icon, label in nav_items:
            btn = tk.Button(self.sidebar, text=f"  {icon}  {label}",
                anchor="w", font=FONT_BTN,
                bg=T["ACCENT"] if key == self.active_tab.get() else T["SIDEBAR"],
                fg="white" if key == self.active_tab.get() else T["TEXT"],
                relief="flat", bd=0, cursor="hand2", pady=10, padx=16,
                activebackground=T["ACCENT"], activeforeground="white",
                command=lambda k=key: self._show_tab(k))
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_btns[key] = btn

        # Progress at bottom
        tk.Frame(self.sidebar, bg=T["BORDER"], height=1).pack(
            fill="x", padx=14, pady=14, side="bottom")
        self.prog_lbl = tk.Label(self.sidebar, text="", bg=T["SIDEBAR"],
                                 fg=T["MUTED"], font=FONT_TINY, wraplength=190)
        self.prog_lbl.pack(side="bottom", pady=8)
        self._update_progress_sidebar()

        # Logout
        tk.Button(self.sidebar, text="  🚪  Logout",
                  anchor="w", font=FONT_BTN,
                  bg=T["SIDEBAR"], fg=T["DANGER"],
                  relief="flat", bd=0, cursor="hand2", pady=10, padx=16,
                  command=self._logout).pack(fill="x", padx=8, pady=2, side="bottom")

        # Theme toggle
        tk.Button(self.sidebar, text="  🌙  Toggle Theme",
                  anchor="w", font=FONT_BTN,
                  bg=T["SIDEBAR"], fg=T["MUTED"],
                  relief="flat", bd=0, cursor="hand2", pady=8, padx=16,
                  command=self._toggle_theme).pack(fill="x", padx=8, side="bottom")

    def _show_tab(self, key):
        self.active_tab.set(key)
        T = self.T
        for k, btn in self.nav_btns.items():
            btn.config(
                bg=T["ACCENT"] if k == key else T["SIDEBAR"],
                fg="white" if k == key else T["TEXT"])
        for w in self.content.winfo_children(): w.destroy()
        {
            "tasks":    self._tab_tasks,
            "add":      self._tab_add,
            "calendar": self._tab_calendar,
            "stats":    self._tab_stats,
            "history":  self._tab_history,
            "pomodoro": self._tab_pomodoro,
            "settings": self._tab_settings,
        }[key]()

    # ══ TAB: TASKS ═══════════════════════════════════════════════════
    def _tab_tasks(self):
        T = self.T
        parent = self.content

        # Header
        hdr = tk.Frame(parent, bg=T["BG"], pady=14)
        hdr.pack(fill="x", padx=24)
        tk.Label(hdr, text="📋  My Tasks", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_TITLE).pack(side="left")
        tk.Button(hdr, text="+ Add Task", bg=T["ACCENT"], fg="white",
                  font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
                  padx=14, pady=6,
                  command=lambda: self._show_tab("add")).pack(side="right")

        # Filter bar
        fbar = tk.Frame(parent, bg=T["CARD"], pady=8,
                        highlightbackground=T["BORDER"], highlightthickness=1)
        fbar.pack(fill="x", padx=24, pady=(0,10))

        # Search
        tk.Label(fbar, text="🔍", bg=T["CARD"], fg=T["MUTED"],
                 font=("Segoe UI Emoji", 11)).pack(side="left", padx=(10,4))
        self.search_var.trace_add("write", lambda *_: self._load_tasks())
        tk.Entry(fbar, textvariable=self.search_var, bg=T["ENTRY"],
                 fg=T["TEXT"], insertbackground=T["TEXT"],
                 font=FONT_BODY, relief="flat", bd=4, width=22).pack(
                 side="left", ipady=4, padx=(0,14))

        # Filters
        for lbl, var, opts in [
            ("Cat:", self.filter_cat, ["All"]+CATEGORIES),
            ("Priority:", self.filter_prio, ["All"]+PRIORITIES),
            ("Status:", self.filter_stat, ["All"]+STATUSES),
            ("Sort:", self.sort_var, SORT_OPTIONS),
        ]:
            tk.Label(fbar, text=lbl, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_SMALL).pack(side="left", padx=(6,2))
            cb = ttk.Combobox(fbar, textvariable=var, values=opts,
                              width=11, state="readonly", font=FONT_SMALL)
            cb.pack(side="left", padx=(0,4))
            var.trace_add("write", lambda *_: self._load_tasks())

        tk.Button(fbar, text="Clear Filters", bg=T["CARD2"], fg=T["MUTED"],
                  font=FONT_TINY, relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=4, command=self._clear_filters).pack(
                  side="right", padx=10)

        # Task list container (scrollable)
        list_frame = tk.Frame(parent, bg=T["BG"])
        list_frame.pack(fill="both", expand=True, padx=24)

        canvas = tk.Canvas(list_frame, bg=T["BG"], highlightthickness=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.task_scroll_frame = tk.Frame(canvas, bg=T["BG"])
        self.task_canvas_window = canvas.create_window(
            (0,0), window=self.task_scroll_frame, anchor="nw")

        def _resize(e):
            canvas.itemconfig(self.task_canvas_window, width=e.width)
        canvas.bind("<Configure>", _resize)
        self.task_scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._load_tasks()

    def _load_tasks(self):
        T = self.T
        for w in self.task_scroll_frame.winfo_children(): w.destroy()

        tasks = self._fetch_tasks()

        if not tasks:
            tk.Label(self.task_scroll_frame,
                     text="🎉 No tasks found! Add one to get started.",
                     bg=T["BG"], fg=T["MUTED"], font=FONT_MED).pack(pady=40)
            return

        for task in tasks:
            self._task_card(self.task_scroll_frame, task)

    def _task_card(self, parent, task):
        T = self.T
        tid, title, desc, notes, due, prio, status, cat, recur, created, *_ = task

        prio_color  = T[prio.upper()[:3]] if prio.upper()[:3] in ("HIG","MED","LOW") else T["MUTED"]
        prio_color  = {"High": T["HIGH"], "Medium": T["MED"], "Low": T["LOW"]}.get(prio, T["MUTED"])
        stat_color  = {"Pending": T["PENDING"], "In Progress": T["INPROG"],
                       "Completed": T["DONE"]}.get(status, T["MUTED"])

        # Overdue?
        overdue = False
        if due and status != "Completed":
            try:
                overdue = datetime.strptime(due, "%Y-%m-%d").date() < date.today()
            except: pass

        card = tk.Frame(parent, bg=T["CARD"],
                        highlightbackground=T["DANGER"] if overdue else T["BORDER"],
                        highlightthickness=1)
        card.pack(fill="x", pady=4)

        # Left color strip
        strip = tk.Frame(card, bg=prio_color, width=5)
        strip.pack(side="left", fill="y")

        body = tk.Frame(card, bg=T["CARD"], pady=10, padx=12)
        body.pack(side="left", fill="both", expand=True)

        # Row 1: title + badges
        r1 = tk.Frame(body, bg=T["CARD"])
        r1.pack(fill="x")
        tk.Label(r1, text=title, bg=T["CARD"], fg=T["TEXT"],
                 font=FONT_MED).pack(side="left")
        if overdue:
            tk.Label(r1, text=" ⚠ OVERDUE", bg=T["CARD"],
                     fg=T["DANGER"], font=FONT_TINY).pack(side="left", padx=4)
        if recur != "None":
            tk.Label(r1, text=f"🔁{recur}", bg=T["CARD"],
                     fg=T["MUTED"], font=FONT_TINY).pack(side="left", padx=4)

        # Row 2: meta
        r2 = tk.Frame(body, bg=T["CARD"])
        r2.pack(fill="x", pady=(2,0))
        meta_items = [
            (f"📅 {due or '—'}", T["MUTED"]),
            (f"🏷 {cat}", T["MUTED"]),
        ]
        for txt, col in meta_items:
            tk.Label(r2, text=txt, bg=T["CARD"], fg=col,
                     font=FONT_TINY).pack(side="left", padx=(0,12))

        # Badges
        def badge(text, bg, fg):
            tk.Label(r2, text=text, bg=bg, fg=fg,
                     font=FONT_TINY, padx=6, pady=2).pack(side="left", padx=3)

        badge(f" {prio} ", prio_color, "white")
        badge(f" {status} ", stat_color, "white")

        if desc:
            tk.Label(body, text=desc, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_TINY, wraplength=600, anchor="w").pack(
                     fill="x", pady=(3,0))

        # Action buttons
        actions = tk.Frame(card, bg=T["CARD"], padx=10)
        actions.pack(side="right", fill="y")

        status_cycle = {"Pending":"In Progress","In Progress":"Completed","Completed":"Pending"}
        next_stat = status_cycle.get(status, "Pending")
        stat_icon = {"Pending":"▶","In Progress":"✔","Completed":"↺"}.get(status,"▶")

        def _btn(text, col, cmd):
            b = tk.Button(actions, text=text, bg=col, fg="white",
                          font=FONT_TINY, relief="flat", bd=0, cursor="hand2",
                          padx=8, pady=4, command=cmd)
            b.pack(pady=2)
            return b

        _btn(f"{stat_icon} {next_stat}", stat_color,
             lambda tid=tid, ns=next_stat: self._set_status(tid, ns))
        _btn("✏ Edit", T["ACCENT"],
             lambda tid=tid: self._edit_task_dialog(tid))
        _btn("🗑 Del", T["DANGER"],
             lambda tid=tid: self._delete_task(tid))

    def _fetch_tasks(self):
        con = db(); c = con.cursor()
        q   = """SELECT id,title,description,notes,due_date,priority,
                        status,category,recurrence,created_at
                 FROM tasks WHERE user_id=? AND deleted=0"""
        params = [self.user_id]

        search = self.search_var.get().strip().lower()
        if search:
            q += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]

        fcat  = self.filter_cat.get()
        fprio = self.filter_prio.get()
        fstat = self.filter_stat.get()
        if fcat  != "All": q += " AND category=?";  params.append(fcat)
        if fprio != "All": q += " AND priority=?";  params.append(fprio)
        if fstat != "All": q += " AND status=?";    params.append(fstat)

        rows = c.execute(q, params).fetchall()
        con.close()

        sort = self.sort_var.get()
        if sort == "Due Date":
            rows.sort(key=lambda r: r[4] or "9999-99-99")
        elif sort == "Priority":
            rows.sort(key=lambda r: PRIO_ORDER.get(r[5], 9))
        elif sort == "Status":
            rows.sort(key=lambda r: STAT_ORDER.get(r[6], 9))
        elif sort == "Category":
            rows.sort(key=lambda r: r[7] or "")
        elif sort == "Title":
            rows.sort(key=lambda r: (r[1] or "").lower())
        return rows

    def _clear_filters(self):
        self.search_var.set("")
        self.filter_cat.set("All")
        self.filter_prio.set("All")
        self.filter_stat.set("All")

    def _set_status(self, tid, status):
        con = db(); c = con.cursor()
        completed_at = datetime.now().isoformat() if status == "Completed" else None
        c.execute("UPDATE tasks SET status=?, completed_at=? WHERE id=?",
                  (status, completed_at, tid))
        con.commit(); con.close()
        self._load_tasks()
        self._update_progress_sidebar()

    def _delete_task(self, tid):
        if messagebox.askyesno("Delete", "Move this task to history?"):
            con = db(); c = con.cursor()
            c.execute("UPDATE tasks SET deleted=1 WHERE id=?", (tid,))
            con.commit(); con.close()
            self._load_tasks()
            self._update_progress_sidebar()

    # ══ TASK FORM (shared add/edit) ═══════════════════════════════════
    def _build_task_form(self, parent, task=None):
        T = self.T
        fields = {}

        def row(lbl, widget_fn, colspan=1):
            r = tk.Frame(parent, bg=T["CARD"])
            r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_SMALL, width=14, anchor="e").pack(side="left", padx=(0,8))
            v = widget_fn(r)
            fields[lbl] = v
            return v

        def entry(parent, prefill=""):
            v = tk.StringVar(value=prefill)
            tk.Entry(parent, textvariable=v, bg=T["ENTRY"], fg=T["TEXT"],
                     insertbackground=T["TEXT"], font=FONT_BODY,
                     relief="flat", bd=4, width=34).pack(side="left", ipady=4)
            return v

        def combo(parent, opts, prefill=None):
            v = tk.StringVar(value=prefill or opts[0])
            ttk.Combobox(parent, textvariable=v, values=opts,
                         width=18, state="readonly",
                         font=FONT_BODY).pack(side="left")
            return v

        def text_area(parent, prefill=""):
            t = tk.Text(parent, bg=T["ENTRY"], fg=T["TEXT"],
                        insertbackground=T["TEXT"], font=FONT_BODY,
                        relief="flat", bd=4, width=34, height=3)
            t.pack(side="left", pady=2)
            if prefill: t.insert("1.0", prefill)
            return t

        v_title = row("Title *",     lambda p: entry(p, task[1] if task else ""))
        v_desc  = row("Description", lambda p: entry(p, task[2] if task else ""))
        v_notes = row("Notes",       lambda p: text_area(p, task[3] if task else ""))
        v_due   = row("Due Date",    lambda p: entry(p, task[4] if task else ""))
        tk.Label(list(parent.children.values())[-1],
                 text="(YYYY-MM-DD)", bg=T["CARD"], fg=T["MUTED"],
                 font=FONT_TINY).pack(side="left", padx=6)
        v_prio  = row("Priority",    lambda p: combo(p, PRIORITIES, task[5] if task else "Medium"))
        v_stat  = row("Status",      lambda p: combo(p, STATUSES,   task[6] if task else "Pending"))
        v_cat   = row("Category",    lambda p: combo(p, CATEGORIES, task[7] if task else "Work"))
        v_recur = row("Recurrence",  lambda p: combo(p, RECURRENCES,task[8] if task else "None"))

        return v_title, v_desc, v_notes, v_due, v_prio, v_stat, v_cat, v_recur

    # ══ TAB: ADD TASK ════════════════════════════════════════════════
    def _tab_add(self):
        T = self.T
        parent = self.content

        tk.Label(parent, text="➕  Add New Task", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_TITLE, pady=14).pack(anchor="w", padx=24)

        card = tk.Frame(parent, bg=T["CARD"], padx=28, pady=20,
                        highlightbackground=T["BORDER"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=24, pady=(0,20))

        widgets = self._build_task_form(card)
        v_title,v_desc,v_notes,v_due,v_prio,v_stat,v_cat,v_recur = widgets

        err = tk.Label(card, text="", bg=T["CARD"], fg=T["DANGER"], font=FONT_SMALL)
        err.pack()

        def save():
            title = v_title.get().strip()
            if not title:
                err.config(text="❌ Task title is required"); return
            due = v_due.get().strip()
            if due:
                try: datetime.strptime(due, "%Y-%m-%d")
                except: err.config(text="❌ Date format: YYYY-MM-DD"); return
            notes_text = v_notes.get("1.0","end").strip()
            con = db(); c = con.cursor()
            c.execute("""INSERT INTO tasks
                (user_id,title,description,notes,due_date,priority,status,
                 category,recurrence,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (self.user_id, title, v_desc.get().strip(),
                 notes_text, due or None,
                 v_prio.get(), v_stat.get(), v_cat.get(),
                 v_recur.get(), datetime.now().isoformat()))
            con.commit(); con.close()
            err.config(text="✅ Task added!", fg=T["SUCCESS"])
            self._update_progress_sidebar()
            self.root.after(800, lambda: self._show_tab("tasks"))

        tk.Button(card, text="💾  Save Task", command=save,
                  bg=T["ACCENT"], fg="white", font=FONT_BTN,
                  relief="flat", bd=0, cursor="hand2",
                  padx=24, pady=8).pack(pady=(16,0))

    # ══ EDIT DIALOG ═══════════════════════════════════════════════════
    def _edit_task_dialog(self, tid):
        T = self.T
        con = db(); c = con.cursor()
        task = c.execute(
            "SELECT id,title,description,notes,due_date,priority,status,"
            "category,recurrence FROM tasks WHERE id=?", (tid,)).fetchone()
        con.close()
        if not task: return

        win = tk.Toplevel(self.root)
        win.title("✏ Edit Task")
        win.geometry("560x520")
        win.configure(bg=T["BG"])
        win.grab_set()

        tk.Label(win, text="✏  Edit Task", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_HEAD, pady=14).pack(anchor="w", padx=24)

        card = tk.Frame(win, bg=T["CARD"], padx=24, pady=16,
                        highlightbackground=T["BORDER"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=(0,10))

        widgets = self._build_task_form(card, task)
        v_title,v_desc,v_notes,v_due,v_prio,v_stat,v_cat,v_recur = widgets

        err = tk.Label(card, text="", bg=T["CARD"], fg=T["DANGER"], font=FONT_SMALL)
        err.pack()

        def save():
            title = v_title.get().strip()
            if not title:
                err.config(text="❌ Title required"); return
            due = v_due.get().strip()
            if due:
                try: datetime.strptime(due, "%Y-%m-%d")
                except: err.config(text="❌ Date: YYYY-MM-DD"); return
            notes_text = v_notes.get("1.0","end").strip()
            con = db(); c = con.cursor()
            c.execute("""UPDATE tasks SET title=?,description=?,notes=?,
                due_date=?,priority=?,status=?,category=?,recurrence=?
                WHERE id=?""",
                (title, v_desc.get().strip(), notes_text, due or None,
                 v_prio.get(), v_stat.get(), v_cat.get(), v_recur.get(), tid))
            con.commit(); con.close()
            self._load_tasks()
            self._update_progress_sidebar()
            win.destroy()

        tk.Button(card, text="💾 Update", command=save,
                  bg=T["ACCENT"], fg="white", font=FONT_BTN,
                  relief="flat", bd=0, cursor="hand2",
                  padx=20, pady=8).pack(pady=(12,0))

    # ══ TAB: CALENDAR ════════════════════════════════════════════════
    def _tab_calendar(self):
        T = self.T
        parent = self.content
        today  = date.today()

        self._cal_year  = getattr(self, "_cal_year",  today.year)
        self._cal_month = getattr(self, "_cal_month", today.month)

        tk.Label(parent, text="📅  Calendar View", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_TITLE, pady=14).pack(anchor="w", padx=24)

        # Month nav
        nav = tk.Frame(parent, bg=T["BG"])
        nav.pack(fill="x", padx=24)
        tk.Button(nav, text="◀", bg=T["CARD2"], fg=T["TEXT"],
                  font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
                  padx=10, pady=4,
                  command=self._cal_prev).pack(side="left")
        self.cal_month_lbl = tk.Label(nav,
            text=f"{month_abbr[self._cal_month]} {self._cal_year}",
            bg=T["BG"], fg=T["TEXT"], font=FONT_HEAD, width=18)
        self.cal_month_lbl.pack(side="left", padx=16)
        tk.Button(nav, text="▶", bg=T["CARD2"], fg=T["TEXT"],
                  font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
                  padx=10, pady=4,
                  command=self._cal_next).pack(side="left")
        tk.Button(nav, text="Today", bg=T["ACCENT"], fg="white",
                  font=FONT_SMALL, relief="flat", bd=0, cursor="hand2",
                  padx=10, pady=4,
                  command=self._cal_today).pack(side="left", padx=8)

        self.cal_frame = tk.Frame(parent, bg=T["BG"])
        self.cal_frame.pack(fill="both", expand=True, padx=24, pady=10)
        self._draw_calendar()

    def _draw_calendar(self):
        T = self.T
        for w in self.cal_frame.winfo_children(): w.destroy()

        today = date.today()
        year, month = self._cal_year, self._cal_month

        # Fetch tasks for this month
        con = db(); c = con.cursor()
        rows = c.execute(
            "SELECT due_date,title,priority FROM tasks "
            "WHERE user_id=? AND deleted=0 AND due_date LIKE ?",
            (self.user_id, f"{year:04d}-{month:02d}-%")).fetchall()
        con.close()
        task_map = {}
        for due, title, prio in rows:
            day = int(due.split("-")[2])
            task_map.setdefault(day, []).append((title, prio))

        # Header: day names
        for col, day_name in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
            tk.Label(self.cal_frame, text=day_name, bg=T["CARD2"],
                     fg=T["MUTED"], font=FONT_SMALL,
                     width=14, anchor="center").grid(row=0, column=col,
                     padx=2, pady=2, sticky="ew")
            self.cal_frame.columnconfigure(col, weight=1)

        weeks = monthcalendar(year, month)
        for row, week in enumerate(weeks, start=1):
            self.cal_frame.rowconfigure(row, weight=1)
            for col, day in enumerate(week):
                is_today = (day == today.day and year == today.year
                            and month == today.month)
                tasks_today = task_map.get(day, [])

                cell_bg = T["ACCENT"] if is_today else T["CARD"] if day else T["BG"]
                cell = tk.Frame(self.cal_frame, bg=cell_bg,
                                highlightbackground=T["BORDER"],
                                highlightthickness=1 if day else 0,
                                height=90)
                cell.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                cell.pack_propagate(False)

                if day:
                    tk.Label(cell, text=str(day), bg=cell_bg,
                             fg="white" if is_today else T["TEXT"],
                             font=("Arial", 9, "bold")).pack(anchor="ne", padx=4)
                    for title, prio in tasks_today[:3]:
                        pcol = {"High":T["HIGH"],"Medium":T["MED"],"Low":T["LOW"]}.get(prio,T["MUTED"])
                        tk.Label(cell, text=f"• {title[:12]}", bg=cell_bg,
                                 fg=pcol, font=FONT_TINY,
                                 wraplength=90, anchor="w").pack(
                                 fill="x", padx=4)
                    if len(tasks_today) > 3:
                        tk.Label(cell, text=f"+{len(tasks_today)-3} more",
                                 bg=cell_bg, fg=T["MUTED"],
                                 font=FONT_TINY).pack(anchor="w", padx=4)

    def _cal_prev(self):
        if self._cal_month == 1: self._cal_month=12; self._cal_year-=1
        else: self._cal_month -= 1
        self.cal_month_lbl.config(
            text=f"{month_abbr[self._cal_month]} {self._cal_year}")
        self._draw_calendar()

    def _cal_next(self):
        if self._cal_month == 12: self._cal_month=1; self._cal_year+=1
        else: self._cal_month += 1
        self.cal_month_lbl.config(
            text=f"{month_abbr[self._cal_month]} {self._cal_year}")
        self._draw_calendar()

    def _cal_today(self):
        today = date.today()
        self._cal_year  = today.year
        self._cal_month = today.month
        self.cal_month_lbl.config(
            text=f"{month_abbr[self._cal_month]} {self._cal_year}")
        self._draw_calendar()

    # ══ TAB: STATISTICS ═══════════════════════════════════════════════
    def _tab_stats(self):
        T = self.T
        parent = self.content

        tk.Label(parent, text="📊  Statistics Dashboard", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_TITLE, pady=14).pack(anchor="w", padx=24)

        con = db(); c = con.cursor()
        all_tasks = c.execute(
            "SELECT priority,status,category,due_date FROM tasks "
            "WHERE user_id=? AND deleted=0", (self.user_id,)).fetchall()
        deleted   = c.execute(
            "SELECT COUNT(*) FROM tasks WHERE user_id=? AND deleted=1",
            (self.user_id,)).fetchone()[0]
        con.close()

        total     = len(all_tasks)
        completed = sum(1 for t in all_tasks if t[1]=="Completed")
        pending   = sum(1 for t in all_tasks if t[1]=="Pending")
        inprog    = sum(1 for t in all_tasks if t[1]=="In Progress")
        high_p    = sum(1 for t in all_tasks if t[0]=="High")
        overdue   = sum(1 for t in all_tasks
                        if t[3] and t[1]!="Completed"
                        and datetime.strptime(t[3],"%Y-%m-%d").date() < date.today())
        pct = round(completed/total*100) if total else 0

        # Stat cards
        stats_row = tk.Frame(parent, bg=T["BG"])
        stats_row.pack(fill="x", padx=24, pady=(0,14))

        for col, (icon, label, val, col_name) in enumerate([
            ("✅", "Total",     str(total),     "ACCENT"),
            ("🟢", "Completed", str(completed), "SUCCESS"),
            ("🟡", "Pending",   str(pending),   "WARN"),
            ("🔵", "In Progress",str(inprog),   "PENDING"),
            ("🔴", "High Prio", str(high_p),    "DANGER"),
            ("⚠",  "Overdue",   str(overdue),   "DANGER"),
        ]):
            card = tk.Frame(stats_row, bg=T["CARD"],
                            highlightbackground=T[col_name],
                            highlightthickness=2, padx=16, pady=12)
            card.grid(row=0, column=col, padx=6, sticky="ew")
            stats_row.columnconfigure(col, weight=1)
            tk.Label(card, text=icon, bg=T["CARD"], fg=T["TEXT"],
                     font=("Segoe UI Emoji", 20)).pack()
            tk.Label(card, text=val, bg=T["CARD"], fg=T[col_name],
                     font=FONT_SCORE).pack()
            tk.Label(card, text=label, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_TINY).pack()

        # Progress bar
        prog_frame = tk.Frame(parent, bg=T["CARD"], padx=20, pady=16,
                              highlightbackground=T["BORDER"], highlightthickness=1)
        prog_frame.pack(fill="x", padx=24, pady=(0,14))
        tk.Label(prog_frame, text=f"Overall Completion: {pct}%  ({completed}/{total})",
                 bg=T["CARD"], fg=T["TEXT"], font=FONT_MED).pack(anchor="w")
        bar_bg = tk.Frame(prog_frame, bg=T["BORDER"], height=18)
        bar_bg.pack(fill="x", pady=(8,0))
        bar_bg.update_idletasks()
        w = bar_bg.winfo_reqwidth()
        bar_fill = tk.Frame(bar_bg, bg=T["SUCCESS"], height=18,
                            width=int(w * pct / 100))
        bar_fill.place(x=0, y=0)
        tk.Label(bar_bg, text=f"{pct}%", bg=T["SUCCESS"] if pct>10 else T["BORDER"],
                 fg="white", font=FONT_TINY).place(x=4, y=2)

        # Category breakdown
        mid = tk.Frame(parent, bg=T["BG"])
        mid.pack(fill="x", padx=24)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        # By category
        cat_card = tk.Frame(mid, bg=T["CARD"], padx=16, pady=12,
                            highlightbackground=T["BORDER"], highlightthickness=1)
        cat_card.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        tk.Label(cat_card, text="By Category", bg=T["CARD"],
                 fg=T["TEXT"], font=FONT_MED).pack(anchor="w")
        cat_counts = {}
        for t in all_tasks: cat_counts[t[2]] = cat_counts.get(t[2],0)+1
        for cat, cnt in sorted(cat_counts.items(), key=lambda x:-x[1]):
            r = tk.Frame(cat_card, bg=T["CARD"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=cat, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_SMALL, width=12, anchor="w").pack(side="left")
            pct_c = cnt/total*100 if total else 0
            bar = tk.Frame(r, bg=T["ACCENT"], height=12,
                           width=int(pct_c*1.2))
            bar.pack(side="left", padx=4)
            tk.Label(r, text=str(cnt), bg=T["CARD"], fg=T["TEXT"],
                     font=FONT_TINY).pack(side="left")

        # By priority
        prio_card = tk.Frame(mid, bg=T["CARD"], padx=16, pady=12,
                             highlightbackground=T["BORDER"], highlightthickness=1)
        prio_card.grid(row=0, column=1, sticky="nsew")
        tk.Label(prio_card, text="By Priority", bg=T["CARD"],
                 fg=T["TEXT"], font=FONT_MED).pack(anchor="w")
        prio_colors_map = {"High":T["HIGH"],"Medium":T["MED"],"Low":T["LOW"]}
        for prio in ["High","Medium","Low"]:
            cnt = sum(1 for t in all_tasks if t[0]==prio)
            r = tk.Frame(prio_card, bg=T["CARD"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=prio, bg=T["CARD"],
                     fg=prio_colors_map[prio],
                     font=FONT_SMALL, width=10, anchor="w").pack(side="left")
            pct_p = cnt/total*100 if total else 0
            tk.Frame(r, bg=prio_colors_map[prio], height=12,
                     width=int(pct_p*1.2)).pack(side="left", padx=4)
            tk.Label(r, text=str(cnt), bg=T["CARD"], fg=T["TEXT"],
                     font=FONT_TINY).pack(side="left")

    # ══ TAB: HISTORY ══════════════════════════════════════════════════
    def _tab_history(self):
        T = self.T
        parent = self.content

        tk.Label(parent, text="🕐  Task History", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_TITLE, pady=14).pack(anchor="w", padx=24)

        # Export buttons
        exp_row = tk.Frame(parent, bg=T["BG"])
        exp_row.pack(fill="x", padx=24, pady=(0,10))
        for lbl, cmd in [("📄 Export TXT", self._export_txt),
                          ("📊 Export CSV", self._export_csv),
                          ("🗃 Backup JSON", self._backup_json)]:
            tk.Button(exp_row, text=lbl, bg=T["CARD2"], fg=T["TEXT"],
                      font=FONT_SMALL, relief="flat", bd=0, cursor="hand2",
                      padx=12, pady=6, command=cmd).pack(side="left", padx=4)

        # Restore JSON
        tk.Button(exp_row, text="📥 Restore JSON", bg=T["WARN"], fg=T["BG"],
                  font=FONT_SMALL, relief="flat", bd=0, cursor="hand2",
                  padx=12, pady=6, command=self._restore_json).pack(side="left", padx=4)

        # Tabs: deleted / completed
        tab_row = tk.Frame(parent, bg=T["BG"])
        tab_row.pack(fill="x", padx=24, pady=(0,8))
        self._hist_tab = tk.StringVar(value="deleted")
        for val, lbl in [("deleted","🗑 Deleted"),("completed","✅ Completed")]:
            tk.Radiobutton(tab_row, text=lbl, variable=self._hist_tab, value=val,
                bg=T["BG"], fg=T["TEXT"], selectcolor=T["ACCENT"],
                activebackground=T["BG"], font=FONT_BTN,
                indicatoron=0, relief="flat", padx=16, pady=6,
                command=self._load_history_list).pack(side="left", padx=4)

        # List
        list_frame = tk.Frame(parent, bg=T["BG"])
        list_frame.pack(fill="both", expand=True, padx=24)
        canvas = tk.Canvas(list_frame, bg=T["BG"], highlightthickness=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.hist_inner = tk.Frame(canvas, bg=T["BG"])
        canvas.create_window((0,0), window=self.hist_inner, anchor="nw")
        self.hist_inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self._load_history_list()

    def _load_history_list(self):
        T = self.T
        for w in self.hist_inner.winfo_children(): w.destroy()
        tab = getattr(self, "_hist_tab", tk.StringVar(value="deleted"))
        tab_val = tab.get() if hasattr(tab,"get") else "deleted"

        con = db(); c = con.cursor()
        if tab_val == "deleted":
            rows = c.execute(
                "SELECT title,description,due_date,priority,status,category,created_at "
                "FROM tasks WHERE user_id=? AND deleted=1 ORDER BY created_at DESC",
                (self.user_id,)).fetchall()
        else:
            rows = c.execute(
                "SELECT title,description,due_date,priority,status,category,completed_at "
                "FROM tasks WHERE user_id=? AND deleted=0 AND status='Completed' "
                "ORDER BY completed_at DESC",
                (self.user_id,)).fetchall()
        con.close()

        if not rows:
            tk.Label(self.hist_inner, text="No records found.",
                     bg=T["BG"], fg=T["MUTED"], font=FONT_MED).pack(pady=40)
            return

        for title,desc,due,prio,stat,cat,ts in rows:
            card = tk.Frame(self.hist_inner, bg=T["CARD"],
                            highlightbackground=T["BORDER"], highlightthickness=1)
            card.pack(fill="x", pady=3)
            tk.Label(card, text=title, bg=T["CARD"], fg=T["TEXT"],
                     font=FONT_MED).pack(anchor="w", padx=12, pady=(8,2))
            meta = f"📅 {due or '—'}  •  🏷 {cat}  •  {prio}  •  {stat}"
            if ts: meta += f"  •  {ts[:16]}"
            tk.Label(card, text=meta, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_TINY).pack(anchor="w", padx=12, pady=(0,8))

    # ══ TAB: POMODORO ════════════════════════════════════════════════
    def _tab_pomodoro(self):
        T = self.T
        parent = self.content

        tk.Label(parent, text="🍅  Pomodoro Timer", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_TITLE, pady=14).pack(anchor="w", padx=24)

        card = tk.Frame(parent, bg=T["CARD"], pady=30,
                        highlightbackground=T["BORDER"], highlightthickness=1)
        card.pack(padx=80, pady=10)

        tk.Label(card, text="Focus on one task at a time", bg=T["CARD"],
                 fg=T["MUTED"], font=FONT_SMALL).pack()

        self.pomo_display = tk.Label(card, text=self._fmt_pomo(),
                                     bg=T["CARD"], fg=T["ACCENT"],
                                     font=("Georgia", 64, "bold"))
        self.pomo_display.pack(pady=20)

        self.pomo_status = tk.Label(card, text="Ready", bg=T["CARD"],
                                    fg=T["MUTED"], font=FONT_MED)
        self.pomo_status.pack()

        btn_row = tk.Frame(card, bg=T["CARD"])
        btn_row.pack(pady=20)

        def _mbtn(text, col, cmd):
            tk.Button(btn_row, text=text, bg=col, fg="white",
                      font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
                      padx=20, pady=10, command=cmd).pack(side="left", padx=6)

        _mbtn("▶ Start",    T["SUCCESS"], self._pomo_start)
        _mbtn("⏸ Pause",   T["WARN"],    self._pomo_pause)
        _mbtn("⏹ Reset",   T["DANGER"],  self._pomo_reset)

        # Duration selector
        dur_row = tk.Frame(card, bg=T["CARD"])
        dur_row.pack(pady=10)
        tk.Label(dur_row, text="Duration (min):", bg=T["CARD"],
                 fg=T["MUTED"], font=FONT_SMALL).pack(side="left", padx=8)
        self.pomo_dur_var = tk.IntVar(value=25)
        for mins in [15, 20, 25, 30, 45]:
            tk.Radiobutton(dur_row, text=str(mins), variable=self.pomo_dur_var,
                           value=mins, bg=T["CARD"], fg=T["TEXT"],
                           selectcolor=T["ACCENT"], activebackground=T["CARD"],
                           font=FONT_SMALL,
                           command=lambda: self._pomo_set_dur()).pack(side="left",padx=4)

        # Session counter
        if not hasattr(self, "pomo_sessions"):
            self.pomo_sessions = 0
        self.pomo_sess_lbl = tk.Label(card,
            text=f"Sessions completed today: {self.pomo_sessions}",
            bg=T["CARD"], fg=T["MUTED"], font=FONT_SMALL)
        self.pomo_sess_lbl.pack(pady=6)

        # Tips
        tips = ["🧠 Break big tasks into small chunks",
                "📵 Put your phone away during focus",
                "💧 Drink water during breaks",
                "🚶 Stand up and stretch every hour"]
        tk.Label(card, text=random.choice(tips), bg=T["CARD"],
                 fg=T["MUTED"], font=FONT_TINY, pady=8).pack()

    def _fmt_pomo(self):
        m, s = divmod(self.pomo_seconds, 60)
        return f"{m:02d}:{s:02d}"

    def _pomo_set_dur(self):
        self.pomo_seconds = self.pomo_dur_var.get() * 60
        if hasattr(self, "pomo_display"):
            self.pomo_display.config(text=self._fmt_pomo())

    def _pomo_start(self):
        if self.pomodoro_running: return
        self.pomodoro_running = True
        if hasattr(self, "pomo_status"):
            self.pomo_status.config(text="🔥 Focusing…", fg=self.T["SUCCESS"])
        self._pomo_tick()

    def _pomo_tick(self):
        if not self.pomodoro_running: return
        if self.pomo_seconds <= 0:
            self.pomodoro_running = False
            self.pomo_sessions = getattr(self, "pomo_sessions", 0) + 1
            if hasattr(self, "pomo_display"):
                self.pomo_display.config(text="Done! 🎉", fg=self.T["SUCCESS"])
                self.pomo_status.config(text=f"Session {self.pomo_sessions} complete! Take a break.",
                                         fg=self.T["SUCCESS"])
                self.pomo_sess_lbl.config(
                    text=f"Sessions completed today: {self.pomo_sessions}")
            messagebox.showinfo("Pomodoro", "⏰ Time's up! Take a break.")
            self.pomo_seconds = self.pomo_dur_var.get() * 60
            return
        self.pomo_seconds -= 1
        if hasattr(self, "pomo_display"):
            self.pomo_display.config(text=self._fmt_pomo())
        self._pomo_id = self.root.after(1000, self._pomo_tick)

    def _pomo_pause(self):
        self.pomodoro_running = False
        if self._pomo_id:
            self.root.after_cancel(self._pomo_id)
        if hasattr(self, "pomo_status"):
            self.pomo_status.config(text="⏸ Paused", fg=self.T["WARN"])

    def _pomo_reset(self):
        self._pomo_pause()
        self.pomo_seconds = self.pomo_dur_var.get() * 60 if hasattr(self,"pomo_dur_var") else 25*60
        if hasattr(self, "pomo_display"):
            self.pomo_display.config(text=self._fmt_pomo(), fg=self.T["ACCENT"])
            self.pomo_status.config(text="Ready", fg=self.T["MUTED"])

    # ══ TAB: SETTINGS ════════════════════════════════════════════════
    def _tab_settings(self):
        T = self.T
        parent = self.content

        tk.Label(parent, text="⚙️  Settings", bg=T["BG"],
                 fg=T["TEXT"], font=FONT_TITLE, pady=14).pack(anchor="w", padx=24)

        card = tk.Frame(parent, bg=T["CARD"], padx=28, pady=24,
                        highlightbackground=T["BORDER"], highlightthickness=1)
        card.pack(fill="x", padx=24, pady=(0,16))

        def row_lbl(text):
            tk.Label(card, text=text, bg=T["CARD"], fg=T["TEXT"],
                     font=FONT_MED).pack(anchor="w", pady=(14,2))

        def row_sub(text):
            tk.Label(card, text=text, bg=T["CARD"], fg=T["MUTED"],
                     font=FONT_TINY).pack(anchor="w", pady=(0,6))

        # Theme
        row_lbl("🎨 Theme")
        row_sub("Switch between dark and light mode")
        thm_row = tk.Frame(card, bg=T["CARD"])
        thm_row.pack(anchor="w")
        for val, lbl in [("dark","🌙 Dark"),("light","☀ Light")]:
            tk.Radiobutton(thm_row, text=lbl, variable=self.theme_name, value=val,
                bg=T["CARD"], fg=T["TEXT"], selectcolor=T["ACCENT"],
                activebackground=T["CARD"], font=FONT_BTN,
                indicatoron=0, relief="flat", padx=14, pady=6,
                command=self._toggle_theme).pack(side="left", padx=4)

        tk.Frame(card, bg=T["BORDER"], height=1).pack(fill="x", pady=12)

        # Account info
        row_lbl("👤 Account")
        tk.Label(card, text=f"Logged in as: {self.username}",
                 bg=T["CARD"], fg=T["MUTED"], font=FONT_SMALL).pack(anchor="w")

        tk.Frame(card, bg=T["BORDER"], height=1).pack(fill="x", pady=12)

        # Data management
        row_lbl("💾 Data Management")
        row_sub("Export, backup, or restore your tasks")
        btn_row = tk.Frame(card, bg=T["CARD"])
        btn_row.pack(anchor="w")
        for text, col, cmd in [
            ("Export TXT", T["ACCENT"],   self._export_txt),
            ("Export CSV", T["SUCCESS"],  self._export_csv),
            ("Backup JSON",T["WARN"],     self._backup_json),
            ("Restore JSON",T["DANGER"],  self._restore_json),
        ]:
            tk.Button(btn_row, text=text, bg=col, fg="white",
                      font=FONT_SMALL, relief="flat", bd=0, cursor="hand2",
                      padx=12, pady=6, command=cmd).pack(side="left", padx=4)

        tk.Frame(card, bg=T["BORDER"], height=1).pack(fill="x", pady=12)

        # AI suggestion
        row_lbl("🤖 AI Task Suggestion")
        row_sub("Get smart priority suggestions for your tasks")
        tk.Button(card, text="✨ Suggest Priorities", command=self._ai_suggest,
                  bg=T["ACCENT2"], fg="white", font=FONT_BTN,
                  relief="flat", bd=0, cursor="hand2",
                  padx=16, pady=8).pack(anchor="w")

    # ══ HELPERS ═══════════════════════════════════════════════════════
    def _update_progress_sidebar(self):
        if not hasattr(self, "prog_lbl"): return
        con = db(); c = con.cursor()
        total = c.execute(
            "SELECT COUNT(*) FROM tasks WHERE user_id=? AND deleted=0",
            (self.user_id,)).fetchone()[0]
        done  = c.execute(
            "SELECT COUNT(*) FROM tasks WHERE user_id=? AND deleted=0 AND status='Completed'",
            (self.user_id,)).fetchone()[0]
        con.close()
        pct = round(done/total*100) if total else 0
        self.prog_lbl.config(text=f"✅ {done}/{total} done ({pct}%)")

    def _toggle_theme(self):
        name = self.theme_name.get()
        # If called from button (not radio), toggle
        if name == "dark":
            self.theme_name.set("light"); name = "light"
        else:
            self.theme_name.set("dark"); name = "dark"
        self.T = THEMES[name]
        self._build()

    def _logout(self):
        self._pomo_pause()
        if self._notif_id:
            self.root.after_cancel(self._notif_id)
        for w in self.root.winfo_children(): w.destroy()
        self.root.geometry("480x540")
        LoginScreen(self.root, _on_login)

    # ── Export ────────────────────────────────────────────────────────
    def _get_all_tasks(self):
        con = db(); c = con.cursor()
        rows = c.execute(
            "SELECT title,description,notes,due_date,priority,status,"
            "category,recurrence,created_at FROM tasks "
            "WHERE user_id=? AND deleted=0", (self.user_id,)).fetchall()
        con.close()
        return rows

    def _export_txt(self):
        tasks = self._get_all_tasks()
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files","*.txt")],
            initialfile="tasks_export.txt")
        if not path: return
        with open(path,"w",encoding="utf-8") as f:
            f.write(f"TaskMaster Pro — {self.username}\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("="*60+"\n\n")
            for t in tasks:
                f.write(f"Title:      {t[0]}\n")
                f.write(f"Desc:       {t[1]}\n")
                f.write(f"Notes:      {t[2]}\n")
                f.write(f"Due:        {t[3]}\n")
                f.write(f"Priority:   {t[4]}  |  Status: {t[5]}\n")
                f.write(f"Category:   {t[6]}  |  Recurrence: {t[7]}\n")
                f.write("-"*40+"\n")
        messagebox.showinfo("Export", f"Exported {len(tasks)} tasks to TXT!")

    def _export_csv(self):
        tasks = self._get_all_tasks()
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files","*.csv")],
            initialfile="tasks_export.csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title","Description","Notes","Due Date",
                             "Priority","Status","Category","Recurrence","Created"])
            writer.writerows(tasks)
        messagebox.showinfo("Export", f"Exported {len(tasks)} tasks to CSV!")

    def _backup_json(self):
        tasks = self._get_all_tasks()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files","*.json")],
            initialfile="tasks_backup.json")
        if not path: return
        keys = ["title","description","notes","due_date","priority",
                "status","category","recurrence","created_at"]
        data = [dict(zip(keys,t)) for t in tasks]
        with open(path,"w",encoding="utf-8") as f:
            json.dump({"user": self.username,
                       "exported": datetime.now().isoformat(),
                       "tasks": data}, f, indent=2)
        messagebox.showinfo("Backup", f"Backed up {len(tasks)} tasks!")

    def _restore_json(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files","*.json")])
        if not path: return
        try:
            with open(path,encoding="utf-8") as f:
                data = json.load(f)
            tasks = data.get("tasks",[])
            con = db(); c = con.cursor()
            imported = 0
            for t in tasks:
                c.execute("""INSERT INTO tasks
                    (user_id,title,description,notes,due_date,priority,status,
                     category,recurrence,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (self.user_id, t.get("title",""),
                     t.get("description",""), t.get("notes",""),
                     t.get("due_date"), t.get("priority","Medium"),
                     t.get("status","Pending"), t.get("category","Work"),
                     t.get("recurrence","None"),
                     t.get("created_at", datetime.now().isoformat())))
                imported += 1
            con.commit(); con.close()
            messagebox.showinfo("Restore", f"Restored {imported} tasks!")
            self._update_progress_sidebar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── AI Suggestion ─────────────────────────────────────────────────
    def _ai_suggest(self):
        con = db(); c = con.cursor()
        tasks = c.execute(
            "SELECT id,title,due_date,priority FROM tasks "
            "WHERE user_id=? AND deleted=0 AND status!='Completed'",
            (self.user_id,)).fetchall()
        con.close()
        if not tasks:
            messagebox.showinfo("AI Suggestion", "No pending tasks to analyze!"); return

        updated = 0
        today = date.today()
        for tid, title, due, prio in tasks:
            new_prio = prio
            if due:
                try:
                    delta = (datetime.strptime(due,"%Y-%m-%d").date()-today).days
                    if delta < 0:    new_prio = "High"
                    elif delta <= 2: new_prio = "High"
                    elif delta <= 7: new_prio = "Medium"
                    else:            new_prio = "Low"
                except: pass
            else:
                new_prio = "Low"
            if new_prio != prio:
                con = db(); c = con.cursor()
                c.execute("UPDATE tasks SET priority=? WHERE id=?", (new_prio,tid))
                con.commit(); con.close()
                updated += 1

        messagebox.showinfo("AI Suggestion",
            f"✨ Analyzed {len(tasks)} tasks.\n"
            f"Updated {updated} task priorities based on due dates!")
        if self.active_tab.get() == "tasks":
            self._load_tasks()

    # ── Reminders ─────────────────────────────────────────────────────
    def _start_reminder_thread(self):
        self._check_reminders()

    def _check_reminders(self):
        try:
            con = db(); c = con.cursor()
            tomorrow = (date.today()+timedelta(days=1)).isoformat()
            tasks = c.execute(
                "SELECT title FROM tasks WHERE user_id=? AND deleted=0 "
                "AND status!='Completed' AND due_date=?",
                (self.user_id, tomorrow)).fetchall()
            con.close()
            if tasks:
                names = ", ".join(t[0] for t in tasks[:3])
                if len(tasks)>3: names += f" +{len(tasks)-3} more"
                self._show_notif(f"⏰ Due Tomorrow: {names}")
        except: pass
        self._notif_id = self.root.after(60000, self._check_reminders)

    def _show_notif(self, msg):
        T = self.T
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.geometry(f"360x60+{self.root.winfo_x()+800}+{self.root.winfo_y()+20}")
        notif.configure(bg=T["WARN"])
        tk.Label(notif, text=msg, bg=T["WARN"], fg=T["BG"],
                 font=FONT_SMALL, wraplength=340).pack(expand=True)
        notif.after(5000, notif.destroy)


# ══════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════
_root = None

def _on_login(uid, uname):
    global _root
    _root.geometry("1200x750")
    TodoApp(_root, uid, uname)

def main():
    global _root
    init_db()
    _root = tk.Tk()
    _root.title("TaskMaster Pro")
    _root.geometry("480x540")
    _root.configure(bg=THEMES["dark"]["BG"])

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox",
                    fieldbackground=THEMES["dark"]["ENTRY"],
                    background=THEMES["dark"]["ENTRY"],
                    foreground=THEMES["dark"]["TEXT"],
                    selectbackground=THEMES["dark"]["ACCENT"])

    LoginScreen(_root, _on_login)
    _root.mainloop()

if __name__ == "__main__":
    main()
