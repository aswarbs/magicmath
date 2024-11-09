from engine.GameEntity import GameEntity
import tkinter as tk

class MXLabel(GameEntity):
    def __init__(self, master, x, y, text = "X"):
        self.text = text
        self.text_id = None
        self.x = x
        self.y = y
        self.x_font = ("Arial", 36, "bold")
        self.x_color = "#32FD32"

    def draw(self, canvas: tk.Canvas):
        if self.text_id is not None: canvas.delete(self.text_id)
        self.text_id = canvas.create_text(self.x, self.y, text=self.text, fill=self.x_color, font=self.x_font)

    def think(self):
        pass