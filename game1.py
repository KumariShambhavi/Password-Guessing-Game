import random
import string
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------
# THEME & CONFIG
# ----------------------------
BG = "#0b0b10"              # near-black
PANEL = "#12121a"           # dark panel
ACCENT = "#7c3aed"          # purple
ACCENT_HOVER = "#8b5cf6"    # lighter purple
TEXT = "#e5e7eb"            # light gray text
MUTED = "#9ca3af"           # muted gray
OK_PURPLE = "#a78bfa"       # correct-position tile
PRESENT_PURPLE = "#6d28d9"  # present-diff-pos tile
ABSENT_GRAY = "#3f3f46"     # absent tile

MAX_ATTEMPTS = 6

EASY_WORDS = ["apple", "train", "money", "india"]
MEDIUM_WORDS = ["python", "bottle", "monkey", "planet", "laptop"]
HARD_WORDS = ["programming", "development", "computer", "technology", "artificial"]

DIFFICULTY_POOLS = {
    "Easy": EASY_WORDS,
    "Medium": MEDIUM_WORDS,
    "Hard": HARD_WORDS
}

BASE_SCORE = {"Easy": 50, "Medium": 100, "Hard": 150}
WRONG_GUESS_PENALTY = 10
HINT_PENALTY = 15

# ----------------------------
# APP
# ----------------------------
class PasswordGuessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Guessing Game")
        self.configure(bg=BG)
        self.geometry("820x640")
        self.minsize(760, 560)

        # Use ttk styling with custom theme
        self._init_style()

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (StartScreen, GameScreen, ResultScreen):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show("StartScreen")

        # state shared across screens
        self.secret = ""
        self.difficulty = "Easy"
        self.attempts = 0
        self.hints_used = 0
        self.score = 0
        self.guess_history = []  # (guess, feedback_list)

    def _init_style(self):
        style = ttk.Style(self)
        # On some systems, 'clam' or 'alt' is safer to customize
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 12))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 26))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 12))

        style.configure("Accent.TButton",
                        background=ACCENT, foreground="white",
                        padding=10, font=("Segoe UI Semibold", 12))
        style.map("Accent.TButton",
                  background=[("active", ACCENT_HOVER)])

        style.configure("Ghost.TButton",
                        background=PANEL, foreground=TEXT,
                        padding=8, font=("Segoe UI", 11), borderwidth=0, relief="flat")
        style.map("Ghost.TButton",
                  background=[("active", "#1f1f2a")])

        style.configure("Info.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 12))
        style.configure("Header.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI Semibold", 14))

        style.configure("TEntry", fieldbackground="#1a1a22", foreground=TEXT, insertcolor=TEXT)
        style.map("TEntry",
                  fieldbackground=[("readonly", "#1a1a22")])

    def show(self, name):
        self.frames[name].tkraise()

    # Game control methods
    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.secret = random.choice(DIFFICULTY_POOLS[difficulty]).lower()
        self.attempts = 0
        self.hints_used = 0
        self.score = 0
        self.guess_history = []
        self.frames["GameScreen"].setup_for_secret(self.secret, difficulty)
        self.show("GameScreen")

    def finish_game(self, won):
        # scoring
        score = BASE_SCORE[self.difficulty]
        wrongs = self.attempts - (1 if won else 0)  # if won, last attempt is correct
        score -= max(0, wrongs) * WRONG_GUESS_PENALTY
        score -= self.hints_used * HINT_PENALTY
        self.score = max(0, score)

        self.frames["ResultScreen"].populate(won, self.secret, self.difficulty,
                                             self.attempts, self.hints_used, self.score)
        self.show("ResultScreen")

    def play_again(self):
        self.show("StartScreen")


# ----------------------------
# START SCREEN
# ----------------------------
class StartScreen(tk.Frame):
    def __init__(self, parent, app: PasswordGuessApp):
        super().__init__(parent, bg=BG)
        self.app = app

        wrapper = ttk.Frame(self, style="TFrame")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(wrapper, text="Password Guessing Game", style="Title.TLabel")
        subtitle = ttk.Label(wrapper, text="Choose your difficulty level to begin",
                             style="Sub.TLabel")

        btns = ttk.Frame(wrapper, style="TFrame")
        for d in ("Easy", "Medium", "Hard"):
            b = ttk.Button(btns, text=d, style="Accent.TButton",
                           command=lambda dd=d: self.app.start_game(dd))
            b.pack(side="left", padx=10, pady=10)

        title.pack(pady=(0, 8))
        subtitle.pack(pady=(0, 18))
        btns.pack()

        # credit / info
        info = ttk.Label(wrapper,
                         text="Theme: black & purple • Wordle-style feedback • Hints • Scoring • 6 attempts",
                         style="Sub.TLabel")
        info.pack(pady=16)


