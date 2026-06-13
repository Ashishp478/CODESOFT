import tkinter as tk
import random
import sys

# ══════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════
CHOICES  = ["Rock", "Paper", "Scissors"]
EMOJI    = {"Rock": "🪨", "Paper": "📄", "Scissors": "✂️"}
BEATS    = {"Rock": "Scissors", "Scissors": "Paper", "Paper": "Rock"}

# ── Cross-platform font helper ─────────────────────────
def _font(size, bold=False):
    weight = "bold" if bold else "normal"
    if sys.platform == "win32":
        return ("Arial Rounded MT Bold", size, weight)
    elif sys.platform == "darwin":
        return ("Helvetica Neue", size, weight)
    else:
        return ("DejaVu Sans", size, weight)

def _emoji_font(size):
    if sys.platform == "win32":
        return ("Segoe UI Emoji", size)
    elif sys.platform == "darwin":
        return ("Apple Color Emoji", size)
    else:
        return ("Noto Color Emoji", size)

# ── Dark Neon Palette ──────────────────────────────────
BG           = "#0f0c29"
CARD         = "#1a1740"
CARD2        = "#231f56"
TEXT         = "#ffffff"
MUTED        = "#a09dc8"
P1_CLR       = "#7B61FF"
P1_BG        = "#1e1845"
P2_CLR       = "#FF6B9D"
P2_BG        = "#3d1028"
WIN_CLR      = "#06D6A0"
WIN_BG       = "#083d2c"
LOSE_CLR     = "#EF476F"
LOSE_BG      = "#3d0818"
TIE_CLR      = "#FFB703"
TIE_BG       = "#3d2c02"
ROCK_CLR     = "#FF6B6B"
PAPER_CLR    = "#4ECDC4"
SCISSORS_CLR = "#FFE66D"

# ── Fonts ──────────────────────────────────────────────
F_TITLE  = _font(22, bold=True)
F_HEAD   = _font(15, bold=True)
F_SCORE  = _font(42, bold=True)
F_MED    = _font(13, bold=True)
F_BODY   = _font(11)
F_SMALL  = _font(10)
F_BTN    = _font(13, bold=True)
F_EMOJI  = _emoji_font(44)
F_RESULT = _font(18, bold=True)
F_TIMER  = _font(20, bold=True)
F_TINY   = _font(9)
F_STREAK = _font(14, bold=True)
F_WINRT  = _font(12, bold=True)


# ══════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rock Paper Scissors")
        self.geometry("680x700")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._show_menu()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _show_menu(self):
        self._clear()
        # Title with emojis
        tk.Label(self, text="🪨  📄  ✂️",
                 bg=BG, fg=TEXT, font=_emoji_font(36)).pack(pady=(30, 4))
        tk.Label(self, text="ROCK  PAPER  SCISSORS",
                 bg=BG, fg=TEXT, font=F_TITLE).pack()
        tk.Label(self, text="Choose your battle mode",
                 bg=BG, fg=MUTED, font=F_BODY).pack(pady=(4, 36))

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack()
        self._mode_card(btn_frame, "🤖", "vs Computer",
                        "1 Player\nChallenge the CPU",
                        lambda: self._start_game("cpu"), 0)
        self._mode_card(btn_frame, "🆚", "2 Players",
                        "Same screen\nSecret picks",
                        lambda: self._start_game("2p"), 1)

    def _mode_card(self, parent, icon, title, sub, cmd, col):
        outer = tk.Frame(parent, bg=P1_CLR, padx=2, pady=2)
        outer.grid(row=0, column=col, padx=16)
        inner = tk.Frame(outer, bg=CARD, padx=36, pady=20, cursor="hand2")
        inner.pack()
        for w in [outer, inner]:
            w.bind("<Button-1>", lambda e, c=cmd: c())

        # Big icon emoji
        lbl_icon = tk.Label(inner, text=icon, bg=CARD, fg=TEXT, font=_emoji_font(42))
        lbl_icon.pack()
        lbl_icon.bind("<Button-1>", lambda e, c=cmd: c())

        lbl_t = tk.Label(inner, text=title, bg=CARD, fg=TEXT, font=F_HEAD)
        lbl_t.pack(pady=(6, 2))
        lbl_t.bind("<Button-1>", lambda e, c=cmd: c())

        lbl_s = tk.Label(inner, text=sub, bg=CARD, fg=MUTED,
                         font=F_SMALL, justify="center")
        lbl_s.pack()
        lbl_s.bind("<Button-1>", lambda e, c=cmd: c())

    def _start_game(self, mode):
        self._clear()
        if mode == "cpu":
            CPUGame(self)
        else:
            TwoPlayerGame(self)


