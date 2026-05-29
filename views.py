import abc

import customtkinter as ctk

from services import GestureStore
from universe import Universe
from utils import get_color_palette
from widgets import Camera, SettingsForm, SettingsHeader, Sidebar


class BaseView(ctk.CTkFrame, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def is_main(cls) -> bool:
        """Verifica que la vista sea la principal"""

    @abc.abstractmethod
    def on_closing(self) -> None:
        """Lo que ocurre cuando se cierra la aplicacion"""


class GestureDetectionView(BaseView):
    def __init__(self, master):
        super().__init__(master, fg_color=get_color_palette()["bg"])

        self.set_layout()

        self.display_sidebar()
        self.display_camera()

    @classmethod
    def is_main(cls) -> bool:
        return not GestureStore.get().is_empty()

    def highlight_gesture(self, event):
        if event.char.isdigit():
            self.sidebar.highlight_gesture(int(event.char))

    def set_layout(self):
        self.columnconfigure(0, weight=0, minsize=Sidebar._WIDTH)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def display_sidebar(self):
        self.sidebar = Sidebar(self)
        self.sidebar.grid(column=0, row=0, sticky="ns")

        universe = Universe.rise()
        universe.responder(self.sidebar)

    def display_camera(self):
        self.camera_frame = Camera(self, self.sidebar)
        self.camera_frame.grid(row=0, column=1, sticky="nswe")

    def on_closing(self):
        self.camera_frame.on_closing()


class ConfigureGesturesView(BaseView):
    def __init__(self, master):
        super().__init__(master, fg_color=get_color_palette()["bg"])

        self.set_layout()
        self.display_header()
        self.display_form()

    @classmethod
    def is_main(cls) -> bool:
        return GestureStore.get().is_empty()

    def set_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def display_form(self):
        self.form = SettingsForm(self)
        self.form.grid(row=1, column=0, pady=0, sticky="wens")

    def display_header(self):
        self.header = SettingsHeader(self)
        self.header.grid(row=0, column=0, sticky="nwse")

    def on_closing(self):
        pass
