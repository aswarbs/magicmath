import cv2
import numpy as np
import matplotlib.pyplot as plt
import py2tex
from PIL import Image


# Function to adjust brightness and contrast of the image
def adjust_brightness_contrast(img, brightness=50, contrast=30):
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



# Function to process the image and separate black (text) and white (background)
def process_whiteboard_image(image_path, output_path="output_image.jpg"):
    # Read the image
    img = cv2.imread(image_path)

    # Increase brightness and contrast before further processing
    img = adjust_brightness_contrast(img, brightness=50, contrast=50)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding to get a black and white image
    _, binary = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)

    # OPTIONAL: Clean up noise using morphological operations (e.g., closing)
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Apply dilation to thicken the text
    dilated_text = cv2.dilate(cleaned, kernel, iterations=1)

    # Invert the binary image to separate the whiteboard (white) from the text (black)
    whiteboard = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(dilated_text))  # White background
    text = cv2.bitwise_and(img, img, mask=dilated_text)  # Thicker black text

    # Convert BGR images to RGB for displaying using matplotlibs
    whiteboard_rgb = cv2.cvtColor(whiteboard, cv2.COLOR_BGR2RGB)
    text_rgb = cv2.cvtColor(text, cv2.COLOR_BGR2RGB)

    # Overlay the thicker text on the original image
    overlay_img = img
    overlay_img = cv2.addWeighted(img, 0.7, text, -0.4, 0)

    # Convert the overlay image to RGB for displaying
    overlay_img_rgb = cv2.cvtColor(overlay_img, cv2.COLOR_BGR2RGB)

    # Save the overlay image as a file
    cv2.imwrite(output_path, overlay_img)

    # Plotting the images
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 3, 1)
    plt.title("Whiteboard (Background)")
    plt.imshow(whiteboard_rgb)
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Thicker Text (Black)")
    plt.imshow(text_rgb)
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Overlay Text on Original Image")
    plt.imshow(overlay_img)
    plt.axis("off")

    plt.show()



def preprocess_image(image_path):
    """
    Preprocess the image by converting it to grayscale and applying adaptive thresholding.
    Additionally, remove black borders around the whiteboard to focus on the equations.
    """
    # Read the image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Display the grayscale image to check the contrast before thresholding
    plt.imshow(gray, cmap='gray')
    plt.title("Grayscale Image")
    plt.axis("off")
    plt.show()

    # Apply adaptive thresholding to get a black and white image
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Display the binary image to inspect the result
    plt.imshow(binary, cmap='gray')
    plt.title("Binary Image (Adaptive Thresholding)")
    plt.axis("off")
    plt.show()

    # Find contours to detect the black border (assuming it is the largest contour)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area and select the largest contour (black border)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Get the bounding box of the largest contour (the whiteboard's black border)
    x, y, w, h = cv2.boundingRect(contours[0])

    # Crop out the region of interest (whiteboard without the black border)
    img_cropped = img[y:y + h, x:x + w]
    binary_cropped = binary[y:y + h, x:x + w]

    return img_cropped, binary_cropped, img, binary



def extract_equation_groups(image_path):
    """
    This function takes the image path of black equations on a white whiteboard,
    removes the black border, and breaks the image into individual equation groups.
    """
    # Preprocess the image to remove the black border
    img_cropped, binary_cropped, img, binary = preprocess_image(image_path)

    # Apply dilation to join nearby contours
    kernel = np.ones((10, 10), np.uint8)  # Adjust the kernel size as needed
    dilated = cv2.dilate(binary_cropped, kernel, iterations=1)

    # Find contours in the dilated binary image (equation groups)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours based on their y-coordinate (top-to-bottom order)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    # Prepare a list to store cropped equation images
    equation_images = []

    # Iterate through each contour and crop the equation group
    for contour in contours:
        # Get the bounding box of the contour
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
            if text_percentage >= 10:
                equation_images.append(cropped_equation)  # Append the original crop

    return equation_images, img_cropped, binary_cropped



