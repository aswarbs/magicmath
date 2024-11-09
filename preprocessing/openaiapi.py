import base64
import openai
from io import BytesIO
from PIL import Image
from Keys import OPENAI_API_KEY

# Ensure your OpenAI API key is set
openai.api_key = OPENAI_API_KEY


# Function to encode a Pillow image to base64
def encode_pillow_image(pillow_image):
    # Create a BytesIO object to hold the image data
    buffered = BytesIO()
    # Save the Pillow image as a JPEG (or PNG) into the buffered object
    pillow_image.save(buffered, format="JPEG")
    # Get the byte data from the buffer and encode it to base64
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


# Function to send the Pillow image and ask for the equation in LaTeX
def get_latex_equation_from_pillow(pillow_image):
    # Encode the Pillow image to base64
    base64_image = encode_pillow_image(pillow_image)

    # Sending the image to OpenAI's API to get a LaTeX response
    response = openai.Image.create(
        model="gpt-4",  # Or any model supporting image input
        prompt="Extract the equation from this image and provide it in LaTeX format.",
        image=f"data:image/jpeg;base64,{base64_image}",
    )

    # Return the LaTeX response
    return response['choices'][0]['text']


# Example usage
# Load a Pillow image (for example from a file or any source)
image_path = 'path_to_your_image_of_equation.jpg'
pillow_image = Image.open(image_path)

# Get the LaTeX equation
latex_equation = get_latex_equation_from_pillow(pillow_image)
print(f"Extracted LaTeX Equation: {latex_equation}")
