import threading
import pyttsx3
from GameEntity import GameEntity
from GenAI.ProfileGen import Profile
from PIL import Image, ImageTk
import tkinter as tk

MPROFILE_OFFSET = 8
SPEECH_DURATION = 8000  # The duration the speech text will be shown

class MProfile(GameEntity):
    def __init__(self, master, p: Profile):
        self.master = master
        self.p = p
        self.name = p.name
        self.image_path = p.image_path  # Assuming Profile has an image_path attribute
        self.text_id = None
        self.speech_id = None
        self.image_id = None  # To keep track of the image
        self.x = 64
        self.y = 64
        self.image = Image.open(self.p.image_path)

        self.speech = ""
        self.is_speaking = False

        # Resize the image to 64x64
        self.image = self.image.resize((64, 64))

        # Convert to a format that Tkinter can use
        self.image = ImageTk.PhotoImage(self.image)

        # Initialize the pyttsx3 TTS engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Set the speech rate (optional)
        self.tts_engine.setProperty('volume', 1)  # Set volume level (optional)

    def draw(self, canvas: tk.Canvas):
        # If there's already text, delete it
        if self.text_id is not None:
            canvas.delete(self.text_id)

        if self.speech_id is not None:
            canvas.delete(self.speech_id)

        # If there's an image, delete it
        if self.image_id is not None:
            canvas.delete(self.image_id)

        # Draw the image (adjust size as necessary)
        self.image_id = canvas.create_image(self.x, self.y, image=self.image)

        # Draw the text below the image with smaller, bold, Times New Roman font size 12
        self.text_id = canvas.create_text(
            self.x,
            self.y + 32 + MPROFILE_OFFSET,
            text=self.name,
            fill="black",
            font=("Times New Roman", 14, "bold")
        )

        if self.is_speaking:
            self.speech_id = canvas.create_text(
                self.x + 32 + MPROFILE_OFFSET,
                self.y,
                text=self.speech,
                fill="black",
                font=("Times New Roman", 14),
                anchor="w"
            )

    def speak(self, text: str):
        # Set the speech to the given text
        self.speech = text
        self.is_speaking = True

        # Run the TTS engine in a separate thread to avoid blocking the main thread
        tts_thread = threading.Thread(target=self._speak_in_background)
        tts_thread.start()

        # Schedule stopping the speech after the set duration
        self.master.after(SPEECH_DURATION, lambda: self.stop_speaking())

    def _speak_in_background(self):
        # Speak the text using TTS in the background (separate thread)
        self.tts_engine.say(self.speech)
        self.tts_engine.runAndWait()

    def stop_speaking(self):
        self.speech = ""
        self.is_speaking = False

    def think(self):
        pass

    def stop_speaking(self):
        self.speech = ""
        self.is_speaking = False

    def think(self):
        pass
