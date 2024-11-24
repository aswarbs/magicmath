
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
import json


class TTS():
    def __init__(self):
        self.speech_file_path = "speech.mp3"

        with open('key.txt', 'r') as file:
            key = file.read().strip()

        self.client = OpenAI(api_key=key)

    def speak(self, text):
        print("PLAYING...")
        with self.client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(self.speech_file_path)

        # Load the MP3 file
        speech = AudioSegment.from_mp3(self.speech_file_path)

        # Play the MP3 file
        play(speech)

        

if __name__ == "__main__": 
    tts = TTS()
    tts.speak("Welcome to your job interview. Can you tell me about yourself?")