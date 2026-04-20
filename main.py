import customtkinter as ctk

from components import Camera, Sidebar
from services import fetch_gestures
from utils import verify_os

ctk.FontManager.load_font("fonts/Proxima Nova Regular.ttf")
ctk.FontManager.load_font("fonts/Proxima Nova Light.ttf")
ctk.FontManager.load_font("fonts/Proxima Nova Semibold.ttf")
ctk.FontManager.load_font("fonts/Proxima Nova Extrabold.ttf")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Reconocimiento de gestos")

        self.configure_layout()
        self.maximize()

    def maximize(self):
        self._state_before_windows_set_titlebar_color = (
            "zoomed"  # Para maximizar la ventana
        )

    def configure_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.display_sidebar()
        self.display_camera()

    def display_sidebar(self):
        self.sidebar = Sidebar(self, fetch_gestures())
        self.sidebar.grid(column=0, row=0, sticky="ns")

    def display_camera(self):
        self.camera_frame = Camera(self)
        self.camera_frame.grid(row=0, column=1, sticky="nswe")

    def on_closing(self):
        self.camera_frame.on_closing()


if __name__ == "__main__":
    verify_os()

    app = App()

    # Hay que mejorar el tema de la pantalla completa
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")
    # app.after(25, lambda: app.attributes("-fullscreen", True))

    # app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
