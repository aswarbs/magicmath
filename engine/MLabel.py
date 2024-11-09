from GameEntity import GameEntity
import tkinter as tk

class MLabel(GameEntity):
    def __init__(self, text = "Label"):
        self.text = text

    def draw(self, canvas: tk.Canvas):
        canvas.create_text(50, 50, text = self.text, fill = "black")