# ----------------------------
# GAME SCREEN
# ----------------------------
class GameScreen(tk.Frame):
    def __init__(self, parent, app: PasswordGuessApp):
        super().__init__(parent, bg=BG)
        self.app = app
        self.secret = ""
        self.row_frames = []
        self.tiles = []   # list of lists (row->label tiles)
        self.hint_state = 0  # how many hints shown

        # Layout
        top = ttk.Frame(self, style="TFrame")
        top.pack(fill="x", padx=24, pady=(20, 10))

        self.title = ttk.Label(top, text="Guess the Password", style="Title.TLabel")
        self.title.pack(side="left")

        # Attempts & difficulty badge
        self.info_badge = ttk.Label(top, text="", style="Sub.TLabel")
        self.info_badge.pack(side="right")

        center = ttk.Frame(self, style="TFrame")
        center.pack(fill="both", expand=True, padx=24, pady=10)

        # Board panel
        self.board = ttk.Frame(center, style="Panel.TFrame")
        self.board.pack(side="top", pady=(0, 16), fill="x")
        board_pad = tk.Frame(self.board, bg=PANEL)
        board_pad.pack(padx=16, pady=16, fill="x")

        self.rows_container = tk.Frame(board_pad, bg=PANEL)
        self.rows_container.pack()

        # Input panel
        self.input_panel = ttk.Frame(center, style="Panel.TFrame")
        self.input_panel.pack(fill="x")
        ip_pad = tk.Frame(self.input_panel, bg=PANEL)
        ip_pad.pack(padx=16, pady=16, fill="x")

        self.prompt = ttk.Label(ip_pad, text="", style="Header.TLabel")
        self.prompt.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.entry = ttk.Entry(ip_pad, width=30)
        self.entry.grid(row=1, column=0, sticky="w")
        self.entry.bind("<Return>", lambda e: self.submit_guess())

        self.submit_btn = ttk.Button(ip_pad, text="Submit Guess", style="Accent.TButton",
                                     command=self.submit_guess)
        self.submit_btn.grid(row=1, column=1, padx=10)

        self.hint_btn = ttk.Button(ip_pad, text="Hint", style="Ghost.TButton",
                                   command=self.show_hint)
        self.hint_btn.grid(row=1, column=2, padx=6)

        self.hint_label = ttk.Label(ip_pad, text="", style="Info.TLabel")
        self.hint_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.footer = ttk.Frame(self, style="TFrame")
        self.footer.pack(fill="x", padx=24, pady=10)
        self.back_btn = ttk.Button(self.footer, text="Back to Menu", style="Ghost.TButton",
                                   command=self.app.play_again)
        self.back_btn.pack(side="left")

        self.status_label = ttk.Label(self.footer, text="", style="Sub.TLabel")
        self.status_label.pack(side="right")

    def setup_for_secret(self, secret, difficulty):
        self.secret = secret
        self.hint_state = 0
        self.app.attempts = 0
        self.app.hints_used = 0
        self.app.guess_history = []

        # clear board
        for rf in self.row_frames:
            rf.destroy()
        self.row_frames.clear()
        self.tiles.clear()
        self.hint_label.config(text="")
        self.entry.delete(0, "end")

        # rows = MAX_ATTEMPTS x len(secret)
        for r in range(MAX_ATTEMPTS):
            row_frame = tk.Frame(self.rows_container, bg=PANEL)
            row_frame.pack(pady=4)
            row_tiles = []
            for c in range(len(secret)):
                lbl = tk.Label(row_frame, text=" ", width=3, height=1,
                               font=("Segoe UI Semibold", 18),
                               bg="#1e1e28", fg=TEXT,
                               bd=0, relief="flat",
                               padx=10, pady=8)
                lbl.grid(row=0, column=c, padx=4, pady=2)
                row_tiles.append(lbl)
            self.row_frames.append(row_frame)
            self.tiles.append(row_tiles)

        self.title.config(text="Guess the Password")
        self.prompt.config(text=f"Enter a {len(secret)}-letter word")
        self.info_badge.config(text=f"Difficulty: {difficulty}  •  Attempts left: {MAX_ATTEMPTS}")
        self.status_label.config(text="Wordle-style feedback: purple = correct spot, violet = in word, gray = not present")

        # put focus on entry
        self.after(100, lambda: self.entry.focus_set())

    def submit_guess(self):
        guess = self.entry.get().strip().lower()
        if not guess:
            return

        if not all(ch in string.ascii_letters for ch in guess):
            messagebox.showinfo("Invalid", "Use letters only (A–Z).")
            return

        if len(guess) != len(self.secret):
            messagebox.showinfo("Invalid length",
                                f"Your guess must be {len(self.secret)} letters.")
            return

        # apply feedback
        feedback = evaluate_guess(guess, self.secret)  # list of "correct"/"present"/"absent"
        self.app.attempts += 1
        row_index = self.app.attempts - 1
        self._render_row(row_index, guess, feedback)
        self.entry.delete(0, "end")

        # update info
        remaining = MAX_ATTEMPTS - self.app.attempts
        self.info_badge.config(
            text=f"Difficulty: {self.app.difficulty}  •  Attempts left: {remaining}"
        )

        # win/lose check
        if all(tag == "correct" for tag in feedback):
            self.app.finish_game(won=True)
            return
        if self.app.attempts >= MAX_ATTEMPTS:
            self.app.finish_game(won=False)
            return

    def _render_row(self, row, guess, feedback):
        tiles = self.tiles[row]

        def animate_tile(index, phase=0):
            """Animate a single tile's flip in 3 phases."""
            lbl = tiles[index]
            ch = guess.upper()[index]
            tag = feedback[index]

            colors = {
                "correct": OK_PURPLE,
                "present": PRESENT_PURPLE,
                "absent": ABSENT_GRAY
            }
            target_bg = colors[tag]

            if phase == 0:
                # Start shrink
                lbl.config(height=1)
                self.after(50, lambda: animate_tile(index, 1))
            elif phase == 1:
                # Mid-flip — change text and background
                lbl.config(text=ch, bg=target_bg, height=1)
                self.after(50, lambda: animate_tile(index, 2))
            elif phase == 2:
                # Expand back to normal height
                lbl.config(height=2)

        # Stagger each tile animation for a cascade effect
        for i in range(len(guess)):
            self.after(i * 120, lambda idx=i: animate_tile(idx))







    def show_hint(self):
        # Two staged hints:
        # 1) Reveal first letter
        # 2) Show a scrambled (anagram) of the secret
        if self.hint_state == 0:
            self.hint_state = 1
            self.app.hints_used += 1
            self.hint_label.config(text=f"Hint: The word starts with '{self.secret[0].upper()}'.")
        elif self.hint_state == 1:
            self.hint_state = 2
            self.app.hints_used += 1
            scrambled = scramble(self.secret)
            # Avoid showing identical scramble
            if scrambled == self.secret:
                scrambled = scramble(self.secret)
            self.hint_label.config(text=f"Hint: Scrambled letters — {scrambled.upper()}")
        else:
            self.hint_label.config(text="No more hints available.")

