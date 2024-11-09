import tkinter as tk
import threading
import time
from computer_vision.detect_corners import CameraCalibrator

class CalibrationScreen:

    def __init__(self, parent, master):
        self.parent = parent
        self.master = master

        # Set background to white
        self.master.configure(bg="white")

        # Display the X labels
        self.display_content()

        # Reposition the labels on window resize or display
        self.master.bind("<Configure>", self.update_corner_labels)

        # Initialize CameraCalibrator and fetch corners
        self.camera_calibrator = CameraCalibrator(camera_index=1)

        # Start a thread to detect corners once after the UI is displayed
        self.corners = None
        self.calibration_thread = threading.Thread(target=self.fetch_corners, daemon=True)
        self.calibration_thread.start()

    def display_content(self):
        # Red X font and color
        x_font = ("Arial", 36, "bold")
        x_color = "#32CD32"

        # Create labels for each corner
        self.label_tl = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_tr = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_bl = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_br = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")

        # Initial placement
        self.label_tl.place(x=3, y=1, anchor="nw")

        # Trigger positioning for other corners
        self.update_corner_labels()

    def update_corner_labels(self, event=None):
        # Get the current width and height of the master window
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        # Place labels at each corner
        self.label_tr.place(x=width - 3, y=1, anchor="ne")
        self.label_bl.place(x=3, y=height - 1, anchor="sw")
        self.label_br.place(x=width - 3, y=height - 1, anchor="se")

    def fetch_corners(self):
        while 1:
            # Capture a single frame to detect corners
            self.corners = self.camera_calibrator.detect_corners()

            # Once detected, you can use self.corners in other parts of your program

            # Optional: Close the calibrator or continue with further operations
            # self.camera_calibrator.release_camera()
            time.sleep(0.1)
