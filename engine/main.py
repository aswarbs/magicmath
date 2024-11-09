from Window import *
from MLabel import MLabel
from MProfile import MProfile
from GenAI.ProfileGen import gen_profile, Era
from MTexLabel import MTexLabel

if __name__ == "__main__":
    # Create and run the app
    app = GameWindow()
    pubert = MProfile(app.master, gen_profile(Era.INFORMATION))
    app.entities.append(pubert)
    pubert.speak("wefmoewmfkmefo")

    app.mainloop()