"""
Advanced Calculator — Python + Tkinter
"""

import tkinter as tk
import math

# ═══════════════════════════════════════════════════
#  PALETTE
# ═══════════════════════════════════════════════════
BG          = "#0a0a0f"
DISPLAY_BG  = "#060608"
DISPLAY_FG  = "#00ff99"
EXPR_FG     = "#446655"
HIST_BG     = "#0d0d15"
HIST_FG     = "#3a5a4a"

BTN_NUM_BG  = "#141420"
BTN_NUM_FG  = "#c8fce8"
BTN_NUM_HL  = "#1e1e32"

BTN_OP_BG   = "#0e1f18"
BTN_OP_FG   = "#00ff99"
BTN_OP_HL   = "#173028"

BTN_EQ_BG   = "#003322"
BTN_EQ_FG   = "#00ff99"
BTN_EQ_HL   = "#00ff99"
BTN_EQ_TFG  = "#000000"

BTN_CLR_BG  = "#200a0a"
BTN_CLR_FG  = "#ff4455"
BTN_CLR_HL  = "#331010"

BTN_SP_BG   = "#0a1020"
BTN_SP_FG   = "#5588ff"
BTN_SP_HL   = "#0f1830"

BORDER      = "#1a2a20"
TEXT_MUTED  = "#334433"

OPERATIONS = {
    "+":  lambda a, b: a + b,
    "-":  lambda a, b: a - b,
    "×":  lambda a, b: a * b,
    "÷":  lambda a, b: a / b,
    "%":  lambda a, b: a % b,
    "**": lambda a, b: a ** b,
}

def fmt_num(n):
    if n is None:
        return "Error"
    s = str(n)
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s

