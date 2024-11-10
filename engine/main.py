from Window import *
from MDoorLevel import MDoor
from MLabel import MLabel
from MMainMenu import MMainMenu

if __name__ == "__main__":
    # Create and run the app
    app = GameWindow()
    lab = MMainMenu(app)

    app.entities.append(lab)
    app.mainloop()