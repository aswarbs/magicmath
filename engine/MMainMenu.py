from GameEntity import GameEntity
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageTk

class MMainMenu(GameEntity):
    def __init__(self, master):
        self.text_id = None
        self.rect_id = None
        self.title_id = None

        self.x = 0  # x will be set dynamically for centering
        self.y = 0  # y will be set dynamically for centering
        self.width = 150  # width of the door
        self.height = 280  # height of the door

    def draw(self, canvas: tk.Canvas):

        if self.text_id is not None:
            canvas.delete(self.text_id)

        if self.title_id is not None:
            canvas.delete(self.title_id)

        if self.rect_id is not None:
            canvas.delete(self.rect_id)

        # Get canvas width and height
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Calculate the position for the door to be centered
        self.x = canvas_width / 4
        self.y = canvas_height / 2

        # If there's a previous image, remove it
        if self.text_id is not None:
            canvas.delete(self.text_id)

        self.title_id = canvas.create_text(canvas_width / 2, canvas_height / 6,
                                           text="Mathquest", font=("Avenir Next", 26, "bold"), fill="black")

        # Draw the door (rectangle)
        self.rect_id = canvas.create_text(canvas_width / 2, canvas_height / 4,
                                          text = "Draw a 1 to enter freemode, or a 2 to enter story.",
                                          font=("CMU Serif Roman", 22), fill="black")

    def think(self):
        pass
