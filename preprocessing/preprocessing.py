import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from preprocessing.openaiapi import *

# Function to adjust brightness and contrast of the image
def adjust_brightness_contrast(img, brightness=0, contrast=0):
    # Adjusting brightness and contrast
    # We use the formula: new_pixel = alpha * (pixel - 128) + 128 + beta
    # Where 'alpha' is a scaling factor (contrast) and 'beta' is the brightness offset

    # Convert image to float32 to avoid overflow during adjustments
    img = img.astype(np.float32)

    # Adjust contrast (alpha is contrast factor)
    alpha = 1 + contrast / 100.0  # 1.0 means no change
    beta = brightness  # Beta is the brightness adjustment

    # Apply contrast and brightness adjustments
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    return img



def process_whiteboard_image(img, output_path="output_image.jpg", dark_threshold=40):
    # Read the image

    # Increase brightness and contrast before further processing
    img = adjust_brightness_contrast(img, brightness=30, contrast=10)
    cv2.imwrite("bright_image.png", img)

    # Apply binary thresholding to get a black and white image
    _, binary = cv2.threshold(img, 245, 255, cv2.THRESH_BINARY_INV)

    # Clean up noise using morphological operations (e.g., closing)
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Apply dilation to thicken the text
    dilated_text = cv2.dilate(cleaned, kernel, iterations=1)

    # Invert the binary image to separate the whiteboard (white) from the text (black)
    text = cv2.bitwise_and(img, img, mask=dilated_text)  # Thicker black text

    # Overlay the thicker text on the original image
    overlay_img = cv2.addWeighted(img, 0.7, text, -0.4, 0)

    # Threshold overlay_img to keep only dark pixels
    dark_pixels = overlay_img < dark_threshold
    overlay_img[~dark_pixels] = 255  # Set pixels lighter than threshold to white

    # Save the overlay image as a file
    cv2.imwrite(output_path, overlay_img)

    return overlay_img



def preprocess_image(image):
    """
    Preprocess the image by converting it to grayscale and applying adaptive thresholding.
    Additionally, remove black borders around the whiteboard to focus on the equations.
    """
    # Convert to grayscale
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Display the grayscale fimage to check the contrast before thresholding
    """plt.imshow(image, cmap='gray')
    plt.title("Grayscale Image")
    plt.axis("off")
    plt.show()"""


    # Apply adaptive thresholding to get a black and white image
    binary = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY, 15, -5)
    
    cv2.imwrite("adaptive_threshold.png", binary)

    # Display the binary image to inspect the result
    """plt.imshow(binary, cmap='gray')
    plt.title("Binary Image (Adaptive Thresholding)")
    plt.axis("off")
    plt.show()"""

    # Find contours to detect the black border (assuming it is the largest contour)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and select the largest contour (black border)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Get the bounding box of the largest contour (the whiteboard's black border)
    # x, y, w, h = cv2.boundingRect(contours[0])

    # Crop out the region of interest (whiteboard without the black border)
    # img_cropped = img[y:y + h, x:x + w]
    # binary_cropped = binary[y:y + h, x:x + w]

    return image, binary, image, binary




def extract_equation_groups(image):
    """
    This function takes the image path of black equations on a white whiteboard,
    removes the black border, and breaks the image into individual equation groups.
    It returns the cropped equations along with their full bounding boxes.
    """
    # Preprocess the image to remove the black border
    img_cropped, binary_cropped, img, binary = preprocess_image(image)
    #binary_cropped = cv2.bitwise_not(binary_cropped)  # White background

    cv2.imwrite("img_cropped.png", binary_cropped)

    # Apply dilation to join nearby contours
    kernel = np.ones((20, 20), np.uint8)  # Adjust the kernel size as needed
    dilated = cv2.dilate(binary_cropped, kernel, iterations=1)
    cv2.imwrite("dilated.png", dilated)

    # Find contours in the dilated binary image (equation groups)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours based on their y-coordinate (top-to-bottom order)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    # Prepare a list to store cropped equation images and their bounding boxes
    equation_groups = []

    img_with_contours = img_cropped.copy()
    cv2.drawContours(img_with_contours, contours, -1, (0, 255, 0), 3)  # Draw contours in green
    cv2.imwrite("contours_debug.png", img_with_contours)

    # Iterate through each contour and crop the equation group
    for cindex, contour in enumerate(contours):

        # Get the bounding box of the contour (x, y, width, height)
        x, y, w, h = cv2.boundingRect(contour)

        # Ensure the bounding box is large enough to contain text
        if w > 20 and h > 20:  # Filter out small contours (non-text regions)
            # Crop the equation group from the original image
            cropped_equation = img_cropped[y:y + h, x:x + w]

            # Convert the crop to grayscale for text percentage calculation
            if len(cropped_equation.shape) == 3:  # Check if it's color
                grayscale_crop = cv2.cvtColor(cropped_equation, cv2.COLOR_BGR2GRAY)
            else:
                grayscale_crop = cropped_equation

            # Convert the grayscale crop to binary
            _, cropped_binary = cv2.threshold(grayscale_crop, 127, 255, cv2.THRESH_BINARY_INV)

            # Calculate the percentage of text in the binary image
            text_pixels = cv2.countNonZero(cropped_binary)  # Count black pixels
            total_pixels = cropped_binary.size
            text_percentage = (text_pixels / total_pixels) * 100

            # Only add the original crop to the list if the text percentage is above 10%
            if text_percentage >= 0:
                # Append the equation crop along with its full bounding box (x, y, w, h)
                equation_groups.append({
                    'equation': cropped_equation,  # Cropped equation image
                    'bounding_box': (x, y, w, h)  # Full bounding box (x, y, width, height)
                })
            else:
                print("Didn't append contour (IT DIDN'T HAVE ENOUGH TEXT!)")

    return equation_groups, img_cropped, binary_cropped




