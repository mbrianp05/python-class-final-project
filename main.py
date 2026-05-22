import customtkinter as ctk

import loader
from uiclasses import MessageType, View
from utils import create_config_file_if_not_exists, supress_warnings, verify_os
from views import ConfigureGesturesView, GestureDetectionView
from widgets import FloatingFeedbackLabel

loader.load_fonts_files()
create_config_file_if_not_exists()
supress_warnings()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Reconocimiento de gestos")

        self.views = {}

        self.feedback = FloatingFeedbackLabel(self)

        self.set_views()
        self.maximize_window()

    def set_views(self):
        self.views[View.DETECTION_VIEW] = GestureDetectionView(self)
        self.views[View.SETTINGS_VIEW] = ConfigureGesturesView(self, notifier=self)

        # Esto es temporal
        self.bind("<Key>", self.views[View.DETECTION_VIEW].highlight_gesture)

        for view in self.views.values():
            view.pack(fill="both", expand=True)

        self.show_main()

    def show_main(self):
        main: View | None = None

        for name, view in self.views.items():
            if getattr(view, "is_main", False) is True:
                main = name

        if main is None:
            main = list(self.views.keys())[0]

        self.show(main)

    def show(self, active_view):
        for view in self.views.values():
            view.pack_forget()

        self.views[active_view].pack(fill="both", expand=True)

    def maximize_window(self):
        self._state_before_windows_set_titlebar_color = "zoomed"

    def on_closing(self):
        for view in self.views.values():
            getattr(view, "on_closing", lambda: None)()

    def notify(self, type: MessageType, text: str):
        self.feedback.show_variant(type, text)


if __name__ == "__main__":
    verify_os()

    app = App()

    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")
    app.mainloop()

    app.on_closing()
