from __future__ import annotations

from collections import deque

import customtkinter as ctk

import loader
from uiclasses import MessageType

# ---------------------------------------------------------------------------
# Paleta y constantes
# ---------------------------------------------------------------------------

_VARIANTS: dict[MessageType, dict[str, str]] = {
    MessageType.SUCCESS: {"bg": "#2E7D52", "icon": "✓"},
    MessageType.ERROR: {"bg": "#B33A3A", "icon": "✗"},
    MessageType.INFO: {"bg": "#1A4F8A", "icon": "ℹ"},
}

_DEFAULT_DURATION_MS = 3500
_PADDING_RIGHT = 20
_PADDING_TOP = 16
_TOAST_WIDTH = 320
_TOAST_HEIGHT = 56
_CORNER_RADIUS = 10


# ---------------------------------------------------------------------------
# Toast
# ---------------------------------------------------------------------------


class _Toast(ctk.CTkFrame):
    """
    Hijo directo de root. Se posiciona con place() y se sube con lift()
    cada vez que aparece, lo que lo pone encima de los frames pack/grid
    existentes en ese momento.
    """

    def __init__(self, root: ctk.CTk) -> None:
        super().__init__(
            root,
            width=_TOAST_WIDTH,
            height=_TOAST_HEIGHT,
            corner_radius=_CORNER_RADIUS,
            fg_color="#1A4F8A",
        )
        self.propagate(False)

        fonts = loader.get_fonts()

        self._icon_label = ctk.CTkLabel(
            self,
            text="ℹ",
            width=36,
            height=_TOAST_HEIGHT,
            font=fonts["bold"],
            text_color="#FFFFFF",
            fg_color="transparent",
        )
        self._icon_label.place(x=12, y=0)

        self._text_label = ctk.CTkLabel(
            self,
            text="",
            width=_TOAST_WIDTH - 60,
            height=_TOAST_HEIGHT,
            font=fonts["regular"],
            text_color="#FFFFFF",
            fg_color="transparent",
            anchor="w",
            wraplength=_TOAST_WIDTH - 64,
            justify="left",
        )
        self._text_label.place(x=48, y=0)

        self.place_forget()

    def show(self, message_type: MessageType, text: str) -> None:
        variant = _VARIANTS[message_type]
        self.configure(fg_color=variant["bg"])
        self._icon_label.configure(text=variant["icon"])
        self._text_label.configure(text=text)
        self._place_on_top()

    def _place_on_top(self) -> None:
        root = self.master
        root.update_idletasks()
        x = root.winfo_width() - _TOAST_WIDTH - _PADDING_RIGHT
        y = _PADDING_TOP
        # place() primero para que el widget exista en pantalla,
        # lift() después para subirlo encima de los frames de las vistas.
        self.place(x=x, y=y)
        self.lift()

    def hide(self) -> None:
        self.place_forget()


# ---------------------------------------------------------------------------
# Notifier — singleton global
# ---------------------------------------------------------------------------


class Notifier:
    _instance: Notifier | None = None

    @classmethod
    def init(cls, root: ctk.CTk) -> "Notifier":
        """
        Llama a esto en main.py DESPUÉS de crear la ventana raíz
        pero ANTES de set_views(), para que el toast se cree antes
        que los frames de las vistas y lift() funcione correctamente.
        """
        if cls._instance is not None:
            return cls._instance
        cls._instance = cls(root)
        return cls._instance

    @classmethod
    def get(cls) -> "Notifier":
        if cls._instance is None:
            raise RuntimeError(
                "Notifier no inicializado. Llama a Notifier.init(root) primero."
            )
        return cls._instance

    def __init__(self, root: ctk.CTk) -> None:
        self._root = root
        self._toast = _Toast(root)
        self._queue: deque[tuple[MessageType, str, int]] = deque()
        self._busy = False

    def notify(
        self,
        message_type: MessageType,
        text: str,
        duration: int = _DEFAULT_DURATION_MS,
    ) -> None:
        self._queue.append((message_type, text, duration))
        if not self._busy:
            self._show_next()

    def _show_next(self) -> None:
        if not self._queue:
            self._busy = False
            return

        self._busy = True
        message_type, text, duration = self._queue.popleft()

        self._toast.show(message_type, text)
        self._keep_on_top()
        self._root.after(duration, self._on_expire)

    def _keep_on_top(self) -> None:
        """Mantiene el toast encima cada 100ms por si algún pack/grid lo tapa."""
        if not self._busy:
            return
        self._toast.lift()
        self._root.after(100, self._keep_on_top)

    def _on_expire(self) -> None:
        self._toast.hide()
        self._root.after(200, self._show_next)
