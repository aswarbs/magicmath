import tkinter as tk

class GameWindow():
    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Mathquest")
        self.entities = []

        # Set window size to 640x480 (4:3 ratio)
        self.master.geometry("640x480")
        self.canvas = tk.Canvas(self.master, bg="white", width=640, height=480)
        self.canvas.pack(fill="both", expand=True)

    def mainloop(self):
        # Run the main event loop
        while True:
            _ = [e.draw(self.canvas) for e in self.entities]
            _ = [e.think() for e in self.entities]
            self.master.update()