def safe_calc(a_str, op, b_str):
    try:
        a = float(a_str)
        b = float(b_str)
    except ValueError:
        return None, "Invalid number"
    if op in ("÷", "%") and b == 0:
        return None, "Cannot divide by zero"
    try:
        result = OPERATIONS[op](a, b)
        if isinstance(result, float) and result == int(result):
            result = int(result)
        return result, None
    except Exception as e:
        return None, str(e)


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CALCULATOR")
        self.geometry("420x680")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._num1    = ""
        self._op      = ""
        self._num2    = ""
        self._phase   = "num1"
        self._history = []
        self._just_eq = False

        self._build()
        self._bind_keys()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=BG, pady=6)
        hdr.pack(fill="x", padx=16)
        tk.Label(hdr, text="◈  CALC  ◈", bg=BG,
                 fg=DISPLAY_FG, font=("Courier New", 11, "bold")).pack(side="left")
        tk.Label(hdr, text="[PY-CALC v1.0]", bg=BG,
                 fg=TEXT_MUTED, font=("Courier New", 8)).pack(side="right")

        # Display
        disp_outer = tk.Frame(self, bg=BORDER, padx=2, pady=2)
        disp_outer.pack(fill="x", padx=16, pady=(0, 8))
        disp_inner = tk.Frame(disp_outer, bg=DISPLAY_BG, pady=10)
        disp_inner.pack(fill="x")

        self._expr_lbl = tk.Label(disp_inner, text="", bg=DISPLAY_BG, fg=EXPR_FG,
                                   font=("Courier New", 11), anchor="e", padx=14)
        self._expr_lbl.pack(fill="x")

        self._main_lbl = tk.Label(disp_inner, text="0", bg=DISPLAY_BG, fg=DISPLAY_FG,
                                   font=("Courier New", 38, "bold"), anchor="e", padx=14)
        self._main_lbl.pack(fill="x")

        self._status_lbl = tk.Label(disp_inner, text="Enter a number", bg=DISPLAY_BG,
                                     fg=TEXT_MUTED, font=("Courier New", 8), anchor="w", padx=14)
        self._status_lbl.pack(fill="x")

        # History
        hist_outer = tk.Frame(self, bg=BORDER, padx=2, pady=2)
        hist_outer.pack(fill="x", padx=16, pady=(0, 8))
        hist_inner = tk.Frame(hist_outer, bg=HIST_BG, pady=6)
        hist_inner.pack(fill="x")
        tk.Label(hist_inner, text="  HISTORY", bg=HIST_BG,
                 fg=TEXT_MUTED, font=("Courier New", 7, "bold"), anchor="w").pack(fill="x")
        self._hist_lbl = tk.Label(hist_inner, text="—", bg=HIST_BG, fg=HIST_FG,
                                   font=("Courier New", 9), anchor="e", padx=10, justify="right")
        self._hist_lbl.pack(fill="x")

        # Button grid
        pad = tk.Frame(self, bg=BG)
        pad.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        layout = [
            [("C","clr"),  ("±","sp"),  ("√","sp"),  ("÷","op")],
            [("7","num"),  ("8","num"), ("9","num"),  ("×","op")],
            [("4","num"),  ("5","num"), ("6","num"),  ("-","op")],
            [("1","num"),  ("2","num"), ("3","num"),  ("+","op")],
            [("**","sp"),  ("%","sp"),  ("0","num"),  ("=","eq")],
        ]

        style_map = {
            "num": (BTN_NUM_BG, BTN_NUM_FG, BTN_NUM_HL),
            "op":  (BTN_OP_BG,  BTN_OP_FG,  BTN_OP_HL),
            "eq":  (BTN_EQ_BG,  BTN_EQ_FG,  BTN_EQ_HL),
            "clr": (BTN_CLR_BG, BTN_CLR_FG, BTN_CLR_HL),
            "sp":  (BTN_SP_BG,  BTN_SP_FG,  BTN_SP_HL),
        }

        for r, row in enumerate(layout):
            for c, (lbl, style) in enumerate(row):
                bg, fg, hl = style_map[style]
                self._make_btn(pad, lbl, bg, fg, hl, r, c, style == "eq")

        for i in range(4):
            pad.columnconfigure(i, weight=1, uniform="col")
        for i in range(5):
            pad.rowconfigure(i, weight=1, uniform="row")

    def _make_btn(self, parent, text, bg, fg, hl, row, col, eq_style=False):
        f = ("Courier New", 16, "bold") if len(text) == 1 else ("Courier New", 12, "bold")

        btn = tk.Button(
            parent, text=text, bg=bg, fg=fg,
            font=f, cursor="hand2",
            relief="flat", bd=0, activebackground=hl,
            activeforeground=BTN_EQ_TFG if eq_style else fg,
            command=lambda t=text: self._handle(t)
        )
        btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

    def _bind_keys(self):
        # Use KeyPress- prefix for ALL keys to avoid mouse button conflicts
        numkeys = "0123456789"
        for k in numkeys:
            self.bind(f"<KeyPress-{k}>", lambda e, a=k: self._handle(a))
        self.bind("<KeyPress-period>",   lambda e: self._handle("."))
        self.bind("<KeyPress-Return>",   lambda e: self._handle("="))
        self.bind("<KP_Enter>",          lambda e: self._handle("="))
        self.bind("<KeyPress-BackSpace>", lambda e: self._handle("⌫"))
        self.bind("<KeyPress-Escape>",   lambda e: self._handle("C"))
        self.bind("<KeyPress-asterisk>", lambda e: self._handle("×"))
        self.bind("<KeyPress-slash>",    lambda e: self._handle("÷"))
        self.bind("<KeyPress-plus>",     lambda e: self._handle("+"))
        self.bind("<KeyPress-minus>",    lambda e: self._handle("-"))
        self.bind("<KeyPress-percent>",  lambda e: self._handle("%"))

    def _handle(self, key):
        if key == "C":
            self._reset(); return
        if key == "⌫":
            self._backspace(); return
        if key == "±":
            self._negate(); return
        if key == "√":
            self._sqrt(); return

        is_digit = key in "0123456789."
        is_op    = key in OPERATIONS

        if is_digit:
            if self._just_eq:
                # After = : fresh new number
                self._num1 = key
                self._num2 = ""
                self._op = ""
                self._phase = "num1"
                self._just_eq = False
                self._set_expr("")
                self._update_display(self._num1)
                self._set_status("Enter a number")
                return
            if self._phase == "num1":
                if key == "." and "." in self._num1:
                    return
                self._num1 += key
                self._update_display(self._num1)
            elif self._phase == "result":
                self._num1 = key
                self._phase = "num1"
                self._update_display(self._num1)
            elif self._phase in ("op", "num2"):
                self._phase = "num2"
                if key == "." and "." in self._num2:
                    return
                self._num2 += key
                self._update_display(self._num2)
            self._just_eq = False

        elif is_op:
            if self._phase == "num2" and self._num2:
                self._calculate()
            if self._num1:
                self._op    = key
                self._phase = "op"
                self._set_expr(f"{self._num1} {key}")
                self._update_display(self._num1)
                self._set_status("Enter second number")
            self._just_eq = False

        elif key == "=":
            if self._phase == "num2" and self._num2:
                self._calculate()
            else:
                self._set_status("Need two numbers & operator")

    def _calculate(self):
        result, err = safe_calc(self._num1, self._op, self._num2)
        expr_str = f"{self._num1} {self._op} {self._num2}"

        if err:
            self._set_status(f"⚠ {err}")
            self._set_expr(expr_str)
            self._update_display("Error")
            self._reset()
            return

        res_str = fmt_num(result)
        full = f"{expr_str} = {res_str}"
        self._set_expr(full)
        self._update_display(res_str)
        self._set_status("✓ Result")

        self._history.insert(0, full)
        if len(self._history) > 8:
            self._history.pop()
        self._refresh_history()

        self._num1    = res_str
        self._num2    = ""
        self._op      = ""
        self._phase   = "result"
        self._just_eq = True

    def _reset(self):
        self._num1    = ""
        self._num2    = ""
        self._op      = ""
        self._phase   = "num1"
        self._just_eq = False
        self._update_display("0")
        self._set_expr("")
        self._set_status("Enter a number")

    def _backspace(self):
        if self._phase == "num1" and self._num1:
            self._num1 = self._num1[:-1]
            self._update_display(self._num1 or "0")
        elif self._phase == "num2" and self._num2:
            self._num2 = self._num2[:-1]
            self._update_display(self._num2 or "0")

    def _negate(self):
        target = "num1" if self._phase in ("num1","result") else "num2"
        src = self._num1 if target == "num1" else self._num2
        if not src:
            return
        try:
            v = fmt_num(-float(src))
            if target == "num1":
                self._num1 = v
            else:
                self._num2 = v
            self._update_display(v)
        except ValueError:
            pass

    def _sqrt(self):
        src = self._num2 if self._phase == "num2" else self._num1
        if not src:
            return
        try:
            v = float(src)
            if v < 0:
                self._set_status("⚠ Cannot √ negative"); return
            res = fmt_num(math.sqrt(v))
            full = f"√({src}) = {res}"
            self._set_expr(full)
            self._update_display(res)
            self._history.insert(0, full)
            if len(self._history) > 8:
                self._history.pop()
            self._refresh_history()
            self._num1    = res
            self._num2    = ""
            self._op      = ""
            self._phase   = "result"
            self._just_eq = True
        except ValueError:
            self._set_status("⚠ Invalid input for √")

    def _update_display(self, text):
        if not text:
            text = "0"
        length = len(str(text))
        sz = 20 if length > 12 else 26 if length > 8 else 38
        self._main_lbl.config(text=str(text), font=("Courier New", sz, "bold"))

    def _set_expr(self, text):
        self._expr_lbl.config(text=text)

    def _set_status(self, text):
        self._status_lbl.config(text=text)

    def _refresh_history(self):
        lines = self._history[:5]
        self._hist_lbl.config(text="\n".join(lines) if lines else "—")


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
