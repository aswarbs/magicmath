import base64
from openai import OpenAI
from io import BytesIO
from PIL import Image
from Key import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# Function to encode the image
def get_latex_from_image_path(path: str):

    # Path to your image
    image_path = path

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Getting the base64 string
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Extract the mathematical expression from this image, provide your response in a LaTeX form. Do not respond with anything other than the mathematical expression in LaTeX, only respond with the mathematical expression in LaTeX.",
            },
            {
              "type": "image_url",
              "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
              },
            },
          ],
        }
      ],
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    latex_equation = get_latex_from_image_path('equation_1.png')
    print(f"Extracted LaTeX Equation: {latex_equation}")
