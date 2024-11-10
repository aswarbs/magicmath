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
from problemgen.generate_problem import program_answer, get_answer

class ProjectorWindow():
    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Mathquest")
        self.screen_width = 640
        self.screen_height = 480
        self.entities = []

        # Set window size to 640x480 (4:3 ratio)
        #self.master.geometry("640x480")
        
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
        

        # Set background to white
        self.master.configure(bg="white")

        self.setup()

        # Display the X labels
        self.display_content()

        # Initialize CameraCalibrator and fetch corners
        self.camera_calibrator = CameraCalibrator()

        # Create a lock for thread synchronization
        self.lock = threading.Lock()

        # Start a thread to detect corners once after the UI is displayed
        self.corners = None
        self.calibration_thread = threading.Thread(target=self.fetch_corners, daemon=True)
        self.calibration_thread.start()

        # Start a thread to draw the center point
        self.draw_thread = threading.Thread(target=self.draw_center, daemon=True)
        self.draw_thread.start()

    

    def save_tkinter_background(self):

        # Save the Tkinter canvas content to a PostScript file
        self.canvas.postscript(file="projection.ps", colormode='color')

        # Open the PostScript file, convert it to PNG format, and save
        img = Image.open("projection.ps")
        img = img.resize((640,480))

        img.save("projection.png", "png")
        
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
            kernel = np.ones((10, 10), np.uint8)  # 5x5 kernel for dilation
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


    def display_content(self):
        # Red X font and color


        # Create labels for each corner
        #self.label_tl = tk.Label(self.canvas, text="X", font=x_font, fg=x_color, bg="white")
        # Offset value (change this value to move labels farther or closer)
        offset = 0

        # Create labels with offset from each corner
        self.label_tl = MXLabel(self.canvas, self.screen_corners[0][0] + offset, self.screen_corners[0][1] + offset)
        self.label_tr = MXLabel(self.canvas, self.screen_corners[1][0] - offset, self.screen_corners[1][1] + offset)
        self.label_bl = MXLabel(self.canvas, self.screen_corners[2][0] + offset, self.screen_corners[2][1] - offset)
        self.label_br = MXLabel(self.canvas, self.screen_corners[3][0] - offset, self.screen_corners[3][1] - offset)
        self.entities.extend([self.label_tl, self.label_tr, self.label_br, self.label_bl])

        self.center_label = MXLabel(self.canvas, -10, -10, colour="red")
        self.entities.append(self.center_label)
        
        #self.master.update_idletasks()


    def flush(self):
        pass

    def draw_center(self):

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
            self.center_label.x = center_screen[0]
            self.center_label.y = center_screen[1]

            
            mask = self.save_foreground_mask()

            if mask is not None:
                equations_with_positions = process_equations(mask)
                if equations_with_positions is not None:
                    answers = []
                    for e in equations_with_positions:
                        answer = None
                        try:
                            answer = program_answer(e[0])
                        except:
                            try:
                                answer = get_answer(e[0])
                            except:
                                pass
                        answers.append(answer)
                        
                        if answer is not None:
                            # draw the answer to the right of the question
                            answer_position = (e[1][0], e[1][1])
                            answer_position = (answer_position[0] + 10, answer_position[1])
                            print(f"answer position: {answer_position}")
                            answer_label = MXLabel(self.canvas, *answer_position, text=answer, colour="red")
                            self.entities.append(answer_label)

                    print(f"equations: {[e for e in equations_with_positions]}\nanswers: {answers}") 

    def mainloop(self):
        # Run the main event loop
        #print(f"Entities: {self.entities}")
        _ = [e.draw(self.canvas) for e in self.entities]
        _ = [e.think() for e in self.entities]
        self.save_tkinter_background()

                        
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
