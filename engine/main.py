from MProjectorWindow import ProjectorWindow
from MLabel import MLabel
from MProfile import MProfile
from GenAI.ProfileGen import gen_profile, Era
from MTexLabel import MTexLabel

if __name__ == "__main__":
    # Create and run the app
    app = ProjectorWindow()

    app.mainloop()