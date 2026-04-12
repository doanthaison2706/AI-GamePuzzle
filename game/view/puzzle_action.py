from tkinter import messagebox


class PuzzleAction:
    """Handles button click actions in the Puzzle window."""

    def __init__(self, puzzle_window):
        self.pz = puzzle_window

    def on_new_game(self):
        self.pz.control.new_game()
        self.pz.control.start_game()

    def on_out_game(self):
        result = messagebox.askyesno(
            "Exit Game?",
            "Are you sure you want to return to Main Menu?",
            parent=self.pz,
        )
        if result:
            self.pz.control.time_controller.stop()
            self.pz.destroy()
            self.pz.main_menu.deiconify()
