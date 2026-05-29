from typing import Any

import customtkinter as ctk

from loader import AssetRegistry
from utils import get_color_palette


class Notifier(ctk.CTkFrame):
    _PROPS = {
        "error": {
            "fg_color": get_color_palette()["red_bg"],
            "border_color": get_color_palette()["red_text"],
            "text_color": get_color_palette()["red_text"],
        },
        "success": {
            "fg_color": get_color_palette()["green_bg"],
            "border_color": get_color_palette()["green_text"],
            "text_color": get_color_palette()["green_text"],
        },
    }

    def __init__(self, master: Any, duration: int = 3200) -> None:
        super().__init__(
            master,
            border_color="#444",
            border_width=1,
            fg_color="#181818",
            corner_radius=10,
        )
        self._after_id = None
        self.duration = duration
        self._build()

    def _build(self):
        self.message = ctk.CTkLabel(
            self,
            text="",
            font=AssetRegistry.fonts(),
            width=100,
            height=30,
        )
        self.message.grid(row=0, column=0, padx=10, pady=10)

    def _reveal(
        self, message: str, text_color: str, border_color: str, fg_color: str
    ) -> None:
        self.configure(
            fg_color=fg_color,
            border_color=border_color,
        )
        self.message.configure(text=message, text_color=text_color)
        self.place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-12)
        self._after_id = self.after(self.duration, self._hide)

    def error(self, message: str) -> None:
        self._reveal(message, **self._PROPS["error"])

    def success(self, message: str) -> None:
        self._reveal(message, **self._PROPS["success"])

    def _hide(self) -> None:
        self.place_forget()

        if self._after_id is not None:
            self.after_cancel(self._after_id)