# ══════════════════════════════════════════════════════
#  SHARED BASE
# ══════════════════════════════════════════════════════
class BaseGame:
    def __init__(self, app):
        self.app      = app
        self.scores   = [0, 0, 0]
        self.history  = []
        self._anim_id = None

    def _cancel_anim(self):
        if self._anim_id is not None:
            try:
                self.app.after_cancel(self._anim_id)
            except Exception:
                pass
            self._anim_id = None

    def _back_btn(self, parent):
        tk.Button(parent, text="← Back", font=F_SMALL,
                  bg=CARD, fg=MUTED, relief="flat", bd=0,
                  cursor="hand2", padx=10, pady=4,
                  command=self.app._show_menu).pack(side="right", padx=12)

    def _build_scoreboard(self, parent, n1, n2, c1=P1_CLR, c2=P2_CLR,
                          icon1="👤", icon2="👤"):
        sb = tk.Frame(parent, bg=CARD, pady=0)
        sb.pack(fill="x", padx=18, pady=(6, 0))
        hdr = tk.Frame(sb, bg=P1_CLR, pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚡  S C O R E B O A R D  ⚡",
                 bg=P1_CLR, fg=TEXT, font=F_SMALL).pack()

        body = tk.Frame(sb, bg=CARD, pady=10)
        body.pack(fill="x")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.columnconfigure(2, weight=1)

        f1 = tk.Frame(body, bg=CARD)
        f1.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(f1, text=icon1, bg=CARD, fg=c1, font=_emoji_font(22)).pack()
        tk.Label(f1, text=n1.upper(), bg=CARD, fg=MUTED, font=F_TINY).pack()
        self.lbl_s1 = tk.Label(f1, text="0", bg=CARD, fg=c1, font=F_SCORE)
        self.lbl_s1.pack()

        fm = tk.Frame(body, bg=CARD)
        fm.grid(row=0, column=1, padx=14)
        tk.Label(fm, text="🤝", bg=CARD, fg=TIE_CLR, font=_emoji_font(18)).pack()
        self.lbl_st = tk.Label(fm, text="0", bg=CARD, fg=TIE_CLR,
                               font=_font(22, bold=True))
        self.lbl_st.pack()
        tk.Label(fm, text="TIES", bg=CARD, fg=MUTED, font=F_TINY).pack()

        f2 = tk.Frame(body, bg=CARD)
        f2.grid(row=0, column=2, sticky="ew", padx=10)
        tk.Label(f2, text=icon2, bg=CARD, fg=c2, font=_emoji_font(22)).pack()
        tk.Label(f2, text=n2.upper(), bg=CARD, fg=MUTED, font=F_TINY).pack()
        self.lbl_s2 = tk.Label(f2, text="0", bg=CARD, fg=c2, font=F_SCORE)
        self.lbl_s2.pack()

    def _update_scores(self):
        self.lbl_s1.config(text=str(self.scores[0]))
        self.lbl_s2.config(text=str(self.scores[1]))
        self.lbl_st.config(text=str(self.scores[2]))

    def _history_widget(self, parent, two_player=False, n1="P1", n2="P2"):
        f = tk.Frame(parent, bg=CARD, pady=6, padx=10)
        f.pack(fill="x", padx=18, pady=(6, 0))
        tk.Label(f, text="📜  RECENT ROUNDS", bg=CARD, fg=MUTED,
                 font=F_TINY).pack(anchor="w")
        self.hist_frame = tk.Frame(f, bg=CARD)
        self.hist_frame.pack(fill="x")
        self._two_player = two_player
        self._hist_names = (n1, n2)

    def _refresh_history(self):
        for w in self.hist_frame.winfo_children():
            w.destroy()
        if not self.history:
            tk.Label(self.hist_frame, text="No rounds yet",
                     bg=CARD, fg=MUTED, font=F_TINY).pack(anchor="w")
            return
        for h in self.history[:6]:
            row = tk.Frame(self.hist_frame, bg=CARD)
            row.pack(fill="x", pady=1)
            if self._two_player:
                txt = f"{EMOJI[h['p1']]}  vs  {EMOJI[h['p2']]}"
                res = h["result"]
                if   res == "tie": badge, bc = "Tie",  TIE_CLR
                elif res == "p1":  badge, bc = f"{self._hist_names[0]} won", P1_CLR
                else:              badge, bc = f"{self._hist_names[1]} won", P2_CLR
            else:
                txt = f"{EMOJI[h['you']]}  vs  {EMOJI[h['cpu']]}"
                res = h["result"]
                if   res == "win":  badge, bc = "Win",  WIN_CLR
                elif res == "lose": badge, bc = "Lose", LOSE_CLR
                else:               badge, bc = "Tie",  TIE_CLR
            tk.Label(row, text=txt, bg=CARD, fg=TEXT, font=F_TINY).pack(side="left")
            tk.Label(row, text=f"  {badge}", bg=CARD, fg=bc,
                     font=(_font(9)[0], 9, "bold")).pack(side="left")


