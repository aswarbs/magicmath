from engine.GameEntity import GameEntity
import tkinter as tk
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from engine.MTimeIntro import MTimeIntro
from PIL import Image, ImageTk
import ctypes.wintypes
from engine.MProjectorWindow import ProjectorWindow
from engine.MTestWindow import TestWindow
import time


class MMainMenu(GameEntity):
    def __init__(self, master):
        self.text_id = None
        self.rect_id = None
        self.title_id = None
        self.dead = False
        self.x = 0  # x will be set dynamically for centering
        self.y = 0  # y will be set dynamically for centering
        self.width = 150  # width of the door
        self.height = 280  # height of the door

        # Bind the keys to functions when the menu is created
        self.master = master
        self.master.master.bind("<KeyPress-n>", self.on_key_press_1)  # Bind key "n"
        self.master.master.bind("<KeyPress-m>", self.on_key_press_2)  # Bind key "m"
        self.setup()

    # Get monitor information
    def get_monitors_info(self):
        user32 = ctypes.windll.user32
        def _get_monitors_resolution():
            monitors = []
            monitor_enum_proc = ctypes.WINFUNCTYPE(
                ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double)
            def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                monitors.append((lprcMonitor.contents.left, lprcMonitor.contents.top,
                                lprcMonitor.contents.right - lprcMonitor.contents.left,
                                lprcMonitor.contents.bottom - lprcMonitor.contents.top))
                return 1
            user32.EnumDisplayMonitors(None, None, monitor_enum_proc(callback), 0)
            return monitors
        monitors = _get_monitors_resolution()
        print(monitors)
        #exit()
        return monitors

    def setup(self):
        monitors = self.get_monitors_info()
        if len(monitors) >= 2:
            x1, y1, w1, h1 = monitors[1]
            x1, y1, w1, h1 = (1536, 0, 640, 480) # trying to fix monitor issues
            self.master.master.geometry("%dx%d+%d+%d" % (w1, h1, x1, y1))
            self.master.master.overrideredirect(1)
        else:
            w1, h1 = monitors[0][2], monitors[0][3]
            self.master.master.geometry("%dx%d+0+0" % (w1, h1))
            self.master.master.overrideredirect(1)



    def draw(self, canvas: tk.Canvas):

        if self.dead:
            return

        # Remove any previous items
        if self.text_id is not None:
            canvas.delete(self.text_id)
        if self.title_id is not None:
            canvas.delete(self.title_id)
        if self.rect_id is not None:
            canvas.delete(self.rect_id)

        # Get canvas width and height
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Calculate the position for the door to be centered
        self.x = canvas_width / 4
        self.y = canvas_height / 2

        # Draw title
        self.title_id = canvas.create_text(canvas_width / 2, canvas_height / 3,
                                           text="Mathquest", font=("Avenir Next", 36, "bold"), fill="black")

        # Draw instruction text
        self.rect_id = canvas.create_text(canvas_width / 2, canvas_height / 2,
                                          text="Draw a 1 to enter freemode, or a 2 to enter story.",
                                          font=("CMU Serif Roman", 22), fill="black")

    def think(self):
        pass

    def delete(self):
        # Remove any previous items
        if self.text_id is not None:
            self.master.canvas.delete(self.text_id)
        if self.title_id is not None:
            self.master.canvas.delete(self.title_id)
        if self.rect_id is not None:
            self.master.canvas.delete(self.rect_id)
        self.dead = True

        self.master.master.unbind("<KeyPress-n>")  # Bind key "n"
        self.master.master.unbind("<KeyPress-m>")  # Bind key "m"

    # Function for when key "1" is pressed
    def on_key_press_1(self, event):
        print("Key 1 pressed! Entering freemode...")
        self.delete()
        self.master.master.destroy()
        app = TestWindow()

        while 1:
            app.mainloop()
            time.sleep(0.1)

        #self.master.entities.append(MTimeIntro(self.master, "2024", "Cario"))
        # Here you can implement logic for freemode entry

    # Function for when key "2" is pressed
    def on_key_press_2(self, event):
        print("Key 2 pressed! Entering story mode...")
        self.delete()
        self.master.master.destroy()
        app = ProjectorWindow()

        while 1:
            app.mainloop()
            time.sleep(0.1)