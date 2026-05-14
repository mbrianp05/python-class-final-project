import customtkinter as ctk

import loader
from uiclasses import MouseEventsImagesPack, Views
from widgets import Camera, IconButton, Sidebar


class GestureDetectionView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

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
        super().__init__(master)

        self.set_layout()
        self.display_go_back_button()

    def set_layout(self):
        self.pack(padx=20, pady=20)

    def display_go_back_button(self):
        pack = MouseEventsImagesPack(noEvent=loader.get_icons()["arrow_left"])
        self.nav_button = IconButton(
            self,
            images_pack=pack,
            command=lambda: self.master.show(Views.DETECTION_VIEW),  # type: ignore
        )
        self.nav_button.grid(row=0, column=0, padx=10, pady=10)
