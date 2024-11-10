from engine.GameEntity import GameEntity
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageTk

class MTexLabel(GameEntity):
    def __init__(self, text, x, y):
        self.text = round(text,3)
        self.text_id = None
        self.x = x
        self.y = y
        self.x_font = ("Arial", 36, "bold")

    def render_tex(self):
        try:
            # Create a Matplotlib figure to render LaTeX
            fig, ax = plt.subplots(figsize=(5, 1))  # Adjust size as needed
            # Explicitly set text color to black
            ax.text(0.5, 0.5, f'${self.text}$', size=20, ha="center", va="center", color='black')
            ax.axis('off')  # Hide the axes

            # Save the figure to a PIL image
            fig.canvas.draw()
            width, height = fig.canvas.get_width_height()
            image = Image.frombytes('RGB', (width, height), fig.canvas.tostring_rgb())
            plt.close(fig)
            return image
        except:
            return None

    def draw(self, canvas: tk.Canvas):
        # Render LaTeX text to an image
        image = self.render_tex()
        if image is None: return

        # Convert the PIL image to a format Tkinter understands
        photo = ImageTk.PhotoImage(image)

        # If there's a previous image, remove it
        #if self.text_id is not None:
        #    canvas.delete(self.text_id)

        # Draw the image on the canvas
        self.text_id = canvas.create_image(self.x, self.y, image=photo)
        canvas.image = photo  # Keep a reference to avoid garbage collection

    def think(self):
        pass
