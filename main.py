from typing import Dict

import customtkinter as ctk

from loader import AssetRegistry
from uiclasses import View
from universe import BaseNavigator, Universe
from utils import (
    create_config_file_if_not_exists,
    get_or_default,
    supress_warnings,
    verify_os,
)
from views import BaseView, ConfigureGesturesView, GestureDetectionView

AssetRegistry.load_fonts()

create_config_file_if_not_exists()
supress_warnings()


class App(ctk.CTk, BaseNavigator):
    def __init__(self):
        super().__init__()

        self.title("Reconocimiento de gestos")

        self._views_classes: Dict[View, type[BaseView]] = {}
        self._views_instances: Dict[View, BaseView] = {}

        Universe.rise().compass(self)

        self._set_views()
        self.maximize_window()

    def _set_views(self) -> None:
        self._views_classes[View.DETECTION_VIEW] = GestureDetectionView
        self._views_classes[View.SETTINGS_VIEW] = ConfigureGesturesView

        self._show_main()

    def _show_main(self) -> None:
        main: View | None = None

        for name, cls in self._views_classes.items():
            if cls.is_main() is True:
                main = name

        if main is None:
            main = get_or_default(list(self._views_classes.keys()), 0, None)

        if main is None:
            return

        self._show(main)

    def navigate(self, destination: View) -> None:
        self._show(destination)

    def _show(self, active_view: View) -> None:
        for view in self._views_instances.values():
            view.pack_forget()

        if active_view not in self._views_instances:
            self._views_instances[active_view] = self._views_classes[active_view](self)

        self._views_instances[active_view].pack(fill="both", expand=True)

    def maximize_window(self):
        self._state_before_windows_set_titlebar_color = "zoomed"

    def on_closing(self):
        for view in self._views_instances.values():
            view.on_closing()


if __name__ == "__main__":
    verify_os()

    app = App()
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")
    app.mainloop()

    app.on_closing()