def show_preprocessed_image(img, binary, img_cropped, binary_cropped):
    """
    Show the original image, the binary threshold image, and the cropped version after
    removing the black border.
    """
    plt.figure(figsize=(12, 6))

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
    plt.show()


def show_extracted_equations(equation_images):
    """
    Display the extracted equations as separate images using matplotlib.
    """
    if len(equation_images) == 0:
        print("No equations were extracted.")
        return

    plt.figure(figsize=(12, 6))
    for i, equation in enumerate(equation_images):
        # Check if the equation is a valid image (not empty)
        if equation is not None and isinstance(equation, np.ndarray) and equation.size > 0:
            plt.subplot(1, len(equation_images), i + 1)
            plt.imshow(cv2.cvtColor(equation, cv2.COLOR_BGR2RGB))
            plt.axis("off")
            plt.title(f"Equation {i + 1}")
        else:
            print(f"Invalid or empty image at index {i}")
    plt.show()


process_whiteboard_image("frame_0.jpg", "output_image_with_text.jpg")

# Example usage
image_path = "output_image_with_text.jpg"  # Replace with your image path
equation_images, img_cropped, binary_cropped = extract_equation_groups(image_path)

# Show the preprocessed images
show_preprocessed_image(img_cropped, binary_cropped, img_cropped, binary_cropped)

# Show the extracted equations (after preprocessing)
show_extracted_equations(equation_images)

# Initialize the formula extractor
p = py2tex.FormulaExtractor()

# Example values for the total area (adjust based on your canvas or reference size)
# Open the image
pil_image = Image.open(image_path)

# Get the image dimensions (width, height)
image_width, image_height = pil_image.size

# Calculate the total area (width * height)
total_area = image_width * image_height


# Function to check if an image is over a certain percentage of dark pixels
def over_n_black(image, n=80, threshold=50):
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



for index, eq in enumerate(equation_images):
    # Convert the OpenCV image (NumPy array) to a PIL image
    pil_image = Image.fromarray(cv2.cvtColor(eq, cv2.COLOR_BGR2RGB))

    # Get the dimensions of the image
    image_width, image_height = pil_image.size

    # Calculate the area of the image
    image_area = image_width * image_height

    # Calculate the percentage of the image area compared to the total area
    area_percentage = (image_area / total_area) * 100

    # Skip if the image takes up more than 40% of the total area
    if area_percentage > 40:
        print(f"Skipping image {index}, as it takes up {area_percentage:.2f}% of the total area.")
        continue  # Skip this iteration

    # Check if the image is over 80% black and skip if true
    if over_n_black(pil_image):
        print(f"Skipping image {index}, as it is over 80% black.")
        continue  # Skip this iteration

    # Extract LaTeX from the PIL image
    try:
        latex_string = p.extract_latex_from_image(pil_image)

        # Clean up the LaTeX string for Matplotlib
        # Remove $$ from the LaTeX string if it has them
        latex_string = [l.replace('$$', '') for l in latex_string]
        latex_string = [l.replace('\\', "\\\\") for l in latex_string]
        latex_string = [l.replace('\n', "") for l in latex_string]

        # Optional: Wrap the entire string in single-dollar signs for inline math
        latex_string = [f"{l}" for l in latex_string]

    except Exception as e:
        latex_string = "Extraction failed"
        print(e)

    # Create a figure for each equation
    plt.figure(figsize=(6, 4))
    plt.imshow(pil_image)
    plt.axis('off')
    plt.title(f"Equation {index}")
    plt.text(0.5, -0.1, latex_string, ha='center', va='top', wrap=True, transform=plt.gca().transAxes)

    # Save each plot as an image file
    plt.savefig(f"equation_{index}.png", bbox_inches='tight')
    plt.close()  # Close the figure to free memory

print("Saved each equation plot as a separate PNG file.")