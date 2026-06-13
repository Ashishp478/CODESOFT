"""
Advanced Password Generator
============================
Features:
 - Uppercase / Lowercase / Digits / Symbols
 - Exclude similar characters (0,O,1,l,I)
 - Password strength checker
 - Multiple password generation
 - Copy to clipboard
 - Save history to file (with timestamp)
 - Password expiry suggestion
 - QR Code generation (popup window)
 - Random Username generator
 - Unique password guarantee (no duplicates in session)
 - Dark Mode / Light Mode toggle
 - Full Tkinter GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import string
import secrets
import datetime
import os
import sys

# ── optional imports ──────────────────────────────────
try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

try:
    import qrcode
    from PIL import Image, ImageTk
    HAS_QR = True
except ImportError:
    HAS_QR = False

# ═══════════════════════════════════════════════════════
#  THEMES
# ═══════════════════════════════════════════════════════
DARK = {
    "bg":         "#0d1117",
    "bg2":        "#161b22",
    "bg3":        "#21262d",
    "border":     "#30363d",
    "text":       "#e6edf3",
    "muted":      "#8b949e",
    "accent":     "#58a6ff",
    "accent2":    "#3fb950",
    "danger":     "#f85149",
    "warn":       "#d29922",
    "card":       "#1c2128",
    "btn":        "#238636",
    "btn_fg":     "#ffffff",
    "btn2":       "#21262d",
    "btn2_fg":    "#c9d1d9",
    "entry_bg":   "#0d1117",
    "entry_fg":   "#e6edf3",
    "sel":        "#1f6feb",
    "weak":       "#f85149",
    "medium":     "#d29922",
    "strong":     "#3fb950",
    "vstrong":    "#58a6ff",
}

LIGHT = {
    "bg":         "#ffffff",
    "bg2":        "#f6f8fa",
    "bg3":        "#eaeef2",
    "border":     "#d0d7de",
    "text":       "#1f2328",
    "muted":      "#636c76",
    "accent":     "#0969da",
    "accent2":    "#1a7f37",
    "danger":     "#d1242f",
    "warn":       "#9a6700",
    "card":       "#ffffff",
    "btn":        "#1a7f37",
    "btn_fg":     "#ffffff",
    "btn2":       "#f6f8fa",
    "btn2_fg":    "#1f2328",
    "entry_bg":   "#ffffff",
    "entry_fg":   "#1f2328",
    "sel":        "#0969da",
    "weak":       "#d1242f",
    "medium":     "#9a6700",
    "strong":     "#1a7f37",
    "vstrong":    "#0969da",
}

# ═══════════════════════════════════════════════════════
#  CHARACTER SETS
# ═══════════════════════════════════════════════════════
SIMILAR = set("0O1lI")
UPPER   = string.ascii_uppercase
LOWER   = string.ascii_lowercase
DIGITS  = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?/"

ADJECTIVES = [
    "Swift","Brave","Silent","Cosmic","Electric","Shadow","Iron","Crystal",
    "Storm","Hyper","Neon","Dark","Wild","Quick","Phantom","Blazing","Frozen",
    "Turbo","Mystic","Cyber","Rogue","Glitch","Stealth","Epic","Omega","Ultra",
]
NOUNS = [
    "Fox","Wolf","Hawk","Tiger","Dragon","Falcon","Panther","Viper","Eagle",
    "Phoenix","Cobra","Shark","Lynx","Jaguar","Raven","Cipher","Ghost","Specter",
    "Nova","Vertex","Nexus","Zenith","Orbit","Pulse","Flux",
]

# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════
def build_charset(upper, lower, digits, symbols, no_similar):
    pool = ""
    if upper:   pool += UPPER
    if lower:   pool += LOWER
    if digits:  pool += DIGITS
    if symbols: pool += SYMBOLS
    if no_similar:
        pool = "".join(c for c in pool if c not in SIMILAR)
    return pool


def generate_password(length, pool, guarantee_all, upper, lower, digits, symbols):
    """Generate one secure password; guarantee at least 1 char from each chosen set."""
    if not pool:
        return ""
    required = []
    if guarantee_all:
        src_upper   = "".join(c for c in UPPER   if c in pool)
        src_lower   = "".join(c for c in LOWER   if c in pool)
        src_digits  = "".join(c for c in DIGITS  if c in pool)
        src_symbols = "".join(c for c in SYMBOLS if c in pool)
        if upper   and src_upper:   required.append(secrets.choice(src_upper))
        if lower   and src_lower:   required.append(secrets.choice(src_lower))
        if digits  and src_digits:  required.append(secrets.choice(src_digits))
        if symbols and src_symbols: required.append(secrets.choice(src_symbols))
    needed = max(0, length - len(required))
    rest   = [secrets.choice(pool) for _ in range(needed)]
    combo  = required + rest
    secrets.SystemRandom().shuffle(combo)
    return "".join(combo)


def password_strength(pwd):
    score = 0
    if len(pwd) >= 8:  score += 1
    if len(pwd) >= 12: score += 1
    if len(pwd) >= 16: score += 1
    if any(c in UPPER   for c in pwd): score += 1
    if any(c in LOWER   for c in pwd): score += 1
    if any(c in DIGITS  for c in pwd): score += 1
    if any(c in SYMBOLS for c in pwd): score += 1
    if score <= 2: return "Weak",   0
    if score <= 4: return "Medium", 1
    if score <= 5: return "Strong", 2
    return "Very Strong", 3


def random_username():
    adj  = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    num  = random.randint(1, 999)
    return f"{adj}{noun}{num}"


def expiry_suggestion(length):
    if length < 8:  return "Change immediately — too short!"
    if length < 12: return "Suggested expiry: 30 days"
    if length < 16: return "Suggested expiry: 90 days"
    return "Suggested expiry: 180 days"


def copy_to_clipboard(text):
    if HAS_CLIPBOARD:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            pass
    # fallback via tk
    return False


def save_history(entries, path):
    with open(path, "a", encoding="utf-8") as f:
        for e in entries:
            f.write(e + "\n")


# ═══════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════
class PasswordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔐 Advanced Password Generator")
        self.geometry("780x820")
        self.resizable(True, True)
        self.minsize(680, 720)

        self._dark      = True
        self._theme     = DARK
        self._history   = []          # list of strings
        self._generated = set()       # unique passwords this session
        self._passwords = []          # last batch of passwords

        self._build_ui()
        self._apply_theme()

    # ─── UI BUILD ─────────────────────────────────────
    def _build_ui(self):
        # ── title bar ─────────────────────────────────
        self._topbar = tk.Frame(self, pady=10)
        self._topbar.pack(fill="x", padx=20)

        self._lbl_title = tk.Label(
            self._topbar, text="🔐  Advanced Password Generator",
            font=("Consolas", 18, "bold"))
        self._lbl_title.pack(side="left")

        self._btn_theme = tk.Button(
            self._topbar, text="☀️  Light Mode",
            font=("Consolas", 10), relief="flat", bd=0,
            cursor="hand2", padx=12, pady=4,
            command=self._toggle_theme)
        self._btn_theme.pack(side="right")

        # ── two columns ───────────────────────────────
        cols = tk.Frame(self)
        cols.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        left  = tk.Frame(cols)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = tk.Frame(cols)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._build_left(left)
        self._build_right(right)

        # ── bottom buttons ─────────────────────────────
        self._bot = tk.Frame(self, pady=10)
        self._bot.pack(fill="x", padx=20)

        self._btn_gen = tk.Button(
            self._bot, text="⚡  Generate Password",
            font=("Consolas", 12, "bold"), relief="flat", bd=0,
            cursor="hand2", padx=20, pady=8,
            command=self._on_generate)
        self._btn_gen.pack(side="left", padx=(0, 8))

        self._btn_multi = tk.Button(
            self._bot, text="🗂  Generate Multiple",
            font=("Consolas", 11), relief="flat", bd=0,
            cursor="hand2", padx=16, pady=8,
            command=self._on_generate_multi)
        self._btn_multi.pack(side="left", padx=(0, 8))

        self._btn_user = tk.Button(
            self._bot, text="👤  Random Username",
            font=("Consolas", 11), relief="flat", bd=0,
            cursor="hand2", padx=16, pady=8,
            command=self._on_username)
        self._btn_user.pack(side="left")

        self._btn_save = tk.Button(
            self._bot, text="💾  Save History",
            font=("Consolas", 11), relief="flat", bd=0,
            cursor="hand2", padx=16, pady=8,
            command=self._on_save)
        self._btn_save.pack(side="right")

        self._btn_clear = tk.Button(
            self._bot, text="🗑  Clear",
            font=("Consolas", 11), relief="flat", bd=0,
            cursor="hand2", padx=12, pady=8,
            command=self._on_clear)
        self._btn_clear.pack(side="right", padx=8)

    def _build_left(self, parent):
        t = self._theme

        # ── LENGTH ────────────────────────────────────
        sec = self._card(parent, "📏  Password Length")
        row = tk.Frame(sec)
        row.pack(fill="x", pady=(4, 0))

        self._len_var = tk.IntVar(value=16)
        self._len_lbl = tk.Label(row, text="16",
                                  font=("Consolas", 14, "bold"), width=4)
        self._len_lbl.pack(side="right")

        self._len_slider = tk.Scale(
            row, from_=4, to=64,
            orient="horizontal", variable=self._len_var,
            showvalue=False, length=200,
            command=lambda v: self._len_lbl.config(text=str(int(float(v)))))
        self._len_slider.pack(side="left", fill="x", expand=True)

        # ── COUNT ─────────────────────────────────────
        sec2 = self._card(parent, "🔢  Number of Passwords")
        row2 = tk.Frame(sec2)
        row2.pack(fill="x", pady=(4, 0))
        self._cnt_var = tk.IntVar(value=1)
        self._cnt_lbl = tk.Label(row2, text="1",
                                  font=("Consolas", 14, "bold"), width=4)
        self._cnt_lbl.pack(side="right")
        self._cnt_slider = tk.Scale(
            row2, from_=1, to=20,
            orient="horizontal", variable=self._cnt_var,
            showvalue=False, length=200,
            command=lambda v: self._cnt_lbl.config(text=str(int(float(v)))))
        self._cnt_slider.pack(side="left", fill="x", expand=True)

        # ── CHARACTER OPTIONS ──────────────────────────
        sec3 = self._card(parent, "🔡  Character Types")

        self._use_upper   = tk.BooleanVar(value=True)
        self._use_lower   = tk.BooleanVar(value=True)
        self._use_digits  = tk.BooleanVar(value=True)
        self._use_symbols = tk.BooleanVar(value=False)
        self._no_similar  = tk.BooleanVar(value=False)
        self._guarantee   = tk.BooleanVar(value=True)

        opts = [
            (self._use_upper,   "🔠  Uppercase  (A–Z)"),
            (self._use_lower,   "🔡  Lowercase  (a–z)"),
            (self._use_digits,  "🔢  Numbers    (0–9)"),
            (self._use_symbols, "🔣  Symbols    (!@#$…)"),
            (self._no_similar,  "🚫  Exclude similar  (0,O,1,l,I)"),
            (self._guarantee,   "✅  Guarantee one of each type"),
        ]
        for var, label in opts:
            cb = tk.Checkbutton(sec3, text=label, variable=var,
                                font=("Consolas", 10), anchor="w",
                                relief="flat", bd=0, cursor="hand2")
            cb.pack(fill="x", pady=1)
            self._checkboxes = getattr(self, "_checkboxes", [])
            self._checkboxes.append(cb)

        # ── USERNAME DISPLAY ───────────────────────────
        sec4 = self._card(parent, "👤  Generated Username")
        self._username_var = tk.StringVar(value="—")
        usr_row = tk.Frame(sec4)
        usr_row.pack(fill="x")
        self._usr_entry = tk.Entry(usr_row, textvariable=self._username_var,
                                    font=("Consolas", 12), relief="flat",
                                    state="readonly", justify="center")
        self._usr_entry.pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(usr_row, text="📋", font=("Consolas", 11),
                  relief="flat", bd=0, cursor="hand2", padx=6,
                  command=lambda: self._copy_text(self._username_var.get())
                  ).pack(side="right")

    def _build_right(self, parent):
        # ── OUTPUT ────────────────────────────────────
        sec = self._card(parent, "🔑  Generated Password(s)")

        self._out_text = tk.Text(sec, height=6, font=("Consolas", 12),
                                  relief="flat", wrap="word",
                                  state="disabled")
        self._out_text.pack(fill="both", expand=True, pady=(4, 0))

        action_row = tk.Frame(sec)
        action_row.pack(fill="x", pady=(6, 0))

        self._btn_copy = tk.Button(action_row, text="📋  Copy First",
            font=("Consolas", 10), relief="flat", bd=0,
            cursor="hand2", padx=12, pady=4,
            command=self._on_copy)
        self._btn_copy.pack(side="left", padx=(0, 6))

        self._btn_qr = tk.Button(action_row, text="📷  QR Code",
            font=("Consolas", 10), relief="flat", bd=0,
            cursor="hand2", padx=12, pady=4,
            command=self._on_qr)
        self._btn_qr.pack(side="left")

        self._copy_status = tk.Label(action_row, text="",
                                      font=("Consolas", 9))
        self._copy_status.pack(side="right")

        # ── STRENGTH ──────────────────────────────────
        sec2 = self._card(parent, "💪  Password Strength")

        self._strength_lbl = tk.Label(sec2, text="—",
                                       font=("Consolas", 13, "bold"))
        self._strength_lbl.pack(anchor="w")

        self._strength_bar_bg = tk.Frame(sec2, height=8)
        self._strength_bar_bg.pack(fill="x", pady=(4, 0))
        self._strength_bar = tk.Frame(self._strength_bar_bg, height=8)
        self._strength_bar.place(x=0, y=0, relheight=1.0, relwidth=0)

        self._expiry_lbl = tk.Label(sec2, text="",
                                     font=("Consolas", 9), anchor="w")
        self._expiry_lbl.pack(fill="x", pady=(4, 0))

        # ── HISTORY ───────────────────────────────────
        sec3 = self._card(parent, "📜  Session History")

        self._hist_text = tk.Text(sec3, height=10, font=("Consolas", 9),
                                   relief="flat", state="disabled",
                                   wrap="none")
        sb = tk.Scrollbar(sec3, command=self._hist_text.yview)
        self._hist_text.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._hist_text.pack(fill="both", expand=True, pady=(4, 0))

    def _card(self, parent, title):
        """Create a labelled card section, return inner frame."""
        frame = tk.Frame(parent, pady=6)
        frame.pack(fill="x", pady=(0, 10))
        tk.Label(frame, text=title,
                 font=("Consolas", 10, "bold")).pack(anchor="w")
        sep = tk.Frame(frame, height=1)
        sep.pack(fill="x", pady=(2, 6))
        self._cards = getattr(self, "_cards", [])
        self._seps  = getattr(self, "_seps",  [])
        self._cards.append(frame)
        self._seps.append(sep)
        return frame

    # ─── ACTIONS ──────────────────────────────────────
    def _on_generate(self):
        pool = build_charset(
            self._use_upper.get(), self._use_lower.get(),
            self._use_digits.get(), self._use_symbols.get(),
            self._no_similar.get())
        if not pool:
            messagebox.showwarning("No characters",
                "Please select at least one character type.")
            return

        length = self._len_var.get()
        pwd    = self._unique_password(length, pool)
        if pwd is None:
            messagebox.showinfo("Exhausted",
                "All possible passwords of this type have been generated!")
            return

        self._passwords = [pwd]
        self._show_passwords([pwd])
        self._update_strength(pwd)
        self._add_history([pwd])

    def _on_generate_multi(self):
        pool = build_charset(
            self._use_upper.get(), self._use_lower.get(),
            self._use_digits.get(), self._use_symbols.get(),
            self._no_similar.get())
        if not pool:
            messagebox.showwarning("No characters",
                "Please select at least one character type.")
            return

        count  = self._cnt_var.get()
        length = self._len_var.get()
        pwds   = []
        for _ in range(count):
            p = self._unique_password(length, pool)
            if p:
                pwds.append(p)

        if not pwds:
            messagebox.showinfo("Exhausted",
                "Could not generate unique passwords. Try different options.")
            return

        self._passwords = pwds
        self._show_passwords(pwds)
        self._update_strength(pwds[0])
        self._add_history(pwds)

    def _unique_password(self, length, pool, max_tries=500):
        for _ in range(max_tries):
            pwd = generate_password(
                length, pool, self._guarantee.get(),
                self._use_upper.get(), self._use_lower.get(),
                self._use_digits.get(), self._use_symbols.get())
            if pwd not in self._generated:
                self._generated.add(pwd)
                return pwd
        return None

    def _on_username(self):
        usr = random_username()
        self._username_var.set(usr)
        self._add_history([f"[USERNAME] {usr}"])

    def _on_copy(self):
        if not self._passwords:
            return
        text = self._passwords[0]
        ok = copy_to_clipboard(text)
        if not ok:
            # fallback: use tk clipboard
            self.clipboard_clear()
            self.clipboard_append(text)
        self._copy_status.config(text="✅ Copied!")
        self.after(2000, lambda: self._copy_status.config(text=""))

    def _copy_text(self, text):
        if not text or text == "—":
            return
        ok = copy_to_clipboard(text)
        if not ok:
            self.clipboard_clear()
            self.clipboard_append(text)
        self._copy_status.config(text="✅ Copied!")
        self.after(2000, lambda: self._copy_status.config(text=""))

    def _on_qr(self):
        if not self._passwords:
            messagebox.showinfo("No password", "Generate a password first.")
            return
        if not HAS_QR:
            messagebox.showerror("Missing library",
                "Install qrcode and Pillow:\n  pip install qrcode pillow")
            return
        pwd = self._passwords[0]
        img = qrcode.make(pwd)
        img = img.resize((280, 280), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        win = tk.Toplevel(self)
        win.title("QR Code")
        win.resizable(False, False)
        win.configure(bg=self._theme["bg"])

        tk.Label(win, text="📷  Scan to get password",
                 bg=self._theme["bg"], fg=self._theme["text"],
                 font=("Consolas", 11, "bold")).pack(pady=(12, 4))
        lbl = tk.Label(win, image=photo, bg=self._theme["bg"])
        lbl.image = photo
        lbl.pack(padx=20, pady=10)

        pw_lbl = tk.Label(win, text=pwd,
                          bg=self._theme["bg"], fg=self._theme["accent"],
                          font=("Consolas", 9), wraplength=260)
        pw_lbl.pack(pady=(0, 12))
        tk.Button(win, text="Close", command=win.destroy,
                  font=("Consolas", 10), relief="flat",
                  bg=self._theme["btn2"], fg=self._theme["btn2_fg"],
                  cursor="hand2", padx=16, pady=6).pack(pady=(0, 12))

    def _on_save(self):
        if not self._history:
            messagebox.showinfo("Nothing to save", "Generate some passwords first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All", "*.*")],
            initialfile="password_history.txt",
            title="Save Password History")
        if not path:
            return
        save_history(self._history, path)
        messagebox.showinfo("Saved", f"History saved to:\n{path}")

    def _on_clear(self):
        self._passwords = []
        self._generated = set()
        self._history   = []
        self._set_text(self._out_text, "")
        self._set_text(self._hist_text, "")
        self._strength_lbl.config(text="—", fg=self._theme["muted"])
        self._strength_bar.place(relwidth=0)
        self._expiry_lbl.config(text="")
        self._username_var.set("—")

    # ─── DISPLAY HELPERS ──────────────────────────────
    def _show_passwords(self, pwds):
        self._set_text(self._out_text, "\n".join(pwds))

    def _set_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def _update_strength(self, pwd):
        t      = self._theme
        label, level = password_strength(pwd)
        colors = [t["weak"], t["medium"], t["strong"], t["vstrong"]]
        widths = [0.25, 0.5, 0.75, 1.0]
        col    = colors[level]
        self._strength_lbl.config(text=f"{'⚠️' if level<2 else '✅'}  {label}",
                                   fg=col)
        self._strength_bar.config(bg=col)
        self._strength_bar.place(relwidth=widths[level])
        self._expiry_lbl.config(
            text="⏰  " + expiry_suggestion(self._len_var.get()),
            fg=t["muted"])

    def _add_history(self, entries):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for e in entries:
            line = f"[{ts}]  {e}"
            self._history.append(line)

        self._hist_text.config(state="normal")
        for e in entries:
            ts2 = datetime.datetime.now().strftime("%H:%M:%S")
            self._hist_text.insert("1.0", f"{ts2}  {e}\n")
        self._hist_text.config(state="disabled")

    # ─── THEME ────────────────────────────────────────
    def _toggle_theme(self):
        self._dark  = not self._dark
        self._theme = DARK if self._dark else LIGHT
        self._apply_theme()

    def _apply_theme(self):
        t = self._theme

        self.configure(bg=t["bg"])

        def _style(w):
            cls = w.__class__.__name__
            if cls == "Frame":
                try: w.config(bg=t["bg"])
                except: pass
            elif cls == "Label":
                try: w.config(bg=t["bg"], fg=t["text"])
                except: pass
            elif cls in ("Button",):
                pass   # handled individually
            elif cls == "Text":
                try: w.config(bg=t["entry_bg"], fg=t["entry_fg"],
                               insertbackground=t["text"],
                               selectbackground=t["sel"])
                except: pass
            elif cls == "Entry":
                try: w.config(bg=t["entry_bg"], fg=t["entry_fg"],
                               insertbackground=t["text"],
                               readonlybackground=t["bg2"])
                except: pass
            elif cls == "Checkbutton":
                try: w.config(bg=t["bg"], fg=t["text"],
                               selectcolor=t["bg3"],
                               activebackground=t["bg"],
                               activeforeground=t["accent"])
                except: pass
            elif cls == "Scale":
                try: w.config(bg=t["bg"], fg=t["text"],
                               troughcolor=t["bg3"],
                               activebackground=t["accent"])
                except: pass
            elif cls == "Scrollbar":
                try: w.config(bg=t["bg3"], troughcolor=t["bg"],
                               activebackground=t["accent"])
                except: pass
            for child in w.winfo_children():
                _style(child)

        _style(self)

        # Override specific widgets
        self._lbl_title.config(bg=t["bg"], fg=t["accent"],
                                font=("Consolas", 18, "bold"))
        self._btn_theme.config(
            bg=t["btn2"], fg=t["btn2_fg"],
            text="☀️  Light Mode" if self._dark else "🌙  Dark Mode")
        self._btn_gen.config(bg=t["btn"], fg=t["btn_fg"])
        self._btn_multi.config(bg=t["btn2"], fg=t["btn2_fg"])
        self._btn_user.config(bg=t["btn2"], fg=t["btn2_fg"])
        self._btn_save.config(bg=t["btn2"], fg=t["btn2_fg"])
        self._btn_clear.config(bg=t["bg3"], fg=t["danger"])
        self._btn_copy.config(bg=t["btn2"], fg=t["btn2_fg"])
        self._btn_qr.config(bg=t["btn2"], fg=t["btn2_fg"])
        self._copy_status.config(bg=t["bg"], fg=t["accent2"])
        self._username_var  # just to silence linter

        # Strength bar bg
        self._strength_bar_bg.config(bg=t["bg3"])

        # Card titles & seps
        for card in getattr(self, "_cards", []):
            card.config(bg=t["bg"])
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=t["bg"], fg=t["accent"])
        for sep in getattr(self, "_seps", []):
            sep.config(bg=t["border"])

        # Slider labels
        self._len_lbl.config(bg=t["bg"], fg=t["text"])
        self._cnt_lbl.config(bg=t["bg"], fg=t["text"])
        self._expiry_lbl.config(bg=t["bg"])
        self._strength_lbl.config(bg=t["bg"])

        # Checkboxes
        for cb in getattr(self, "_checkboxes", []):
            cb.config(bg=t["bg"], fg=t["text"],
                      selectcolor=t["bg3"],
                      activebackground=t["bg"],
                      activeforeground=t["accent"])


# ═══════════════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    app = PasswordApp()
    app.mainloop()