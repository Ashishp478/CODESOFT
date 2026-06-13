import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import re
import csv

DATA_FILE = "contacts.json"

def load_contacts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

def validate_phone(phone):
    return bool(re.match(r"^[\d\s\+\-\(\)]{7,15}$", phone.strip()))

def validate_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip())) if email.strip() else True

BG       = "#0f0f13"
CARD     = "#1a1a24"
BORDER   = "#2a2a3a"
ACCENT   = "#6c63ff"
ACCENT2  = "#ff6584"
TEXT     = "#e8e8f0"
SUBTEXT  = "#888899"
SUCCESS  = "#43e97b"
DANGER   = "#ff4d6d"
ENTRY_BG = "#252535"

FONT_TITLE = ("Georgia", 22, "bold")
FONT_HEAD  = ("Georgia", 13, "bold")
FONT_BODY  = ("Courier New", 11)
FONT_SMALL = ("Courier New", 9)
FONT_LABEL = ("Courier New", 10, "bold")
FONT_BTN   = ("Georgia", 10, "bold")

def styled_button(parent, text, command, color=ACCENT, width=14, **kw):
    btn = tk.Button(parent, text=text, command=command, bg=color, fg=TEXT,
        font=FONT_BTN, relief="flat", bd=0, cursor="hand2",
        activebackground=color, activeforeground=TEXT, width=width, pady=6, **kw)
    def on_enter(e): btn.config(bg=_lighten(color))
    def on_leave(e): btn.config(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def _lighten(hex_color):
    r = min(255, int(hex_color[1:3], 16) + 30)
    g = min(255, int(hex_color[3:5], 16) + 30)
    b = min(255, int(hex_color[5:7], 16) + 30)
    return f"#{r:02x}{g:02x}{b:02x}"

def labeled_entry(parent, label, row, show=None):
    tk.Label(parent, text=label, bg=CARD, fg=SUBTEXT, font=FONT_LABEL).grid(row=row, column=0, sticky="w", pady=(8,2))
    var = tk.StringVar()
    e = tk.Entry(parent, textvariable=var, bg=ENTRY_BG, fg=TEXT, font=FONT_BODY,
        relief="flat", bd=0, insertbackground=ACCENT, highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=ACCENT, show=show or "")
    e.grid(row=row+1, column=0, columnspan=2, sticky="ew", ipady=6, padx=2)
    return var

class ContactApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact Manager")
        self.geometry("1050x680")
        self.minsize(900, 560)
        self.configure(bg=BG)
        self.contacts = load_contacts()
        self.sort_col = "name"
        self.sort_rev = False
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG, pady=14)
        hdr.pack(fill="x", padx=28)
        tk.Label(hdr, text="CONTACT", bg=BG, fg=ACCENT, font=FONT_TITLE).pack(side="left")
        tk.Label(hdr, text=" MANAGER", bg=BG, fg=TEXT, font=FONT_TITLE).pack(side="left")
        self.count_lbl = tk.Label(hdr, text=f"  — {len(self.contacts)} saved",
            bg=BG, fg=SUBTEXT, font=FONT_SMALL)
        self.count_lbl.pack(side="left", pady=6)

        # toolbar
        toolbar = tk.Frame(self, bg=BG)
        toolbar.pack(fill="x", padx=28, pady=(0,4))
        styled_button(toolbar, "Export CSV", self._export_csv, color="#2d6a4f", width=12).pack(side="left", padx=(0,6))
        styled_button(toolbar, "Import CSV", self._import_csv, color="#1b4332", width=12).pack(side="left", padx=(0,6))
        styled_button(toolbar, "Print List", self._print_contacts, color="#333355", width=12).pack(side="left", padx=(0,6))

        # sort buttons
        tk.Label(toolbar, text="  Sort:", bg=BG, fg=SUBTEXT, font=FONT_LABEL).pack(side="left")
        for label, col in [("Name", "name"), ("Phone", "phone"), ("Email", "email")]:
            styled_button(toolbar, label, lambda c=col: self._sort_by(c),
                color="#2a2a3a", width=8).pack(side="left", padx=2)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=28)
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=16)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,16))
        left.rowconfigure(1, weight=1)

        search_frame = tk.Frame(left, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        search_frame.pack(fill="x", pady=(0,10))
        tk.Label(search_frame, text="Search:", bg=CARD, fg=ACCENT, font=FONT_BODY).pack(side="left", padx=8)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_list())
        tk.Entry(search_frame, textvariable=self.search_var, bg=CARD, fg=TEXT,
            font=FONT_BODY, relief="flat", bd=0, insertbackground=ACCENT).pack(
            side="left", fill="x", expand=True, ipady=8, padx=4)
        styled_button(search_frame, "Clear", lambda: self.search_var.set(""),
            color=BORDER, width=6).pack(side="right", padx=4)

        tree_frame = tk.Frame(left, bg=BG)
        tree_frame.pack(fill="both", expand=True)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Contacts.Treeview", background=CARD, foreground=TEXT,
            fieldbackground=CARD, rowheight=34, font=FONT_BODY, borderwidth=0)
        style.configure("Contacts.Treeview.Heading", background=BG, foreground=ACCENT,
            font=FONT_LABEL, relief="flat")
        style.map("Contacts.Treeview", background=[("selected", ACCENT)], foreground=[("selected", TEXT)])

        cols = ("name", "phone", "email", "address")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
            style="Contacts.Treeview", selectmode="browse")
        for col, head, w in [("name","NAME",180),("phone","PHONE",130),("email","EMAIL",190),("address","ADDRESS",160)]:
            self.tree.heading(col, text=head, command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w, anchor="w")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._load_for_edit())

        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill="x", pady=(10,0))
        styled_button(btn_row, "+ ADD NEW", self._clear_form, color=ACCENT).pack(side="left")
        styled_button(btn_row, "EDIT", self._load_for_edit, color="#3a7bd5").pack(side="left", padx=8)
        styled_button(btn_row, "DELETE", self._delete_contact, color=DANGER).pack(side="left")

    def _build_right(self, parent):
        self.right = tk.Frame(parent, bg=CARD, padx=20, pady=18,
            highlightbackground=BORDER, highlightthickness=1)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.columnconfigure(0, weight=1)
        self.form_title = tk.Label(self.right, text="NEW CONTACT", bg=CARD, fg=ACCENT, font=FONT_HEAD)
        self.form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))
        self.v_name    = labeled_entry(self.right, "FULL NAME", 1)
        self.v_phone   = labeled_entry(self.right, "PHONE",     3)
        self.v_email   = labeled_entry(self.right, "EMAIL",     5)
        self.v_address = labeled_entry(self.right, "ADDRESS",   7)
        self.editing_id = None
        tk.Frame(self.right, bg=BORDER, height=1).grid(row=9, column=0, columnspan=2, sticky="ew", pady=16)
        styled_button(self.right, "SAVE", self._save_contact, color=SUCCESS, width=18).grid(row=10, column=0, sticky="ew")
        self.status_lbl = tk.Label(self.right, text="", bg=CARD, fg=SUBTEXT, font=FONT_SMALL, wraplength=220)
        self.status_lbl.grid(row=11, column=0, pady=(8,0))

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _save_contact(self):
        name    = self.v_name.get().strip()
        phone   = self.v_phone.get().strip()
        email   = self.v_email.get().strip()
        address = self.v_address.get().strip()
        if not name:
            self._status("Name is required.", ACCENT2); return
        if not phone:
            self._status("Phone is required.", ACCENT2); return
        if not validate_phone(phone):
            self._status("Invalid phone number.", ACCENT2); return
        if email and not validate_email(email):
            self._status("Invalid email address.", ACCENT2); return
        entry = {"name": name, "phone": phone, "email": email, "address": address}
        if self.editing_id is not None:
            self.contacts[self.editing_id] = entry
            self._status(f"'{name}' updated.", SUCCESS)
        else:
            if any(c["phone"] == phone for c in self.contacts):
                if not messagebox.askyesno("Duplicate Phone", f"Phone {phone} already exists. Save anyway?"):
                    return
            self.contacts.append(entry)
            self._status(f"'{name}' added.", SUCCESS)
        save_contacts(self.contacts)
        self._refresh_list()
        self._clear_form()

    def _delete_contact(self):
        sel = self.tree.selection()
        if not sel:
            self._status("Select a contact first.", SUBTEXT); return
        idx = self._tree_index(sel[0])
        name = self.contacts[idx]["name"]
        if messagebox.askyesno("Delete", f"Delete '{name}'?", icon="warning"):
            self.contacts.pop(idx)
            save_contacts(self.contacts)
            self._refresh_list()
            self._clear_form()
            self._status(f"'{name}' deleted.", DANGER)

    def _load_for_edit(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self._tree_index(sel[0])
        c = self.contacts[idx]
        self.editing_id = idx
        self.v_name.set(c["name"])
        self.v_phone.set(c["phone"])
        self.v_email.set(c.get("email", ""))
        self.v_address.set(c.get("address", ""))
        self.form_title.config(text=f"EDIT — {c['name'].upper()}")
        self._status("", SUBTEXT)

    def _clear_form(self):
        self.editing_id = None
        for v in (self.v_name, self.v_phone, self.v_email, self.v_address):
            v.set("")
        self.form_title.config(text="NEW CONTACT")
        self._status("", SUBTEXT)

    def _tree_index(self, item):
        # map tree item back to contacts index via stored iid
        return int(self.tree.item(item, "tags")[0])

    # ── Sort ──────────────────────────────────────────────────────────────────

    def _sort_by(self, col):
        if self.sort_col == col:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col = col
            self.sort_rev = False
        self.contacts.sort(key=lambda c: c.get(col, "").lower(), reverse=self.sort_rev)
        save_contacts(self.contacts)
        self._refresh_list()
        arrow = " ▲" if not self.sort_rev else " ▼"
        for c, h, _ in [("name","NAME",0),("phone","PHONE",0),("email","EMAIL",0),("address","ADDRESS",0)]:
            self.tree.heading(c, text=h + (arrow if c == col else ""))

    # ── Export CSV ────────────────────────────────────────────────────────────

    def _export_csv(self):
        if not self.contacts:
            messagebox.showinfo("Export", "No contacts to export!"); return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV files","*.csv"),("All files","*.*")],
            initialfile="contacts.csv")
        if not path: return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name","phone","email","address"])
            writer.writeheader()
            writer.writerows(self.contacts)
        messagebox.showinfo("Export", f"Exported {len(self.contacts)} contacts to:\n{path}")

    # ── Import CSV ────────────────────────────────────────────────────────────

    def _import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path: return
        imported = 0
        skipped  = 0
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name  = row.get("name","").strip()
                    phone = row.get("phone","").strip()
                    if not name or not phone:
                        skipped += 1; continue
                    if any(c["phone"] == phone for c in self.contacts):
                        skipped += 1; continue
                    self.contacts.append({
                        "name": name, "phone": phone,
                        "email": row.get("email","").strip(),
                        "address": row.get("address","").strip()
                    })
                    imported += 1
            save_contacts(self.contacts)
            self._refresh_list()
            messagebox.showinfo("Import", f"Imported: {imported}  |  Skipped: {skipped}")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    # ── Print ─────────────────────────────────────────────────────────────────

    def _print_contacts(self):
        if not self.contacts:
            messagebox.showinfo("Print", "No contacts to print!"); return

        win = tk.Toplevel(self)
        win.title("Print Preview")
        win.geometry("700x520")
        win.configure(bg=BG)

        tk.Label(win, text="CONTACT LIST — PRINT PREVIEW", bg=BG, fg=ACCENT,
            font=FONT_HEAD).pack(pady=(16,8))
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=20)

        frame = tk.Frame(win, bg=CARD)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        text = tk.Text(frame, bg=CARD, fg=TEXT, font=("Courier New", 10),
            relief="flat", wrap="none", padx=12, pady=8)
        sb = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=sb.set)
        text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        header = f"{'NAME':<25} {'PHONE':<16} {'EMAIL':<28} {'ADDRESS'}"
        text.insert("end", header + "\n")
        text.insert("end", "-" * 85 + "\n")
        for c in self.contacts:
            line = f"{c['name']:<25} {c['phone']:<16} {c.get('email','-'):<28} {c.get('address','-')}"
            text.insert("end", line + "\n")
        text.config(state="disabled")

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=10)

        def save_txt():
            path = filedialog.asksaveasfilename(defaultextension=".txt",
                filetypes=[("Text files","*.txt")], initialfile="contacts_print.txt")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text.get("1.0","end"))
                messagebox.showinfo("Saved", f"Saved to {path}")

        styled_button(btn_row, "Save as TXT", save_txt, color="#333355", width=14).pack(side="left", padx=8)
        styled_button(btn_row, "Close", win.destroy, color=DANGER, width=10).pack(side="left")

    # ── Refresh ───────────────────────────────────────────────────────────────

    def _refresh_list(self):
        query = self.search_var.get().lower().strip() if hasattr(self, "search_var") else ""
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for i, c in enumerate(self.contacts):
            if query and query not in c["name"].lower() and query not in c["phone"] \
                     and query not in c.get("email","").lower():
                continue
            self.tree.insert("", "end", values=(
                c["name"], c["phone"], c.get("email","-"), c.get("address","-")),
                tags=(str(i),))
            shown += 1
        self.count_lbl.config(text=f"  — {shown} shown / {len(self.contacts)} total")

    def _on_select(self, _event):
        sel = self.tree.selection()
        if sel:
            idx = self._tree_index(sel[0])
            c = self.contacts[idx]
            self._status(f"Address: {c.get('address','-')}", SUBTEXT)

    def _status(self, msg, color=SUBTEXT):
        self.status_lbl.config(text=msg, fg=color)

if __name__ == "__main__":
    app = ContactApp()
    app.mainloop()