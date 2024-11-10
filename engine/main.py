from Window import GameWindow
from MLabel import MLabel
from MProfile import MProfile
from MCharacterDialogue import MCharacterDialogue
from MTimeIntro import MTimeIntro
from GenAI.ProfileGen import gen_profile, Era
from MTexLabel import MTexLabel
from MMainMenu import MMainMenu

if __name__ == "__main__":
    # Create and run the app
    app = GameWindow()
    a = MMainMenu(app)
    app.entities.append(a)
    app.mainloop()