# ----------------------------
# RESULT SCREEN
# ----------------------------
class ResultScreen(tk.Frame):
    def __init__(self, parent, app: PasswordGuessApp):
        super().__init__(parent, bg=BG)
        self.app = app

        wrapper = ttk.Frame(self, style="TFrame")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        self.title = ttk.Label(wrapper, text="", style="Title.TLabel")
        self.title.pack(pady=(0, 8))

        self.summary = ttk.Label(wrapper, text="", style="Sub.TLabel")
        self.summary.pack(pady=(0, 16))

        panel = ttk.Frame(wrapper, style="Panel.TFrame")
        panel.pack(fill="x")
        pad = tk.Frame(panel, bg=PANEL)
        pad.pack(padx=16, pady=16)

        self.details = ttk.Label(pad, text="", style="Info.TLabel", justify="left")
        self.details.pack()

        btns = ttk.Frame(wrapper, style="TFrame")
        btns.pack(pady=18)
        self.play_again_btn = ttk.Button(btns, text="Play Again", style="Accent.TButton",
                                         command=self.app.play_again)
        self.play_again_btn.pack(side="left", padx=8)

        self.exit_btn = ttk.Button(btns, text="Exit", style="Ghost.TButton",
                                   command=self.app.destroy)
        self.exit_btn.pack(side="left", padx=8)

    def populate(self, won, secret, difficulty, attempts, hints_used, score):
        if won:
            self.title.config(text="You Cracked It! 🎉")
            self.summary.config(text=f"The password was '{secret.upper()}'.")
        else:
            self.title.config(text="Out of Attempts 😿")
            self.summary.config(text=f"The password was '{secret.upper()}'. Better luck next time!")

        lines = [
            f"Difficulty: {difficulty}",
            f"Attempts used: {attempts}/{MAX_ATTEMPTS}",
            f"Hints used: {hints_used}",
            f"Score: {score}"
        ]
        self.details.config(text="\n".join(lines))


# ----------------------------
# GAME LOGIC
# ----------------------------
def evaluate_guess(guess: str, secret: str):
    """
    Returns a list with values in {"correct", "present", "absent"} for each letter.
    Wordle-like rules with duplicate letter handling.
    """
    result = ["absent"] * len(secret)
    secret_counts = {}

    # First pass: mark correct
    for i, (g, s) in enumerate(zip(guess, secret)):
        if g == s:
            result[i] = "correct"
        else:
            secret_counts[s] = secret_counts.get(s, 0) + 1

    # Second pass: mark present
    for i, g in enumerate(guess):
        if result[i] == "correct":
            continue
        if secret_counts.get(g, 0) > 0:
            result[i] = "present"
            secret_counts[g] -= 1
        else:
            result[i] = "absent"

    return result

def scramble(word: str):
    letters = list(word)
    random.shuffle(letters)
    return "".join(letters)

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    app = PasswordGuessApp()
    app.mainloop()
