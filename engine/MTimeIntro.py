from engine.GameEntity import GameEntity
import tkinter as tk
from datetime import datetime, timedelta
from engine.MCharacterDialogue import MCharacterDialogue

class MTimeIntro(GameEntity):
    def __init__(self, master, year: str, location: str):
        self.master = master
        self.year = year
        self.location = location
        self.text_id = None
        self.rect_id = None
        self.title_id = None
        self.dead = False

        self.x = 0  # x will be set dynamically for centering
        self.y = 0  # y will be set dynamically for centering
        self.width = 150  # width of the door
        self.height = 280  # height of the door

        # Start time for the fade effect
        self.start_time = datetime.now()
        # Target duration for fade-in (e.g., 1 second)
        self.fade_duration = timedelta(seconds=2)
        self.exit_duration = timedelta(seconds=4)

    def delete(self):
        if self.text_id is not None:
            self.master.canvas.delete(self.text_id)
        if self.title_id is not None:
            self.master.canvas.delete(self.title_id)
        if self.rect_id is not None: self.master.canvas.delete(self.rect_id)
        self.dead = True

    def draw(self, canvas: tk.Canvas):
        if self.dead:
            return

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

        # Draw the title text (location)
        self.title_id = canvas.create_text(canvas_width / 2, (canvas_height / 2) - 25,
                                           text=f"{self.location}", font=("CMU Serif Roman", 28, "bold"), fill="black")

        # Draw the year text (rectangle)
        self.rect_id = canvas.create_text(canvas_width / 2, (canvas_height / 2) + 30 - 25,
                                          text=f"{self.year}", font=("CMU Serif Roman", 22), fill="black")

        # Update the opacity based on the current time
        self.update_opacity(canvas)

    def update_opacity(self, canvas: tk.Canvas):
        """Update the opacity based on the time elapsed since the start."""
        # Calculate elapsed time
        elapsed_time = datetime.now() - self.start_time
        elapsed_time2 = datetime.now() - self.start_time
        # Clamp elapsed time to be within 0 and fade_duration
        if elapsed_time > self.fade_duration:
            elapsed_time = self.fade_duration

        if elapsed_time2 > self.exit_duration:
            print("TimeIntro DIED!")
            self.master.entities.append(MCharacterDialogue(self.master))
            self.delete()

        # Calculate opacity as a value between 0 and 255 based on elapsed time
        opacity = 255 - int(255 * (elapsed_time / self.fade_duration))
        opacity_hex = f'#{opacity:02x}{opacity:02x}{opacity:02x}'  # Convert to hex
        print(opacity)

        # Update the text opacity by changing the fill color
        canvas.itemconfig(self.title_id, fill=opacity_hex)
        canvas.itemconfig(self.rect_id, fill=opacity_hex)

    def think(self):
        pass
