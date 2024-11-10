from GameEntity import GameEntity
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageTk

class MDoor(GameEntity):
    def __init__(self, master, texlabel="Label"):
        self.text = texlabel
        self.text_id = None
        self.rect_id = None
        self.title_id = None

        self.x = 0  # x will be set dynamically for centering
        self.y = 0  # y will be set dynamically for centering
        self.width = 150  # width of the door
        self.height = 280  # height of the door

    def render_tex(self):
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

    def draw(self, canvas: tk.Canvas):

        # Draw the text
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

        # Render LaTeX text to an image
        image = self.render_tex()

        # Convert the PIL image to a format Tkinter understands
        photo = ImageTk.PhotoImage(image)

        # If there's a previous image, remove it
        if self.text_id is not None:
            canvas.delete(self.text_id)

        self.title_id = canvas.create_text(canvas_width / 2, canvas_height / 8,
                                           text="Solve this to pass.", font=("CMU Serif Roman", 22), fill="black")

        # Draw the image on the canvas
        self.text_id = canvas.create_image(self.x, self.y, image=photo)
        canvas.image = photo  # Keep a reference to avoid garbage collection

        # Draw the door (rectangle)
        self.rect_id = canvas.create_rectangle(self.x - self.width / 2, self.y - self.height / 2,
                                               self.x + self.width / 2, self.y + self.height / 2,
                                               outline="black", width=5)  # Set the outline width to 5

    def think(self):
        pass
