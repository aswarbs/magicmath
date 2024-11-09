from Window import *
from MLabel import MLabel
from MTexLabel import MTexLabel

if __name__ == "__main__":
    # Create and run the app
    app = GameWindow()
    app.entities.append(MTexLabel())
    app.mainloop()