from tkinter import *
import ctypes.wintypes
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
from gui.calibration_screen import CalibrationScreen


# Get monitor information
def get_monitors_info():
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
    return monitors

class MyApp:
    def __init__(self, master):
        self.master = master
        master.title("My App")

        monitors = get_monitors_info()
        if len(monitors) >= 2:
            x1, y1, w1, h1 = monitors[1]
            master.geometry("%dx%d+%d+%d" % (w1, h1, x1, y1))
            master.overrideredirect(1)
        else:
            w1, h1 = monitors[0][2], monitors[0][3]
            master.geometry("%dx%d+0+0" % (w1, h1))
            master.overrideredirect(1)

        # Set the background color to white
        master.configure(bg="white")

        self.parent_frame = Frame(self.master)
        self.parent_frame.pack(fill=BOTH, expand=TRUE)


    def display_calibration_screen(self):
        calibration_screen = CalibrationScreen(self.master, self.parent_frame)
