from tkinter import *


class Interface:

    def __init__(self):
        # Interface
        self.windows = Tk()
        self.canvas = Canvas()

    def set_up_windows(self):
        self.windows.config(padx=50, pady=50)
        self.windows.minsize(1280, 720)
        self.windows.maxsize(1920, 1080)
        self.windows.resizable(True, True)
        self.windows.title('Watermark App')