import cv2
import numpy as np

class CameraCalibrator:
    def __init__(self, camera_index=0):
        
        self.default_corners = [(75, 319), (506, 317), (485, 43), (94, 37)]

        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        
        # Define lower and upper bounds for lime green in HSV
        self.lower_green = np.array([40, 100, 100])  # Lower bound for lime green
        self.upper_green = np.array([80, 255, 255])  # Upper bound for lime green
        
        # Set minimum and maximum area to filter noise and small contours
        self.min_area = 1
        self.max_area = 5000

    def detect_corners(self):
        # Capture a single frame from the camera
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return []

        # Convert the frame to HSV color space for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance contrast
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        # Create a mask to detect lime green
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # List to store the positions of detected lime green objects
        detected_x_positions = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if self.min_area < area < self.max_area:
                # Get the bounding box of each contour
                x, y, w, h = cv2.boundingRect(cnt)

                # Calculate center of the contour
                center_x, center_y = x + w // 2, y + h // 2
                detected_x_positions.append((center_x, center_y))

                # Optional: Draw bounding box, center circle, and text
                cv2.rectangle(enhanced_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(enhanced_frame, (center_x, center_y), 5, (255, 0, 0), -1)
                cv2.putText(enhanced_frame, f"X at ({center_x}, {center_y})", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw all contours on the frame
        cv2.drawContours(enhanced_frame, contours, -1, (0, 255, 255), 1)  # Yellow contours for visibility

        # Display the frame with detections (optional)
        cv2.imshow("Lime Green Detection", enhanced_frame)
        cv2.waitKey(1)

        if len(detected_x_positions) == 4:
            return detected_x_positions
        else:
            return self.default_corners


    def release_camera(self):
        # Release the camera and close all OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()
