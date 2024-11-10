"""from engine.MProjectorWindow import ProjectorWindow
from engine.MTestWindow import TestWindow
import time

if __name__ == "__main__":
    # Create and run the app
    app = ProjectorWindow()
    
    while 1:
        app.mainloop()
        time.sleep(0.1)"""


from engine.Window import GameWindow
from engine.MLabel import MLabel
from engine.MProfile import MProfile
from engine.MCharacterDialogue import MCharacterDialogue
from engine.MTimeIntro import MTimeIntro
from engine.GenAI.ProfileGen import gen_profile, Era
from engine.MTexLabel import MTexLabel
from engine.MMainMenu import MMainMenu

if __name__ == "__main__":
    # Create and run the app
    app = GameWindow()
    a = MMainMenu(app)
    app.entities.append(a)
    app.mainloop()