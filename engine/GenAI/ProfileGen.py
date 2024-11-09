from enum import Enum
from ImageGen import *
import datetime
import random

def get_current_date_filename():
    current_date = datetime.datetime.now()
    filename = current_date.strftime("%Y-%m-%d_%H-%M-%S") + f".{current_date.microsecond // 10000:02d}"
    return filename


class Profile():
    def __init__(self, name, image):
        self.name = name
        self.image_path = image

class Era(Enum):
    ANCIENT = "Ancient"
    CLASSICAL = "Classical"
    MEDIEVAL = "Medieval"
    RENAISSANCE = "Renaissance"
    INDUSTRIAL = "Industrial"
    MODERN = "Modern"
    ATOMIC = "Atomic"
    INFORMATION = "Futuristic"

def gen_profile(era: Era) -> Profile:
    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:

        try:
            with open("Names/" + era.value.upper() + ".txt", "r") as f:
                # Read all lines from the file
                lines = f.readlines()
                # Pick a random line
                age, gender, name = random.choice(lines).strip().split(",")
                # Print the result
                print(age, gender, name)
                break  # If successful, break out of the loop
        except Exception as e:
            # If there's any exception (e.g., file not found or bad format), increment attempts
            print(f"Attempt {attempts + 1} failed: {e}")
            attempts += 1

    filepath = get_current_date_filename()
    prompt = f"{era} painted portrait of a {age} {gender} named {name}."
    generate_and_download_image(OPENAI_API_KEY, prompt, "Assets/" + filepath + ".png")
    return Profile(
        name,
        "Assets/" + filepath + ".png"
    )

if __name__ == "__main__":
    gen_profile(Era.INFORMATION)