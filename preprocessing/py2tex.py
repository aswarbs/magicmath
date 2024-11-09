from pix2text import Pix2Text
from PIL import Image
import matplotlib.pyplot as plt
import os


class FormulaExtractor():
    def __init__(self, model=None):
        """
        Initializes the formula extractor with a Pix2Text model.
        If no model is provided, it initializes a new Pix2Text model.
        """
        # Initialize Pix2Text model if not passed
        self.pix2text = model if model else Pix2Text()

        # Ensure output directory exists
        if not os.path.exists('output'):
            os.makedirs('output')

    def extract_latex_from_image(self, image):
        """
        Extracts LaTeX formulas from a handwritten image and saves them as images.

        Args:
            image (str): Path to the image containing handwritten formulas.

        Returns:
            list: List of LaTeX formulas extracted from the image.
        """

        # Save the original image before processing
        original_image_path = "saved_image.png"  # Path where you want to save the original image
        image.save(original_image_path)

        # Convert the image to grayscale for OCR
        image = image.convert("L")

        # Run OCR on the image using Pix2Text
        ocr_text = self.pix2text(image)

        # Extract and process OCR output
        texts = [o.text for o in ocr_text.elements if o.text.strip()]
        detected_formulas = []

        # Process each detected formula and save as an image
        for i, formula in enumerate(texts, 1):
            # Skip if the detected formula is empty
            if not formula:
                continue

            # Display the formula in the terminal
            print(f"Formula {i}: {formula}")
            detected_formulas.append(formula)

        return detected_formulas