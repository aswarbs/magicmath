import tkinter as tk
import threading
import time
import numpy as np
import cv2
from computer_vision.detect_corners import CameraCalibrator
from engine.MXLabel import MXLabel
import ctypes.wintypes

class ProjectorWindow():
    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Mathquest")
        self.screen_width = 800
        self.screen_height = 600
        self.entities = []

        # Set window size to 640x480 (4:3 ratio)
        #self.master.geometry("640x480")
        
        self.canvas = tk.Canvas(self.master, bg="white", width=self.screen_width, height=self.screen_height)
        self.canvas.pack(fill="both", expand=True)

        self.screen_corners = [
            (0, 0),  # Top-left corner
            (self.screen_width, 0),  # Top-right corner
            (0, self.screen_height),  # Bottom-left corner
            (self.screen_width, self.screen_height)  # Bottom-right corner
        ]

        self.image_corners = [
            (0, 0),  # Top-left corner
            (0, 0),  # Top-right corner (to be updated later)
            (0, 0),  # Bottom-left corner (to be updated later)
            (0, 0)   # Bottom-right corner (to be updated later)
        ]
        

        # Set background to white
        self.master.configure(bg="white")

        self.setup()

        # Display the X labels
        self.display_content()

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

    # Get monitor information
    def get_monitors_info(self):
        user32 = ctypes.windll.user32
        def _get_monitors_resolution():
            monitors = []
            monitor_enum_proc = ctypes.WINFUNCTYPE(
                ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double)
            def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                monitors.append((lprcMonitor.contents.left, lprcMonitor.contents.top,
                                lprcMonitor.contents.right - lprcMonitor.contents.left,
                                lprcMonitor.contents.bottom - lprcMonitor.contents.top))
                return 1
            user32.EnumDisplayMonitors(None, None, monitor_enum_proc(callback), 0)
            return monitors
        monitors = _get_monitors_resolution()
        return monitors

    def setup(self):
        monitors = self.get_monitors_info()
        if len(monitors) >= 2:
            x1, y1, w1, h1 = monitors[1]
            self.master.geometry("%dx%d+%d+%d" % (w1, h1, x1, y1))
            self.master.overrideredirect(1)
        else:
            w1, h1 = monitors[0][2], monitors[0][3]
            self.master.geometry("%dx%d+0+0" % (w1, h1))
            self.master.overrideredirect(1)

        



    def display_content(self):
        # Red X font and color


        # Create labels for each corner
        #self.label_tl = tk.Label(self.canvas, text="X", font=x_font, fg=x_color, bg="white")
        # Offset value (change this value to move labels farther or closer)
        offset = 20

        # Create labels with offset from each corner
        self.label_tl = MXLabel(self.canvas, self.screen_corners[0][0] + offset, self.screen_corners[0][1] + offset)
        self.label_tr = MXLabel(self.canvas, self.screen_corners[1][0] - offset, self.screen_corners[1][1] + offset)
        self.label_bl = MXLabel(self.canvas, self.screen_corners[2][0] + offset, self.screen_corners[2][1] - offset)
        self.label_br = MXLabel(self.canvas, self.screen_corners[3][0] - offset, self.screen_corners[3][1] - offset)
        self.entities.extend([self.label_tl, self.label_tr, self.label_br, self.label_bl])
        
        #self.master.update_idletasks()

    def complete_formula(self):
        while 1:
            formula = self.camera_calibrator.get_formula(self.corners)
            print(f"formula: {formula}")
            time.sleep(1)
    


    def draw_center(self):
        # to test projection
        # draw to the center of the tkinter canvas using only camera corners
        x_font = ("Arial", 36, "bold")
        self.center_label = tk.Label(self.canvas, text="X", fg="red", bg="white", font=x_font)

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



        

    def mainloop(self):
        # Run the main event loop
        _ = [e.draw(self.canvas) for e in self.entities]
        _ = [e.think() for e in self.entities]
        self.master.update()

    
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
            (self.screen_width, 0),  # Top-right corner
            (0, self.screen_height),  # Bottom-left corner
            (self.screen_width, self.screen_height)  # Bottom-right corner
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