# ══════════════════════════════════════════════════════
#  1 PLAYER vs CPU
# ══════════════════════════════════════════════════════
class CPUGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.streak        = 0
        self.best_streak   = 0
        self.total_games   = 0
        self.total_wins    = 0
        self.cpu_counts    = {"Rock": 0, "Paper": 0, "Scissors": 0}
        self.timer_on      = False
        self.timer_secs    = 10
        self._timer_id     = None
        self._cd           = 0
        self._btns         = {}
        self._btns_enabled = True
        self._build()

    def _build(self):
        # Top bar
        topbar = tk.Frame(self.app, bg=BG, pady=8)
        topbar.pack(fill="x")
        tk.Label(topbar, text="🤖  vs Computer", bg=BG, fg=TEXT,
                 font=F_HEAD).pack(side="left", padx=14)
        self._back_btn(topbar)

        # Scoreboard — Player1=👤, CPU=🤖
        self._build_scoreboard(self.app, "You", "CPU",
                               P1_CLR, LOSE_CLR,
                               icon1="👤", icon2="🤖")

        # Timer / streak bar
        tbar = tk.Frame(self.app, bg=CARD2, pady=6)
        tbar.pack(fill="x", padx=18, pady=(4, 0))

        tk.Label(tbar, text="⏱ Timer:", bg=CARD2, fg=MUTED,
                 font=F_TINY).pack(side="left", padx=(10, 4))
        self.timer_lbl = tk.Label(tbar, text="10s", bg=CARD2,
                                   fg=WIN_CLR, font=F_TIMER, width=4)
        self.timer_lbl.pack(side="left")
        self.timer_btn = tk.Button(tbar, text="START", font=F_SMALL,
                                    bg=WIN_BG, fg=WIN_CLR, relief="flat", bd=0,
                                    cursor="hand2", padx=10, pady=3,
                                    command=self._toggle_timer)
        self.timer_btn.pack(side="left", padx=6)

        tk.Label(tbar, text="🔥 Streak:", bg=CARD2, fg=MUTED,
                 font=F_TINY).pack(side="left", padx=(14, 4))
        self.streak_lbl = tk.Label(tbar, text="0", bg=CARD2,
                                    fg=TEXT, font=F_STREAK)
        self.streak_lbl.pack(side="left")

        tk.Label(tbar, text="📊 Win%:", bg=CARD2, fg=MUTED,
                 font=F_TINY).pack(side="left", padx=(14, 4))
        self.winrate_lbl = tk.Label(tbar, text="—", bg=CARD2,
                                     fg=TEXT, font=F_WINRT)
        self.winrate_lbl.pack(side="left")

        tk.Button(tbar, text="🔄 Reset", font=F_TINY,
                  bg=LOSE_BG, fg=LOSE_CLR, relief="flat", bd=0,
                  cursor="hand2", padx=8, pady=3,
                  command=self._reset).pack(side="right", padx=10)

        # Arena
        arena = tk.Frame(self.app, bg=BG, pady=8)
        arena.pack(fill="x", padx=18)
        arena.columnconfigure(0, weight=1)
        arena.columnconfigure(1, weight=0)
        arena.columnconfigure(2, weight=1)

        # You card
        you_f  = tk.Frame(arena, bg=P1_CLR, padx=2, pady=2)
        you_f.grid(row=0, column=0, sticky="nsew")
        you_in = tk.Frame(you_f, bg=P1_BG, pady=14)
        you_in.pack(fill="both", expand=True)
        tk.Label(you_in, text="👤  YOU", bg=P1_BG, fg=P1_CLR, font=F_SMALL).pack()
        self.you_emoji  = tk.Label(you_in, text="🤔", bg=P1_BG, fg=TEXT, font=F_EMOJI)
        self.you_emoji.pack(pady=4)
        self.you_choice = tk.Label(you_in, text="—", bg=P1_BG, fg=MUTED, font=F_SMALL)
        self.you_choice.pack()

        # VS
        vs_f = tk.Frame(arena, bg=BG, width=60)
        vs_f.grid(row=0, column=1, padx=8)
        self.vs_lbl = tk.Label(vs_f, text="VS", bg=CARD2, fg=MUTED,
                                font=F_MED, width=4, pady=10)
        self.vs_lbl.pack()

        # CPU card
        cpu_f  = tk.Frame(arena, bg=LOSE_CLR, padx=2, pady=2)
        cpu_f.grid(row=0, column=2, sticky="nsew")
        cpu_in = tk.Frame(cpu_f, bg=LOSE_BG, pady=14)
        cpu_in.pack(fill="both", expand=True)
        tk.Label(cpu_in, text="🤖  CPU", bg=LOSE_BG, fg=LOSE_CLR, font=F_SMALL).pack()
        self.cpu_emoji  = tk.Label(cpu_in, text="🤖", bg=LOSE_BG, fg=TEXT, font=F_EMOJI)
        self.cpu_emoji.pack(pady=4)
        self.cpu_choice = tk.Label(cpu_in, text="—", bg=LOSE_BG, fg=MUTED, font=F_SMALL)
        self.cpu_choice.pack()

        # Result label
        self.result_lbl = tk.Label(self.app, text="👇 Pick your weapon!",
                                    bg=BG, fg=MUTED, font=F_RESULT)
        self.result_lbl.pack(pady=(6, 8))

        # Choice buttons
        btn_row = tk.Frame(self.app, bg=BG)
        btn_row.pack()
        colors = {"Rock": ROCK_CLR, "Paper": PAPER_CLR, "Scissors": SCISSORS_CLR}
        bgs    = {"Rock": "#3d1a1a", "Paper": "#0d2d2c", "Scissors": "#3d3200"}

        for ch in CHOICES:
            col = colors[ch]; bg = bgs[ch]
            outer = tk.Frame(btn_row, bg=col, padx=2, pady=2)
            outer.pack(side="left", padx=10)
            inner = tk.Frame(outer, bg=bg, padx=22, pady=14)
            inner.pack()
            el = tk.Label(inner, text=EMOJI[ch], bg=bg, fg=TEXT, font=F_EMOJI)
            el.pack()
            nl = tk.Label(inner, text=ch.upper(), bg=bg, fg=col,
                          font=_font(11, bold=True))
            nl.pack(pady=(4, 0))
            widgets = [outer, inner, el, nl]
            for w in widgets:
                w.bind("<Button-1>", lambda e, c=ch: self._play(c))
                w.configure(cursor="hand2")
            self._btns[ch] = widgets

        self.tip_lbl = tk.Label(self.app,
            text="🧠 Play a few rounds to unlock CPU pattern!",
            bg=BG, fg=MUTED, font=F_TINY)
        self.tip_lbl.pack(pady=(6, 2))

        self._history_widget(self.app)
        self._refresh_history()

    # ── Gameplay ────────────────────────────────────
    def _play(self, choice):
        if not self._btns_enabled:
            return
        self._set_btns_enabled(False)
        self._stop_timer()

        cpu    = random.choice(CHOICES)
        self.cpu_counts[cpu] += 1
        self.total_games += 1

        result = ("tie"  if choice == cpu
                  else "win" if BEATS[choice] == cpu
                  else "lose")

        if result == "win":
            self.scores[0] += 1; self.total_wins += 1
            self.streak = self.streak + 1 if self.streak > 0 else 1
        elif result == "lose":
            self.scores[1] += 1
            self.streak = self.streak - 1 if self.streak < 0 else -1
        else:
            self.scores[2] += 1; self.streak = 0

        if abs(self.streak) > self.best_streak:
            self.best_streak = abs(self.streak)

        self.history.insert(0, {"you": choice, "cpu": cpu, "result": result})
        if len(self.history) > 8:
            self.history.pop()

        self.vs_lbl.config(text="💥")
        step  = [0]
        spins = list(EMOJI.values())

        def spin():
            if step[0] < 9:
                self.you_emoji.config(text=spins[step[0] % 3])
                self.cpu_emoji.config(text=spins[(step[0] + 2) % 3])
                step[0] += 1
                self._anim_id = self.app.after(70, spin)
            else:
                self._anim_id = None
                self._resolve(choice, cpu, result)

        spin()

    def _resolve(self, choice, cpu, result):
        self.you_emoji.config(text=EMOJI[choice])
        self.cpu_emoji.config(text=EMOJI[cpu])
        self.you_choice.config(text=choice)
        self.cpu_choice.config(text=cpu)
        self.vs_lbl.config(text="VS")
        self._update_scores()

        msg_map = {
            "win":  ("🎉 You Win!",     WIN_CLR),
            "lose": ("😢 CPU Wins!",    LOSE_CLR),
            "tie":  ("🤝 It's a Tie!", TIE_CLR),
        }
        msg, col = msg_map[result]
        self.result_lbl.config(text=msg, fg=col)

        sv = self.streak
        sc = WIN_CLR if sv > 0 else LOSE_CLR if sv < 0 else MUTED
        self.streak_lbl.config(
            text=(f"+{sv}" if sv > 0 else str(sv)), fg=sc)
        wr = (f"{round(self.total_wins / self.total_games * 100)}%"
              if self.total_games > 0 else "—")
        self.winrate_lbl.config(text=wr)

        self._update_cpu_tip()
        self._refresh_history()

        def re_enable():
            self._set_btns_enabled(True)
            if self.timer_on:
                self._start_timer()

        self.app.after(350, re_enable)

    def _set_btns_enabled(self, enabled):
        self._btns_enabled = enabled
        cursor = "hand2" if enabled else "arrow"
        for widgets in self._btns.values():
            for w in widgets:
                try:
                    w.configure(cursor=cursor)
                except tk.TclError:
                    pass

    def _update_cpu_tip(self):
        tot = sum(self.cpu_counts.values())
        if tot < 4:
            self.tip_lbl.config(
                text="🧠 Play more rounds to reveal CPU pattern!", fg=MUTED)
            return
        fav = max(self.cpu_counts, key=self.cpu_counts.get)
        pct = round(self.cpu_counts[fav] / tot * 100)
        ctr = {"Rock": "Paper", "Paper": "Scissors", "Scissors": "Rock"}
        self.tip_lbl.config(
            text=(f"🧠 CPU loves {EMOJI[fav]} {fav} ({pct}%) — "
                  f"counter with {EMOJI[ctr[fav]]} {ctr[fav]}!"),
            fg=TIE_CLR)

    # ── Timer ───────────────────────────────────────
    def _toggle_timer(self):
        self.timer_on = not self.timer_on
        if self.timer_on:
            self.timer_btn.config(text="STOP", bg=LOSE_BG, fg=LOSE_CLR)
            self._start_timer()
        else:
            self.timer_btn.config(text="START", bg=WIN_BG, fg=WIN_CLR)
            self._stop_timer()

    def _start_timer(self):
        self._stop_timer()
        self._cd = self.timer_secs
        self._tick()

    def _tick(self):
        if self._cd <= 0:
            self.timer_lbl.config(text="GO!", fg=LOSE_CLR)
            self._timer_id = None
            if self._btns_enabled:
                self._play(random.choice(CHOICES))
            return
        col = WIN_CLR if self._cd > 5 else TIE_CLR if self._cd > 3 else LOSE_CLR
        self.timer_lbl.config(text=f"{self._cd}s", fg=col)
        self._cd -= 1
        self._timer_id = self.app.after(1000, self._tick)

    def _stop_timer(self):
        if self._timer_id is not None:
            try:
                self.app.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        try:
            self.timer_lbl.config(text=f"{self.timer_secs}s", fg=WIN_CLR)
        except Exception:
            pass

    # ── Reset ───────────────────────────────────────
    def _reset(self):
        self._stop_timer()
        self._cancel_anim()
        self.timer_on    = False
        self.timer_btn.config(text="START", bg=WIN_BG, fg=WIN_CLR)
        self.scores      = [0, 0, 0]
        self.history     = []
        self.streak      = 0
        self.best_streak = 0
        self.total_games = 0
        self.total_wins  = 0
        self.cpu_counts  = {"Rock": 0, "Paper": 0, "Scissors": 0}
        self._update_scores()
        self.you_emoji.config(text="🤔")
        self.cpu_emoji.config(text="🤖")
        self.you_choice.config(text="—")
        self.cpu_choice.config(text="—")
        self.result_lbl.config(text="👇 Pick your weapon!", fg=MUTED)
        self.streak_lbl.config(text="0", fg=TEXT)
        self.winrate_lbl.config(text="—", fg=TEXT)
        self.tip_lbl.config(
            text="🧠 Play a few rounds to unlock CPU pattern!", fg=MUTED)
        self._refresh_history()
        self._set_btns_enabled(True)


