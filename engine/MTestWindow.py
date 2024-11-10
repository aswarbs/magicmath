import tkinter as tk
import threading
import time
import numpy as np
import cv2
from computer_vision.detect_corners import CameraCalibrator
from engine.MXLabel import MXLabel
import ctypes.wintypes
from PIL import Image
from preprocessing.preprocessing import process_equations
from engine.GameEntity import GameEntity
import random

class TestWindow(GameEntity):
    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Mathquest - Times Tables")
        self.screen_width = 640
        self.screen_height = 480
        self.entities = []
        self.canvas = tk.Canvas(self.master, bg="white", width=self.screen_width, height=self.screen_height)
        self.canvas.pack()

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
        
        
        # Other initializations
        self.current_problem = None  # Store the current multiplication problem
        self.problem_label = None    # Label to display the problem

        self.setup()
        self.display_content()
        
        self.camera_calibrator = CameraCalibrator()
        self.lock = threading.Lock()
        self.corners = None
        self.calibration_thread = threading.Thread(target=self.fetch_corners, daemon=True)
        self.calibration_thread.start()
        self.draw_thread = threading.Thread(target=self.draw_center, daemon=True)
        self.draw_thread.start()
        
        # Display initial multiplication problem
        self.generate_problem()

    def fetch_corners(self):
        while True:
            # Capture a single frame to detect corners
            detected_corners = self.camera_calibrator.detect_corners()

            # Use a lock to safely update corners data
            with self.lock:
                self.corners = detected_corners

            time.sleep(1)

    def save_tkinter_background(self):
        try:


            with self.lock:
                    
                # Save the Tkinter canvas content to a PostScript file
                self.canvas.postscript(file="projection.ps", colormode='color')

                # Open the PostScript file, convert it to PNG format, and save
                img = Image.open("projection.ps")
                img = img.resize((640,480))
                img.save("projection.png", "png")
        except:
            pass
        

    def mainloop(self):
        # Run the main event loop
        #print(f"Entities: {self.entities}")
        _ = [e.draw(self.canvas) for e in self.entities]
        _ = [e.think() for e in self.entities]
        
        self.save_tkinter_background()

                        
        self.master.update()


    def display_content(self):
        # Red X font and color


        # Create labels for each corner
        #self.label_tl = tk.Label(self.canvas, text="X", font=x_font, fg=x_color, bg="white")
        # Offset value (change this value to move labels farther or closer)
        offset = 0

        # Create labels with offset from each corner
        self.label_tl = MXLabel(self, self.screen_corners[0][0] + offset, self.screen_corners[0][1] + offset)
        self.label_tr = MXLabel(self, self.screen_corners[1][0] - offset, self.screen_corners[1][1] + offset)
        self.label_bl = MXLabel(self, self.screen_corners[2][0] + offset, self.screen_corners[2][1] - offset)
        self.label_br = MXLabel(self, self.screen_corners[3][0] - offset, self.screen_corners[3][1] - offset)
        self.entities.extend([self.label_tl, self.label_tr, self.label_br, self.label_bl])

        self.center_label = MXLabel(self, -10, -10, colour="red")
        self.entities.append(self.center_label)
        
        #self.master.update_idletasks()

    def generate_problem(self):
        """Generates a new multiplication problem and displays it."""
        # Randomly choose two numbers for multiplication
        num1 = random.randint(1, 12)
        num2 = random.randint(1, 12)
        self.current_problem = (num1, num2)
        problem_text = f"{num1} x {num2} = ?"

        # Display the new problem on the canvas
        if self.problem_label:
            self.problem_label.delete()  # Remove the old problem
        self.problem_label = MXLabel(self, 320, 50, text=problem_text, colour="blue")
        self.problem_label.tag = "PROBLEM"
        self.entities.append(self.problem_label)

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
        print(monitors)
        #exit()
        return monitors

    def setup(self):
        monitors = self.get_monitors_info()
        if len(monitors) >= 2:
            x1, y1, w1, h1 = monitors[1]
            x1, y1, w1, h1 = (1536, 0, 640, 480) # trying to fix monitor issues
            self.master.geometry("%dx%d+%d+%d" % (w1, h1, x1, y1))
            self.master.overrideredirect(1)
        else:
            w1, h1 = monitors[0][2], monitors[0][3]
            self.master.geometry("%dx%d+0+0" % (w1, h1))
            self.master.overrideredirect(1)



    def check_answer(self, user_answer):
        """Check if the user's answer is correct."""
        correct_answer = self.current_problem[0] * self.current_problem[1]
        print(f"user answer: {user_answer} correct answer: {correct_answer}")
        return str(correct_answer) in str(user_answer)

    def save_foreground_mask(self):
        """
        Isolate and save the mask of new drawings on the whiteboard using warpPerspective.
        Also save an overlay of the registration on the background, excluding non-white areas from Tkinter.
        """
        # Synchronize access to frame and corner data
        with self.lock:
            frame = self.camera_calibrator.frame
            corners = self.corners

        # Ensure corners have been set up and frame is captured
        if corners is None or frame is None:
            return None

        try:
            with self.lock:
                # Read the background image in grayscale (projection-only baseline)
                background = cv2.imread('projection.png', cv2.IMREAD_GRAYSCALE)

            # Convert the current frame to grayscale
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Convert the real-world corners and screen corners to numpy arrays
            real_points = np.array(corners, dtype=np.float32).reshape(-1, 1, 2)
            screen_points = np.array(self.screen_corners, dtype=np.float32).reshape(-1, 1, 2)

            # Calculate the homography matrix using OpenCV
            homography_matrix, _ = cv2.findHomography(real_points, screen_points)

            # Use warpPerspective to align the current frame (ensuring it's the same size as the background)
            aligned_frame = cv2.warpPerspective(frame_gray, homography_matrix, (background.shape[1], background.shape[0]))

            # Create a mask to ignore non-white areas in the background
            _, background_white_mask = cv2.threshold(background, 250, 255, cv2.THRESH_BINARY)

            # Dilate the background mask to make the white areas bigger
            kernel = np.ones((15, 15), np.uint8)  # 5x5 kernel for dilation
            dilated_background_mask = cv2.erode(background_white_mask, kernel, iterations=2)

            # Invert the dilated background mask to get non-white areas as "black"
            inverted_background_mask = cv2.bitwise_not(dilated_background_mask)

            # Apply the inverted mask on aligned_frame to extract new drawings (make black areas white)
            foreground_mask = cv2.bitwise_or(aligned_frame, inverted_background_mask)

            # Save the intermediate images for inspection
            cv2.imwrite("background_white_mask.png", background_white_mask)
            cv2.imwrite("dilated_background_mask.png", dilated_background_mask)
            cv2.imwrite("aligned_frame.png", aligned_frame)
            cv2.imwrite("foreground_mask.png", foreground_mask)

            # Overlay the aligned frame onto the background (to visualize registration)
            overlay = cv2.addWeighted(background, 0.7, aligned_frame, 0.3, 0)

            # Save the overlay image
            cv2.imwrite('overlay.png', overlay)
            return foreground_mask  # Return the foreground mask for further processing
        except:
            return None
        
    def draw_center(self):
        while True:
            time.sleep(1)
            if not self.corners:
                continue
            real_points = np.array(self.corners, dtype=np.float32)
            center_real = np.mean(real_points, axis=0)
            center_screen = self.real_to_screen(center_real)
            if center_screen is None or center_screen[0] < 0 or center_screen[1] < 0:
                continue
            self.center_label.x = center_screen[0]
            self.center_label.y = center_screen[1]
            mask = self.save_foreground_mask()
            if mask is not None:
                equations_with_positions = process_equations(mask)
                for _e in self.entities:
                    if _e.tag == "ANSWER":
                        _e.delete()
                if equations_with_positions is not None:
                    answers = []
                    for e in equations_with_positions:
                        print(f"e is {e}")
                        user_answer = e[0]
                        if self.check_answer(user_answer):
                            self.generate_problem()  # New problem on correct answer
                            print("Correct answer! Generating new problem.")
                        else:
                            print("Incorrect, try again.")

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


        # Convert corners to numpy arrays for OpenCV
        screen_points = np.array(self.screen_corners, dtype=np.float32)

        # Calculate the homography matrix using OpenCV
        homography_matrix, _ = cv2.findHomography(real_points, screen_points)

        # Convert the real-world point to screen coordinates using the homography matrix
        real_point = np.array([real_point], dtype=np.float32)
        screen_point = cv2.perspectiveTransform(real_point[None, :, :], homography_matrix)

        # Ensure the point is within the bounds of the screen
        screen_x, screen_y = screen_point[0][0]

        return (screen_x, screen_y)
 