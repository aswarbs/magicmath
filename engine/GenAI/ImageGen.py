from openai import OpenAI
from Key import OPENAI_API_KEY
import requests

def generate_and_download_image(api_key, prompt, image_filename="generated_image.png", size="256x256", n=1):
    """
    Generate an image using OpenAI's DALL·E and download it locally.

    Parameters:
    - api_key (str): OpenAI API key for authentication.
    - prompt (str): The text prompt to generate the image.
    - image_filename (str): The filename to save the generated image. Defaults to "generated_image.png".
    - size (str): The resolution of the image. Can be "256x256", "512x512", or "1024x1024".
    - n (int): The number of images to generate (default is 1).

    Returns:
    - str: The filename where the image is saved.
    """
    # Set up your OpenAI API key

    # Generate the image using OpenAI's DALL·E
    client = OpenAI(api_key=api_key)
    response = client.images.generate(prompt=prompt,  # Describe the image you want
    n=n,  # Number of images to generate
    size=size)

    # Get the URL of the generated image
    image_url = response.data[0].url

    # Download the image from the URL
    img_data = requests.get(image_url).content

    # Save the image locally (you can change the file name and format if needed)
    with open(image_filename, 'wb') as file:
        file.write(img_data)

    print(f"Image saved as '{image_filename}'")
    return image_filename


if __name__ == "__main__":
    prompt = "a painting of a renissance era man"
    filename = generate_and_download_image(OPENAI_API_KEY, prompt, "surreal_forest.png")
