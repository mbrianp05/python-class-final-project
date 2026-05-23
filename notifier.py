"""
notifier.py
-----------
Notificador global de la aplicación.

Uso rápido
----------
    # En la ventana raíz (una sola vez):
    Notifier.init(root_window)

    # Desde cualquier widget, en cualquier parte de la app:
    Notifier.get().notify(MessageType.SUCCESS, "Gesto guardado")
    Notifier.get().notify(MessageType.ERROR,   "Algo salió mal")
    Notifier.get().notify(MessageType.INFO,    "Información")

Diseño
------
• Singleton: una sola instancia vive atada a la ventana raíz.
• Posicionamiento con .place(relx, rely) → siempre en la esquina
  superior derecha, independiente del layout del resto de la app.
• Cola de mensajes: si llega uno nuevo antes de que expire el actual,
  se encola y se muestra en secuencia (sin solapamiento).
• Animación de entrada/salida mediante pasos de opacidad simulados
  con .place() y alpha (en plataformas que lo soporten) o simplemente
  aparece/desaparece limpiamente en las que no.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

import customtkinter as ctk

import loader
from uiclasses import MessageType

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Paleta y constantes
# ---------------------------------------------------------------------------

_VARIANTS: dict[MessageType, dict[str, str]] = {
    MessageType.SUCCESS: {"bg": "#2E7D52", "icon": "✓"},
    MessageType.ERROR: {"bg": "#B33A3A", "icon": "✗"},
    MessageType.INFO: {"bg": "#1A4F8A", "icon": "ℹ"},
}

_DEFAULT_DURATION_MS = 3500  # tiempo visible por notificación
_PADDING_RIGHT = 20  # margen desde el borde derecho (px)
_PADDING_TOP = 16  # margen desde el borde superior (px)
_TOAST_WIDTH = 320
_TOAST_HEIGHT = 56
_CORNER_RADIUS = 10


# ---------------------------------------------------------------------------
# Toast — el widget visual de una notificación
# ---------------------------------------------------------------------------


class _Toast(ctk.CTkFrame):
    """
    Frame flotante con icono + texto que se ancla a la ventana raíz
    mediante .place(). No participa en ningún layout (pack/grid).
    """

    def __init__(self, root: ctk.CTk) -> None:
        super().__init__(
            root,
            width=_TOAST_WIDTH,
            height=_TOAST_HEIGHT,
            corner_radius=_CORNER_RADIUS,
            fg_color="#1A4F8A",
        )
        # Evita que CTkFrame encoja el frame a 0x0 antes del primer place()
        self.propagate(False)

        fonts = loader.get_fonts()

        # Icono (carácter unicode)
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

        # Texto del mensaje
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

        # Empezamos oculto
        self.place_forget()

    def show(self, message_type: MessageType, text: str) -> None:
        variant = _VARIANTS[message_type]
        self.configure(fg_color=variant["bg"])
        self._icon_label.configure(text=variant["icon"])
        self._text_label.configure(text=text)
        self._reposition()

    def _reposition(self) -> None:
        root = self.master
        root.update_idletasks()

        win_w = root.winfo_width()
        x = win_w - _TOAST_WIDTH - _PADDING_RIGHT
        y = _PADDING_TOP

        self.place(x=x, y=y)

    def hide(self) -> None:
        self.place_forget()


# ---------------------------------------------------------------------------
# Notifier — singleton global
# ---------------------------------------------------------------------------


class Notifier:
    """
    Notificador global. Mantiene una cola de mensajes y los muestra
    de uno en uno usando el mismo _Toast.

    Ciclo de vida
    -------------
    init(root)   →  crea la instancia singleton
    get()        →  devuelve la instancia (lanza si no fue inicializado)
    notify(...)  →  encola un mensaje; si no hay ninguno visible, lo muestra
    """

    _instance: Notifier | None = None

    # -- Inicialización ------------------------------------------------------

    @classmethod
    def init(cls, root: ctk.CTk) -> "Notifier":
        """
        Crea el singleton y lo ancla a *root*.
        Debe llamarse una sola vez, justo después de crear la ventana raíz.
        """
        if cls._instance is not None:
            return cls._instance
        cls._instance = cls(root)
        return cls._instance

    @classmethod
    def get(cls) -> "Notifier":
        """Devuelve la instancia global. Lanza si no se llamó a init()."""
        if cls._instance is None:
            raise RuntimeError(
                "Notifier no inicializado. Llama a Notifier.init(root) primero."
            )
        return cls._instance

    # -- Constructor (privado en la práctica) --------------------------------

    def __init__(self, root: ctk.CTk) -> None:
        self._root = root
        self._toast = _Toast(root)
        self._queue: deque[tuple[MessageType, str, int]] = deque()
        self._busy = False

    # -- API pública ---------------------------------------------------------

    def notify(
        self,
        message_type: MessageType,
        text: str,
        duration: int = _DEFAULT_DURATION_MS,
    ) -> None:
        """
        Muestra *text* como notificación de tipo *message_type*.
        Si hay otra activa, encola el mensaje y se mostrará al terminar.
        """
        self._queue.append((message_type, text, duration))
        if not self._busy:
            self._show_next()

    # -- Lógica interna ------------------------------------------------------

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
        """Rellama cada 100ms mientras el toast esté visible."""
        if not self._busy:
            return
        self._toast._reposition()
        self._toast.lift()
        self._root.after(100, self._keep_on_top)

    def _on_expire(self) -> None:
        self._toast.hide()
        # Pequeña pausa entre notificaciones para que no se solapean visualmente
        self._root.after(200, self._show_next)
