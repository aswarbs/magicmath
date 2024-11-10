from GameEntity import GameEntity
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageTk

class MCharacterDialogue(GameEntity):
    def __init__(self, master,
                 text = "Congratulations on solving that riddle!",
                 solve = ""):
        self.text = text
        self.solve = solve
        self.text_id = None

    def render_tex(self):
        # Create a Matplotlib figure to render LaTeX

        fig, ax = plt.subplots(figsize=(5, 1))  # Adjust size as needed
        # Explicitly set text color to black
        ax.text(0.5, 0.5, f'${self.solve}$', size=20, ha="center", va="center", color='black')
        ax.axis('off')  # Hide the axes

        # Save the figure to a PIL image
        fig.canvas.draw()
        width, height = fig.canvas.get_width_height()
        image = Image.frombytes('RGB', (width, height), fig.canvas.tostring_rgb())
        plt.close(fig)
        return image


    def draw(self, canvas: tk.Canvas):
        # Get canvas width and height
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Calculate the position for the door to be centered
        self.x = canvas_width / 2
        self.y = canvas_height / 10
        self.ymid = canvas_height / 3

        if self.text_id is not None: canvas.delete(self.text_id)
        self.text_id = canvas.create_text(
            self.x,
            self.y,
            text=self.text,
            font=("CMU Serif Roman", 18, "bold"),
            fill="black",
            width=((canvas_width) / 5) * 4  # Specify the width for text wrapping
        )

        # Render LaTeX text to an image
        image = self.render_tex()

        # Convert the PIL image to a format Tkinter understands
        photo = ImageTk.PhotoImage(image)

        # Draw the image on the canvas
        self.text_id = canvas.create_image(self.x, self.ymid, image=photo)
        canvas.image = photo  # Keep a reference to avoid garbage collection

    def think(self):
        pass
