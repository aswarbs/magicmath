import tkinter as tk
import threading
import time
import numpy as np
import cv2
from computer_vision.detect_corners import CameraCalibrator

class CalibrationScreen:

    def __init__(self, parent, master):
        self.parent = parent
        self.master = master

        self.screen_corners = [
            (0, 0),  # Top-left corner
            (0, 0),  # Top-right corner (to be updated later)
            (0, 0),  # Bottom-left corner (to be updated later)
            (0, 0)   # Bottom-right corner (to be updated later)
        ]
        self.image_corners = [
            (0, 0),  # Top-left corner
            (0, 0),  # Top-right corner (to be updated later)
            (0, 0),  # Bottom-left corner (to be updated later)
            (0, 0)   # Bottom-right corner (to be updated later)
        ]
        

        # Set background to white
        self.master.configure(bg="white")

        # Display the X labels
        #self.display_content()

        # Reposition the labels on window resize or display
        self.master.bind("<Configure>", self.update_corner_labels)

        # Initialize CameraCalibrator and fetch corners
        self.camera_calibrator = CameraCalibrator(camera_index=1)

        # Create a lock for thread synchronization
        self.lock = threading.Lock()

        # Start a thread to detect corners once after the UI is displayed
        self.corners = None
        self.calibration_thread = threading.Thread(target=self.fetch_corners, daemon=True)
        self.calibration_thread.start()

        # Start a thread to draw the center point
        #self.draw_thread = threading.Thread(target=self.draw_center, daemon=True)
        #self.draw_thread.start()

        self.completion_thread = threading.Thread(target=self.complete_formula, daemon=True)
        self.completion_thread.start()

    def display_content(self):
        # Red X font and color
        x_font = ("Arial", 36, "bold")
        x_color = "#32FD32"

        # Create labels for each corner
        self.label_tl = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_tr = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_bl = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")
        self.label_br = tk.Label(self.parent, text="X", font=x_font, fg=x_color, bg="white")

        self.label_tl.place(x=self.screen_corners[0][0], y=self.screen_corners[0][1], anchor="nw")

        # Trigger positioning for other corners
        self.update_corner_labels()

    def complete_formula(self):
        while 1:
            formula = self.camera_calibrator.get_formula(self.corners)
            print(f"formula: {formula}")
            time.sleep(1)
    
    def update_corner_labels(self, event=None):
        # Update the screen corners after window resize
        self.screen_corners = [
            (0, 0),  # Top-left corner
            (self.master.winfo_width(), 0),  # Top-right corner
            (0, self.master.winfo_height()),  # Bottom-left corner
            (self.master.winfo_width(), self.master.winfo_height())  # Bottom-right corner
        ]

        # Place labels at each corner
        self.label_tr.place(x=self.screen_corners[1][0], y=self.screen_corners[1][1], anchor="ne")
        self.label_bl.place(x=self.screen_corners[2][0], y=self.screen_corners[2][1], anchor="sw")
        self.label_br.place(x=self.screen_corners[3][0], y=self.screen_corners[3][1], anchor="se")


    def draw_center(self):
        # to test projection
        # draw to the center of the tkinter canvas using only camera corners
        x_font = ("Arial", 36, "bold")
        self.center_label = tk.Label(self.parent, text="X", fg="red", bg="white", font=x_font)

        while True:
            time.sleep(1)

            if not self.corners:
                continue

            # Get the real-world corners (top-left, top-right, bottom-left, bottom-right)
            real_points = np.array(self.corners, dtype=np.float32)

            # Calculate the center of the real-world quadrilateral formed by the corners
            center_real = np.mean(real_points, axis=0)

            # Convert real-world coordinates to screen coordinates
            center_screen = self.real_to_screen(center_real)

            if center_screen is None:
                continue

            # If the center screen coordinates are out of bounds, skip placing the label
            if center_screen[0] < 0 or center_screen[1] < 0:
                continue

            # Place the label at the center screen position
            self.center_label.place(x=center_screen[0], y=center_screen[1], anchor=tk.CENTER)


    def fetch_corners(self):
        while True:
            # Capture a single frame to detect corners
            detected_corners = self.camera_calibrator.detect_corners()

            # Use a lock to safely update corners data
            with self.lock:
                self.corners = detected_corners

            time.sleep(1)

    def real_to_screen(self, real_point):
        """
        Convert real-world coordinates (real_point) to screen coordinates.
        Assumes that self.corners and screen_corners are available.
        """
        if self.corners is None:
            return None

        # Synchronize access to self.corners
        with self.lock:
            real_points = np.array(self.corners, dtype=np.float32)

        # Define the screen corners (top-left, top-right, bottom-left, bottom-right)
        screen_corners = [
            (0, 0),  # Top-left corner
            (self.master.winfo_width(), 0),  # Top-right corner
            (0, self.master.winfo_height()),  # Bottom-left corner
            (self.master.winfo_width(), self.master.winfo_height())  # Bottom-right corner
        ]

        # Convert corners to numpy arrays for OpenCV
        screen_points = np.array(screen_corners, dtype=np.float32)

        # Calculate the homography matrix using OpenCV
        homography_matrix, _ = cv2.findHomography(real_points, screen_points)

        # Convert the real-world point to screen coordinates using the homography matrix
        real_point = np.array([real_point], dtype=np.float32)
        screen_point = cv2.perspectiveTransform(real_point[None, :, :], homography_matrix)

        # Ensure the point is within the bounds of the screen
        screen_x, screen_y = screen_point[0][0]

        #print(f"real point: {real_point} screen point: ({screen_x}, {screen_y})")

        return (screen_x, screen_y)
