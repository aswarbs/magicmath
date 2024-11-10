from engine.GameEntity import GameEntity
import tkinter as tk

class MLabel(GameEntity):
    def __init__(self, master, text = "Label"):

        self.text = text
        self.text_id = None
        self.x = 0
        self.y = 100

    def draw(self, canvas: tk.Canvas):
        if self.text_id is not None: canvas.delete(self.text_id)
        self.text_id = canvas.create_text(self.x, self.y, text=self.text, fill="black")

    def think(self):
        pass
