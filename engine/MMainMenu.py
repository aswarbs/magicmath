from GameEntity import GameEntity
import tkinter as tk
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from MTimeIntro import MTimeIntro
from PIL import Image, ImageTk

class MMainMenu(GameEntity):
    def __init__(self, master):
        self.text_id = None
        self.rect_id = None
        self.title_id = None
        self.dead = False
        self.x = 0  # x will be set dynamically for centering
        self.y = 0  # y will be set dynamically for centering
        self.width = 150  # width of the door
        self.height = 280  # height of the door

        # Bind the keys to functions when the menu is created
        self.master = master
        self.master.master.bind("<KeyPress-n>", self.on_key_press_1)  # Bind key "n"
        self.master.master.bind("<KeyPress-m>", self.on_key_press_2)  # Bind key "m"

    def draw(self, canvas: tk.Canvas):

        if self.dead:
            return

        # Remove any previous items
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

        # Draw title
        self.title_id = canvas.create_text(canvas_width / 2, canvas_height / 3,
                                           text="Mathquest", font=("Avenir Next", 36, "bold"), fill="black")

        # Draw instruction text
        self.rect_id = canvas.create_text(canvas_width / 2, canvas_height / 2,
                                          text="Draw a 1 to enter freemode, or a 2 to enter story.",
                                          font=("CMU Serif Roman", 22), fill="black")

    def think(self):
        pass

    def delete(self):
        # Remove any previous items
        if self.text_id is not None:
            self.master.canvas.delete(self.text_id)
        if self.title_id is not None:
            self.master.canvas.delete(self.title_id)
        if self.rect_id is not None:
            self.master.canvas.delete(self.rect_id)
        self.dead = True

        self.master.master.unbind("<KeyPress-n>")  # Bind key "n"
        self.master.master.unbind("<KeyPress-m>")  # Bind key "m"

    # Function for when key "1" is pressed
    def on_key_press_1(self, event):
        print("Key 1 pressed! Entering freemode...")
        self.delete()
        self.master.entities.append(MTimeIntro(self.master, "2024", "Cario"))
        # Here you can implement logic for freemode entry

    # Function for when key "2" is pressed
    def on_key_press_2(self, event):
        print("Key 2 pressed! Entering story mode...")
        self.delete()
        # Here you can implement logic for story mode entry
