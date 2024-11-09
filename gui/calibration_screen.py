import tkinter as tk

class CalibrationScreen:

    def __init__(self, parent, master):
        self.parent = parent
        self.master = master

        # Set background to white
        self.master.configure(bg="white")

        # Call display_content to create the "X" labels
        self.display_content()

        # Reposition the labels on window resize or display
        self.master.bind("<Configure>", self.update_corner_labels)

    def display_content(self):
        # Red X font and color
        x_font = ("Arial", 36, "bold")
        x_color = "red"

        # Create labels for each corner
        self.label_tl = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_tr = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_bl = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_br = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")

        # Initial placement
        self.label_tl.place(x=10, y=10, anchor="nw")

        # Trigger positioning for other corners
        self.update_corner_labels()

    def update_corner_labels(self, event=None):
        # Get the current width and height of the master window
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        # Place labels at each corner
        self.label_tr.place(x=width - 10, y=10, anchor="ne")
        self.label_bl.place(x=10, y=height - 10, anchor="sw")
        self.label_br.place(x=width - 10, y=height - 10, anchor="se")

