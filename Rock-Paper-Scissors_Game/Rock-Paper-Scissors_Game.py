# Rock • Paper • Scissors
# built during a boring meeting. now it's my tiny focus break.

import tkinter as tk
from tkinter import messagebox
import random


class RockPaperScissors:
    def __init__(self):
        # window basics
        self.window = tk.Tk()
        self.window.title("Rock Paper Scissors - The Ultimate Showdown")
        self.window.geometry("680x720")      # wide-ish so things fit nicely
        self.window.minsize(660, 680)        # safety net: prevents label clipping
        self.window.configure(bg="#1e3a8a")
        self.window.resizable(True, True)

        # let the grid breathe
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(2, weight=1)  # game area expands

        # game state
        self.player_score = 0
        self.computer_score = 0
        self.rounds_played = 0
        self.game_history = []  # last results go here

        # choices (kept simple)
        self.choices = {
            "rock":     {"emoji": "🪨", "name": "Rock"},
            "paper":    {"emoji": "📄", "name": "Paper"},
            "scissors": {"emoji": "✂️", "name": "Scissors"},
        }
        self.winning_moves = {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock",
        }

        self._build_ui()

    # ---------- UI ----------

    def _build_ui(self):
        # header
        header = tk.Frame(self.window, bg="#1e40af", height=80)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        tk.Label(
            header,
            text="🎮 ROCK  PAPER  SCISSORS 🎮",
            font=("Impact", 20, "bold"),
            fg="#fbbf24",
            bg="#1e40af",
        ).pack(pady=20)

        # scoreboard
        score_frame = tk.Frame(self.window, bg="#1e3a8a")
        score_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        score_frame.columnconfigure(0, weight=1)

        box = tk.Frame(score_frame, bg="#374151", relief="ridge", bd=2)
        box.grid(row=0, column=0, padx=16, pady=10, sticky="ew")
        box.columnconfigure(0, weight=1)

        self.score_label = tk.Label(
            box,
            text="🏆 SCOREBOARD 🏆\nYou: 0  |  Computer: 0  |  Rounds: 0",
            font=("Arial", 14, "bold"),
            fg="#10b981",
            bg="#374151",
            pady=10,
            padx=20,
            justify="center",
            wraplength=560,  # stays inside the box
        )
        self.score_label.grid(row=0, column=0, sticky="ew")

        # game area
        game = tk.Frame(self.window, bg="#1e3a8a")
        game.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        game.columnconfigure(0, weight=1)

        tk.Label(
            game,
            text="Choose your weapon wisely! 🤔",
            font=("Arial", 13, "bold"),
            fg="#e5e7eb",
            bg="#1e3a8a",
            anchor="center",
        ).grid(row=0, column=0, pady=(6, 12), sticky="ew")

        # three big buttons (stretchy)
        buttons = tk.Frame(game, bg="#1e3a8a")
        buttons.grid(row=1, column=0, pady=6, sticky="ew")
        for i in range(3):
            buttons.columnconfigure(i, weight=1, uniform="btns")

        btn_style = dict(font=("Arial", 14, "bold"), height=2, relief="raised", bd=3, cursor="hand2")

        tk.Button(
            buttons, text="🪨\nROCK", command=lambda: self.play("rock"),
            bg="#7c2d12", fg="white", activebackground="#a8432b", **btn_style
        ).grid(row=0, column=0, padx=6, sticky="ew")

        tk.Button(
            buttons, text="📄\nPAPER", command=lambda: self.play("paper"),
            bg="#1e40af", fg="white", activebackground="#3b82f6", **btn_style
        ).grid(row=0, column=1, padx=6, sticky="ew")

        tk.Button(
            buttons, text="✂️\nSCISSORS", command=lambda: self.play("scissors"),
            bg="#7c2d12", fg="white", activebackground="#a8432b", **btn_style
        ).grid(row=0, column=2, padx=6, sticky="ew")

        # battle zone (the VS row + result text)
        arena = tk.Frame(game, bg="#374151", relief="sunken", bd=3)
        arena.grid(row=2, column=0, pady=12, sticky="nsew")
        arena.columnconfigure(0, weight=1)
        arena.rowconfigure(1, weight=1)

        vs = tk.Frame(arena, bg="#374151")
        vs.grid(row=0, column=0, sticky="ew", padx=10, pady=12)

        # IMPORTANT: equal columns + minimum size so right label never clips
        vs.columnconfigure(0, weight=1, uniform="vs", minsize=200)
        vs.columnconfigure(1, weight=1, uniform="vs", minsize=120)
        vs.columnconfigure(2, weight=1, uniform="vs", minsize=200)

        self.player_display = tk.Label(
            vs, text="❓\nYour Choice", font=("Arial", 18, "bold"),
            fg="#10b981", bg="#374151", justify="center", width=16
        )
        self.player_display.grid(row=0, column=0, sticky="ew", padx=8)

        tk.Label(
            vs, text="⚔️\nVS\n⚔️", font=("Arial", 16, "bold"),
            fg="#fbbf24", bg="#374151", justify="center"
        ).grid(row=0, column=1, sticky="ew")

        self.computer_display = tk.Label(
            vs, text="❓\nComputer Choice", font=("Arial", 18, "bold"),
            fg="#ef4444", bg="#374151", justify="center", width=16
        )
        self.computer_display.grid(row=0, column=2, sticky="ew", padx=8)

        self.result_label = tk.Label(
            arena, text="Make your move!", font=("Arial", 16, "bold"),
            fg="#e5e7eb", bg="#374151", pady=12, padx=10, justify="center", wraplength=560
        )
        self.result_label.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 10))

        # controls
        controls = tk.Frame(game, bg="#1e3a8a")
        controls.grid(row=3, column=0, pady=8, sticky="ew")
        for i in range(3):
            controls.columnconfigure(i, weight=1, uniform="ctrl")

        tk.Button(
            controls, text="🔄 Play Again", command=self.reset_round,
            font=("Arial", 12, "bold"), bg="#059669", fg="white",
            activebackground="#10b981", padx=12, pady=8, relief="raised", bd=2, cursor="hand2"
        ).grid(row=0, column=0, padx=6, sticky="ew")

        tk.Button(
            controls, text="🔄 Reset Scores", command=self.reset_game,
            font=("Arial", 12, "bold"), bg="#dc2626", fg="white",
            activebackground="#ef4444", padx=12, pady=8, relief="raised", bd=2, cursor="hand2"
        ).grid(row=0, column=1, padx=6, sticky="ew")

        tk.Button(
            controls, text="📊 History", command=self.show_history,
            font=("Arial", 12, "bold"), bg="#7c3aed", fg="white",
            activebackground="#8b5cf6", padx=12, pady=8, relief="raised", bd=2, cursor="hand2"
        ).grid(row=0, column=2, padx=6, sticky="ew")

        # keyboard shortcuts (lazy mode)
        self.window.bind("<Key>", self._on_key)
        self.window.bind("<Configure>", self._on_resize)  # keep wraplengths in line
        self.window.focus_set()

    # ---------- tiny helpers ----------

    def _thinking(self):
        return random.choice(["🤔 Computing...", "⚡ Processing...", "🎲 Deciding..."])

    def _on_resize(self, event):
        # adjust wrap lengths to the window width so text doesn't spill
        wrap = max(360, event.width - 120)
        self.score_label.config(wraplength=wrap)
        self.result_label.config(wraplength=wrap)

    # ---------- gameplay ----------

    def play(self, player_choice):
        # computer picks something, obviously
        computer_choice = random.choice(list(self.choices.keys()))

        # show the picks immediately
        p = self.choices[player_choice]
        c = self.choices[computer_choice]
        self.player_display.config(text=f"{p['emoji']}\n{p['name']}")
        self.computer_display.config(text=f"{c['emoji']}\n{c['name']}")

        # little pause for drama
        self.result_label.config(text=self._thinking())
        self.window.after(700, lambda: self._finish_round(player_choice, computer_choice))

    def _finish_round(self, player_choice, computer_choice):
        self.rounds_played += 1

        if player_choice == computer_choice:
            result, text, color = "tie", "🤝 It's a TIE!", "#fbbf24"
        elif self.winning_moves[player_choice] == computer_choice:
            result, text, color = "win", "🎉 YOU WIN!", "#10b981"
            self.player_score += 1
        else:
            result, text, color = "lose", "😭 COMPUTER WINS!", "#ef4444"
            self.computer_score += 1

        self.result_label.config(text=text, fg=color)
        self._update_scoreboard()

        # stash round info (handy for history)
        self.game_history.append({
            "round": self.rounds_played,
            "player": player_choice,
            "computer": computer_choice,
            "result": result
        })

        self._flavor(player_choice, computer_choice, result)

    def _flavor(self, player_choice, computer_choice, result):
        # tiny commentary so it feels alive
        flavor = {
            "win": ["Nice move! 🔥", "You're on fire! 🌟", "Crushing it! 💪", "Computer didn't see that coming! 😎"],
            "lose": ["Ouch! Try again 😅", "Computer got lucky 🤖", "That was close! 😬", "Revenge time! ⚡"],
            "tie":  ["Great minds think alike 🧠", "Perfectly matched ⚖️", "Tie breaker needed 🔥"],
        }
        explain = {
            ("rock", "scissors"): "Rock crushes Scissors! 🪨💥✂️",
            ("scissors", "paper"): "Scissors cuts Paper! ✂️💥📄",
            ("paper", "rock"): "Paper covers Rock! 📄💥🪨",
        }

        if result == "tie":
            extra = random.choice(flavor["tie"])
            self.result_label.config(text=f"{self.result_label.cget('text')}\n{extra}")
            return

        # pick the right explanation based on who won
        if result == "win":
            rule = explain.get((player_choice, computer_choice), "")
            extra = random.choice(flavor["win"])
        else:
            rule = explain.get((computer_choice, player_choice), "")
            extra = random.choice(flavor["lose"])

        self.result_label.config(text=f"{self.result_label.cget('text')}\n{rule}\n{extra}")

    def _update_scoreboard(self):
        txt = f"🏆 SCOREBOARD 🏆\nYou: {self.player_score}  |  Computer: {self.computer_score}  |  Rounds: {self.rounds_played}"
        self.score_label.config(text=txt)

        # color hint: green if you're ahead, red if not, yellow if tied
        if self.player_score > self.computer_score:
            self.score_label.config(fg="#10b981")
        elif self.computer_score > self.player_score:
            self.score_label.config(fg="#ef4444")
        else:
            self.score_label.config(fg="#fbbf24")

    # ---------- buttons / shortcuts ----------

    def reset_round(self):
        self.player_display.config(text="❓\nYour Choice")
        self.computer_display.config(text="❓\nComputer Choice")
        self.result_label.config(text="Make your move!", fg="#e5e7eb")

    def reset_game(self):
        if messagebox.askyesno("Reset Game", "Reset all scores?"):
            self.player_score = 0
            self.computer_score = 0
            self.rounds_played = 0
            self.game_history = []
            self._update_scoreboard()
            self.reset_round()

    def show_history(self):
        if not self.game_history:
            messagebox.showinfo("History", "No games played yet!")
            return

        top = tk.Toplevel(self.window)
        top.title("Game History")
        top.geometry("460x360")
        top.minsize(420, 300)
        top.configure(bg="#374151")
        top.columnconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)

        tk.Label(
            top, text="📊 Game History", font=("Arial", 16, "bold"), fg="#fbbf24", bg="#374151"
        ).grid(row=0, column=0, pady=10, sticky="ew")

        area = tk.Frame(top, bg="#374151")
        area.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        area.columnconfigure(0, weight=1)
        area.rowconfigure(0, weight=1)

        txt = tk.Text(area, bg="#1f2937", fg="#e5e7eb", font=("Courier", 10), wrap="word")
        sc = tk.Scrollbar(area, command=txt.yview)
        txt.config(yscrollcommand=sc.set)

        lines = []
        for g in self.game_history[-10:]:
            p = self.choices[g["player"]]["emoji"]
            c = self.choices[g["computer"]]["emoji"]
            r = {"win": "🏆", "lose": "💀", "tie": "🤝"}[g["result"]]
            lines.append(f"Round {g['round']}: {p} vs {c} {r}")
        txt.insert("1.0", "\n".join(lines))
        txt.config(state="disabled")

        txt.grid(row=0, column=0, sticky="nsew")
        sc.grid(row=0, column=1, sticky="ns")

    def _on_key(self, e):
        ch = e.char.lower()
        if ch == "r":
            self.play("rock")
        elif ch == "p":
            self.play("paper")
        elif ch == "s":
            self.play("scissors")
        elif ch == " ":
            self.reset_round()

    # ---------- app ----------

    def run(self):
        messagebox.showinfo(
            "Welcome!",
            "🎮 Welcome to Rock Paper Scissors!\n\n"
            "HOW TO PLAY:\n"
            "• Click the buttons or use keyboard shortcuts\n"
            "• R = Rock, P = Paper, S = Scissors\n"
            "• Spacebar = Play Again\n\n"
            "RULES:\n"
            "🪨 Rock crushes ✂️ Scissors\n"
            "✂️ Scissors cuts 📄 Paper\n"
            "📄 Paper covers 🪨 Rock\n\n"
            "Good luck! 🍀"
        )
        self.window.mainloop()


def main():
    game = RockPaperScissors()
    game.run()


if __name__ == "__main__":
    main()