# ══════════════════════════════════════════════════════
#  2 PLAYER LOCAL
# ══════════════════════════════════════════════════════
class TwoPlayerGame(BaseGame):
    def __init__(self, app):
        super().__init__(app)
        self.names     = ["Player 1", "Player 2"]
        self.picks     = [None, None]
        self.name_vars = [tk.StringVar(value=n) for n in self.names]
        self._build_setup()

    # ── Setup Screen ────────────────────────────────
    def _build_setup(self):
        self._cancel_anim()
        for w in self.app.winfo_children():
            w.destroy()

        topbar = tk.Frame(self.app, bg=BG, pady=8)
        topbar.pack(fill="x")
        tk.Label(topbar, text="🆚  2 Players", bg=BG, fg=TEXT,
                 font=F_HEAD).pack(side="left", padx=14)
        self._back_btn(topbar)

        # Scoreboard — P1=🧑, P2=🧑
        self._build_scoreboard(self.app, self.names[0], self.names[1],
                               P1_CLR, P2_CLR,
                               icon1="🧑", icon2="🧑")
        self._update_scores()

        nf = tk.Frame(self.app, bg=BG, pady=10)
        nf.pack()
        tk.Label(nf, text="✏️  Player Names:", bg=BG, fg=MUTED,
                 font=F_SMALL).pack()
        row = tk.Frame(nf, bg=BG)
        row.pack(pady=6)

        icons   = ["🧑", "🧑"]
        p_colors = [P1_CLR, P2_CLR]
        for i in range(2):
            col_frame = tk.Frame(row, bg=BG)
            col_frame.pack(side="left", padx=10)
            tk.Label(col_frame, text=f"{icons[i]} Player {i+1}",
                     bg=BG, fg=p_colors[i], font=F_TINY).pack()
            e = tk.Entry(col_frame, textvariable=self.name_vars[i],
                         bg=CARD2, fg=p_colors[i],
                         insertbackground=p_colors[i],
                         font=F_MED, width=13, relief="flat", bd=4,
                         justify="center")
            e.pack()

        info = tk.Frame(self.app, bg=CARD, pady=12)
        info.pack(fill="x", padx=18, pady=8)
        tk.Label(info, text="ℹ️  How it works", bg=CARD, fg=MUTED,
                 font=(_font(9)[0], 9, "bold")).pack()
        tk.Label(info,
                 text="🧑 P1 picks secretly  →  🙈 Shield  →  🧑 P2 picks  →  🎊 Both revealed!",
                 bg=CARD, fg=TEXT, font=F_SMALL, wraplength=500).pack(pady=4)

        self._history_widget(self.app, two_player=True,
                              n1=self.names[0], n2=self.names[1])
        self._refresh_history()

        sf = tk.Frame(self.app, bg=BG, pady=10)
        sf.pack()
        tk.Button(sf, text="▶  Start Round", font=F_BTN, bg=P1_CLR, fg=TEXT,
                  relief="flat", bd=0, cursor="hand2", padx=24, pady=10,
                  command=self._start_round).pack(side="left", padx=8)
        tk.Button(sf, text="🔄 Reset", font=F_SMALL, bg=LOSE_BG, fg=LOSE_CLR,
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=10,
                  command=self._reset).pack(side="left")

    # ── Pick Screen ──────────────────────────────────
    def _build_pick_screen(self, player_idx):
        for w in self.app.winfo_children():
            w.destroy()

        p_name  = self.name_vars[player_idx].get().strip() or self.names[player_idx]
        p_color = P1_CLR if player_idx == 0 else P2_CLR
        other   = (self.name_vars[1 - player_idx].get().strip()
                   or self.names[1 - player_idx])
        p_icon  = "🧑" if player_idx == 0 else "🧑"

        hdr = tk.Frame(self.app, bg=p_color, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"{p_icon}  {p_name}'s Secret Turn",
                 bg=p_color, fg=TEXT, font=F_HEAD).pack()
        tk.Label(hdr, text=f"🙈  Don't show {other}!",
                 bg=p_color, fg="#cccccc", font=F_SMALL).pack()

        tk.Label(self.app,
                 text="👇 Choose your weapon — pick stays hidden until both choose",
                 bg=BG, fg=MUTED, font=F_TINY, wraplength=500).pack(pady=(14, 4))

        self.pick_lbl = tk.Label(self.app, text="No pick yet",
                                  bg=BG, fg=MUTED, font=F_MED)
        self.pick_lbl.pack(pady=(0, 8))

        btn_row = tk.Frame(self.app, bg=BG)
        btn_row.pack(pady=4)
        colors = {"Rock": ROCK_CLR, "Paper": PAPER_CLR, "Scissors": SCISSORS_CLR}
        bgs    = {"Rock": "#3d1a1a", "Paper": "#0d2d2c", "Scissors": "#3d3200"}

        for ch in CHOICES:
            col = colors[ch]; bg = bgs[ch]
            outer = tk.Frame(btn_row, bg=col, padx=2, pady=2)
            outer.pack(side="left", padx=10)
            inner = tk.Frame(outer, bg=bg, padx=22, pady=14)
            inner.pack()
            el = tk.Label(inner, text=EMOJI[ch], bg=bg, fg=TEXT, font=F_EMOJI)
            el.pack()
            nl = tk.Label(inner, text=ch.upper(), bg=bg, fg=col,
                          font=_font(11, bold=True))
            nl.pack(pady=(4, 0))
            for w in [outer, inner, el, nl]:
                w.bind("<Button-1>",
                       lambda e, c=ch, pi=player_idx: self._pick(pi, c))
                w.configure(cursor="hand2")

        cf = tk.Frame(self.app, bg=BG, pady=14)
        cf.pack()
        next_txt = (f"✅ Confirm — Pass to {other} →"
                    if player_idx == 0 else "✅ Confirm and Reveal! 🎊")
        self.confirm_btn = tk.Button(cf, text=next_txt,
            font=F_BTN, bg=CARD2, fg=MUTED,
            relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
            command=lambda: self._confirm(player_idx), state="disabled")
        self.confirm_btn.pack()

    # ── Shield Screen ────────────────────────────────
    def _build_shield(self):
        for w in self.app.winfo_children():
            w.destroy()

        p1_name = self.name_vars[0].get().strip() or "Player 1"
        p2_name = self.name_vars[1].get().strip() or "Player 2"

        tk.Label(self.app, text="🙈", bg=BG, fg=TEXT,
                 font=_emoji_font(72)).pack(pady=(50, 10))
        tk.Label(self.app, text=f"✅  {p1_name} has picked!",
                 bg=BG, fg=P1_CLR, font=F_TITLE).pack()
        tk.Label(self.app,
                 text=f"Now hand the screen to  🧑 {p2_name}  without peeking!",
                 bg=BG, fg=MUTED, font=F_HEAD, wraplength=460).pack(pady=(8, 30))
        tk.Button(self.app, text=f"🧑  {p2_name}, I'm ready! 👊",
                  font=F_BTN, bg=P2_CLR, fg=TEXT,
                  relief="flat", bd=0, cursor="hand2", pady=12,
                  command=lambda: self._build_pick_screen(1)).pack()

    # ── Reveal Screen ────────────────────────────────
    def _build_reveal(self):
        for w in self.app.winfo_children():
            w.destroy()

        n1 = self.name_vars[0].get().strip() or "Player 1"
        n2 = self.name_vars[1].get().strip() or "Player 2"
        a, b = self.picks

        if   a == b:         result, msg, col = "tie", "🤝 It's a Tie!", TIE_CLR
        elif BEATS[a] == b:  result, msg, col = "p1",  f"🎉 {n1} Wins!",  P1_CLR
        else:                result, msg, col = "p2",  f"🎉 {n2} Wins!",  P2_CLR

        if   result == "p1": self.scores[0] += 1
        elif result == "p2": self.scores[1] += 1
        else:                self.scores[2] += 1

        self.names = [n1, n2]
        self.history.insert(0, {"p1": a, "p2": b, "result": result})
        if len(self.history) > 8:
            self.history.pop()

        topbar = tk.Frame(self.app, bg=BG, pady=8)
        topbar.pack(fill="x")
        tk.Label(topbar, text="🆚  2 Players", bg=BG, fg=TEXT,
                 font=F_HEAD).pack(side="left", padx=14)
        self._back_btn(topbar)

        self._build_scoreboard(self.app, n1, n2, P1_CLR, P2_CLR,
                               icon1="🧑", icon2="🧑")
        self._update_scores()

        res_f = tk.Frame(self.app, bg=col, pady=14)
        res_f.pack(fill="x", padx=18, pady=(10, 6))
        tk.Label(res_f, text=msg, bg=col, fg=BG, font=F_RESULT).pack()

        arena = tk.Frame(self.app, bg=BG, pady=6)
        arena.pack(fill="x", padx=18)
        arena.columnconfigure(0, weight=1)
        arena.columnconfigure(1, weight=0)
        arena.columnconfigure(2, weight=1)

        card_colors = {
            "p1":  [(P1_CLR, P1_BG),    (LOSE_CLR, LOSE_BG)],
            "p2":  [(LOSE_CLR, LOSE_BG), (P2_CLR,   P2_BG)],
            "tie": [(TIE_CLR,  TIE_BG),  (TIE_CLR,  TIE_BG)],
        }
        sides      = [(n1, a, 0), (n2, b, 2)]
        side_icons = ["🧑", "🧑"]
        for (name, pick, col_idx), icon in zip(sides, side_icons):
            bc, ibg = card_colors[result][col_idx // 2]
            fr  = tk.Frame(arena, bg=bc, padx=2, pady=2)
            fr.grid(row=0, column=col_idx, sticky="nsew")
            inn = tk.Frame(fr, bg=ibg, pady=14)
            inn.pack(fill="both", expand=True)
            tk.Label(inn, text=f"{icon}  {name.upper()}",
                     bg=ibg, fg=bc, font=F_SMALL).pack()
            tk.Label(inn, text=EMOJI[pick], bg=ibg, fg=TEXT,
                     font=F_EMOJI).pack(pady=4)
            tk.Label(inn, text=pick, bg=ibg, fg=MUTED, font=F_SMALL).pack()

        vs_f = tk.Frame(arena, bg=BG, width=60)
        vs_f.grid(row=0, column=1, padx=8)
        tk.Label(vs_f, text="VS", bg=CARD2, fg=MUTED,
                 font=F_MED, width=4, pady=10).pack()

        self._history_widget(self.app, two_player=True, n1=n1, n2=n2)
        self._refresh_history()

        sf = tk.Frame(self.app, bg=BG, pady=10)
        sf.pack()
        tk.Button(sf, text="▶  Next Round", font=F_BTN, bg=P1_CLR, fg=TEXT,
                  relief="flat", bd=0, cursor="hand2", padx=20, pady=10,
                  command=self._start_round).pack(side="left", padx=8)
        tk.Button(sf, text="🔄 Reset", font=F_SMALL, bg=LOSE_BG, fg=LOSE_CLR,
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=10,
                  command=self._reset).pack(side="left")

    # ── Flow control ─────────────────────────────────
    def _start_round(self):
        self.picks = [None, None]
        self._build_pick_screen(0)

    def _pick(self, player_idx, choice):
        self.picks[player_idx] = choice
        self.pick_lbl.config(
            text=f"✅  {EMOJI[choice]}  {choice} selected!",
            fg=P1_CLR if player_idx == 0 else P2_CLR)
        self.confirm_btn.config(
            state="normal",
            bg=P1_CLR if player_idx == 0 else P2_CLR,
            fg=TEXT)

    def _confirm(self, player_idx):
        if self.picks[player_idx] is None:
            return
        if player_idx == 0:
            self._build_shield()
        else:
            self._build_reveal()

    def _reset(self):
        self.scores  = [0, 0, 0]
        self.history = []
        self.picks   = [None, None]
        self._build_setup()


# ══════════════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()