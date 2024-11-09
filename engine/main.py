from Window import *
from MLabel import MLabel

if __name__ == "__main__":
    # Create and run the app
    app = GameWindow()
    app.entities.append(MLabel("beans"))
    app.mainloop()