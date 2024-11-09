from gui.screen_setup import MyApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    app.display_calibration_screen()
    root.mainloop()