def show_preprocessed_image(img, binary, img_cropped, binary_cropped):
    """
    Show the original image, the binary threshold image, and the cropped version after
    removing the black border.
    """
    pass
    """plt.figure(figsize=(12, 6))

    # Show the original image
    plt.subplot(2, 2, 1)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title("Original Image")
    plt.axis("off")

    # Show the binary threshold image
    plt.subplot(2, 2, 2)
    plt.imshow(binary, cmap='gray')
    plt.title("Binary Image")
    plt.axis("off")

    # Show the cropped image (after removing the black border)
    plt.subplot(2, 2, 3)
    plt.imshow(cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB))
    plt.title("Cropped Image (No Black Border)")
    plt.axis("off")

    # Show the cropped binary image (after removing the black border)
    plt.subplot(2, 2, 4)
    plt.imshow(binary_cropped, cmap='gray')
    plt.title("Cropped Binary Image")
    plt.axis("off")

    plt.tight_layout()
    plt.show()"""


def show_extracted_equations(equation_images):
    """
    Display the extracted equations as separate images using matplotlib.
    """
    if len(equation_images) == 0:
        print("No equations were extracted.")
        return

    """plt.figure(figsize=(12, 6))
    for i, equation in enumerate(equation_images):
        # Check if the equation is a valid image (not empty)
        if equation is not None and isinstance(equation, np.ndarray) and equation.size > 0:
            plt.subplot(1, len(equation_images), i + 1)
            plt.imshow(cv2.cvtColor(equation, cv2.COLOR_BGR2RGB))
            plt.axis("off")
            plt.title(f"Equation {i + 1}")
        else:
            print(f"Invalid or empty image at index {i}")
    plt.show()"""


# Function to check if an image is over a certain percentage of dark pixels
def over_n_black(image, n=80, threshold=30):
    """
    Checks if more than 'n' percent of the pixels in the image are considered dark (below the 'threshold').

    :param image: The PIL image to analyze.
    :param n: The percentage of dark pixels required (default 80%).
    :param threshold: The pixel value below which a pixel is considered dark (default 50).
    :return: True if more than 'n' percent of the pixels are dark, otherwise False.
    """
    # Convert the image to grayscale
    gray_image = image.convert('L')  # Convert to grayscale (L mode)

    # Convert the grayscale image to a numpy array
    img_array = np.array(gray_image)

    # Count dark pixels (pixels below the threshold)
    dark_pixels = np.sum(img_array < threshold)

    # Calculate total number of pixels
    total_pixels = img_array.size

    # Calculate the percentage of dark pixels
    dark_percentage = (dark_pixels / total_pixels) * 100

    return dark_percentage > n


def process_equations(image):
    image = process_whiteboard_image(image, "output_image_with_text.jpg")

    equation_groups, img_cropped, binary_cropped = extract_equation_groups(image)
    equation_images = [e["equation"] for e in equation_groups]
    equation_boxes = [e['bounding_box'] for e in equation_groups]
    print(f"equation groups: {equation_groups}")

    # Show the preprocessed images
    #show_preprocessed_image(img_cropped, binary_cropped, img_cropped, binary_cropped)

    # Show the extracted equations (after preprocessing)
    show_extracted_equations(equation_images)

    # Get the image dimensions (width, height)
    image_height, image_width = image.shape[:2]

    # Calculate the total area (width * height)
    total_area = image_width * image_height

    print(f"There are {len(equation_images)} equations in total.")

    equations_with_positions = []

    for index, eq in enumerate(equation_images):
        # Convert the OpenCV image (NumPy array) to a PIL image
        image = Image.fromarray(cv2.cvtColor(eq, cv2.COLOR_BGR2RGB))

        # Get the dimensions of the image
        eq_width, eq_height = image.size

        # Calculate the area of the image
        image_area = eq_width * eq_height

        # Calculate the percentage of the image area compared to the total area
        area_percentage = (image_area / total_area) * 100

        # Skip if the image takes up more than 40% of the total area
        if area_percentage > 40:
            print(f"Skipping image {index}, as it takes up {area_percentage:.2f}% of the total area.")
            continue  # Skip this iteration

        # Check if the image is over 80% black and skip if true
        if over_n_black(image):
            print(f"Skipping image {index}, as it is over 80% black.")
            continue  # Skip this iteration

        # Extract LaTeX from the PIL image
        try:
            image.save(f"eq_{index}.jpg", format="JPEG")
            latex_string = get_latex_from_image_path(f"eq_{index}.jpg")
            print(f"Latex String obtained :: {latex_string}")
            
            # Get the position of the equation in the cropped image
            # Assuming the equation group has the "position" data which provides the (x, y) top-left position
            #eq_position = equation_groups[index].get("position", (0, 0))
            #eq_x, eq_y = eq_position

            (x1, y1, w, h) = equation_groups[index].get("bounding_box")

            center_right_x = x1 + w + 15
            center_right_y = y1 + (h // 2)

            # Append the equation and its position
            equations_with_positions.append((latex_string, (center_right_x, center_right_y)))

        except Exception as e:
            latex_string = "Extraction failed"
            print(e)

        # Create a figure for each equation
        """plt.figure(figsize=(6, 4))
        plt.imshow(image)
        plt.axis('off')
        plt.title(f"Equation {index}")
        plt.text(0.5, -0.1, latex_string, ha='center', va='top', wrap=True, transform=plt.gca().transAxes)

        # Save each plot as an image file
        plt.savefig(f"equation_{index}.png", bbox_inches='tight')
        plt.close()"""

    return equations_with_positions



if __name__ == "__main__":
    process_equations()