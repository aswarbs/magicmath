from pix2text import Pix2Text
from PIL import Image
import matplotlib.pyplot as plt
import re

# Initialize Pix2Text
pix2text = Pix2Text()

# Load the handwritten formula image
image_path = 'test_images/test_lambda.png'
image = Image.open(image_path)

# Convert the image to grayscale
image = image.convert("L")

# Run OCR on the enhanced image
ocr_text = pix2text(image)

# Process and print the output
print("Extracted Page:", ocr_text)
texts = [o.text for o in ocr_text.elements]
print(texts)

# Print each formula found and save as an image
print("Detected Formulas:")
for i, clean_t in enumerate(texts, 1):
    if not clean_t:  # Skip empty formulas
        print(f"Formula {i}: (empty or invalid)")
        continue

    # Display the formula text
    print(f"Formula {i}: {clean_t}")

    try:
        # Plot the formula using LaTeX formatting and save it as an image
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"${clean_t}$", fontsize=20, ha='center', va='center', usetex=True)
        ax.axis('off')  # Hide axes

        # Save each formula as an image file
        fig.savefig(f'output/formula_{i}.png', bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)
        
        print(f"Formula {i} saved as 'formula_{i}.png'")

    except Exception as e:
        print(f"Error rendering formula {i}: {e}")
