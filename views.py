import customtkinter as ctk

from utils import get_color_palette
from widgets import Camera, SettingsForm, SettingsHeader, Sidebar


class GestureDetectionView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=get_color_palette()["bg"])

        self.main = True
        self.set_layout()

    def highlight_gesture(self, event):
        if event.char.isdigit():
            self.sidebar.highlight_gesture(int(event.char))

    def set_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.display_sidebar()
        self.display_camera()

    def display_sidebar(self):
        self.sidebar = Sidebar(self, controller=self.master)
        self.sidebar.grid(column=0, row=0, sticky="ns")

    def display_camera(self):
        self.camera_frame = Camera(self)
        self.camera_frame.grid(row=0, column=1, sticky="nswe")

    def on_closing(self):
        self.camera_frame.on_closing()


class ConfigureGesturesView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=get_color_palette()["bg"])

        self.set_layout()
        self.display_header()
        self.display_form()

    def set_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def display_form(self):
        self.form = SettingsForm(self)
        self.form.grid(row=1, column=0, pady=0, sticky="wens")

    def display_header(self):
        self.header = SettingsHeader(self, controller=self.master)
        self.header.grid(row=0, column=0, sticky="nwse")
