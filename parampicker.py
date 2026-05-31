from __future__ import annotations

import abc
from typing import Any, Callable

import customtkinter as ctk

from loader import AssetRegistry
from numeric_input import NumericInput
from utilityclasses import FormState, ParamType
from utils import (
    is_valid_file,
    is_valid_path,
    pick_file,
    pick_folder,
    shorten_middle,
)

# ---------------------------------------------------------------------------
# Paleta de colores y constantes de diseño
# ---------------------------------------------------------------------------

_COLORS = {
    "bg": "transparent",
    "accent": "#3A8CFF",
    "error": "#FF5C5C",
    "success": "#4CAF93",
    "text": "#DCE4EE",
    "subtext": "#999",
    "border": "#2D3748",
    "input_bg": "#1A2233",
    "button_bg": "#223355",
    "button_hover": "#3A8CFF",
}

_RADIUS = 8
_ENTRY_HEIGHT = 31
_BUTTON_HEIGHT = 31
_PATH_MAX_LEN = 45


# ---------------------------------------------------------------------------
# Clase base – contrato que todo sub-picker debe cumplir
# ---------------------------------------------------------------------------


class BaseParamPanel(ctk.CTkFrame, abc.ABC):
    stands_for: ParamType  # declarado en cada subclase

    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(
            master,
            fg_color=_COLORS["bg"],
            height=90,
            width=400,
            **kwargs,
        )

        self.font_regular = AssetRegistry.fonts(variant="regular")
        self.font_bold = AssetRegistry.fonts(variant="bold")

        self._callback = None

        self._build()

    # -- API pública --------------------------------------------------------

    @abc.abstractmethod
    def _build(self) -> None:
        """Construye los widgets internos."""

    @abc.abstractmethod
    def adjust_value(self, value: Any) -> None:
        """Carga *value* en el widget (puede ser None)."""

    @abc.abstractmethod
    def get_value(self) -> Any:
        """Devuelve el valor actual del widget."""

    @abc.abstractmethod
    def get_state(self) -> FormState:
        """Valida el valor actual y devuelve un FormState."""

    @abc.abstractmethod
    def on_change(self, callback: Callable[[Any], None]) -> None:
        """Registra un callback para ejecutar cuando cambia el valor"""


# ---------------------------------------------------------------------------
# Sub-picker: BINARY  (Activar / Desactivar)
# ---------------------------------------------------------------------------


class BinaryParamPanel(BaseParamPanel):
    stands_for = ParamType.BINARY

    def _build(self) -> None:
        self._var = ctk.IntVar(value=1)

        radio_cfg = dict(
            variable=self._var,
            font=self.font_regular,
            fg_color=_COLORS["accent"],
        )

        ctk.CTkRadioButton(self, text="Activar", value=1, **radio_cfg).grid(  # type: ignore
            row=0, column=0, sticky="w", padx=(10, 0)
        )

        ctk.CTkRadioButton(self, text="Desactivar", value=0, **radio_cfg).grid(  # type: ignore
            row=0, column=1, sticky="w", padx=(10, 0)
        )

        if self._callback:
            self._var.trace_add("write", lambda *_: self._callback(self._var.get()))

    def on_change(self, callback: Callable[[Any], None]) -> None:
        self._callback = callback

    def adjust_value(self, value: Any) -> None:
        self._var.set(int(value) if value is not None else 1)

    def get_value(self) -> bool:
        return bool(self._var.get())

    def get_state(self) -> FormState:
        return FormState(is_valid=True)


# ---------------------------------------------------------------------------
# Sub-picker: NUMERIC  (entrada numérica validada)
# ---------------------------------------------------------------------------


class NumericParamPanel(BaseParamPanel):
    stands_for = ParamType.NUMERIC

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)

        self._entry = NumericInput(
            self,
            font=self.font_regular,
            height=_ENTRY_HEIGHT,
            width=200,
            min=-1,
            max=1,
            allow_float=True,
            allow_negatives=True,
            onchange=self._on_change,
        )
        self._entry.grid(row=0, column=0, sticky="w", padx=0)

        self._error_label = ctk.CTkLabel(
            self,
            text="",
            font=self.font_regular,
            text_color=_COLORS["error"],
            fg_color=_COLORS["bg"],
        )
        self._error_label.grid(row=1, column=0, sticky="w", padx=0)

    def _on_change(self, value: float) -> None:
        state = self._entry.get_state()
        self._error_label.configure(
            text="" if state.is_valid else (state.error_message or "")
        )

        if self._callback:
            self._callback(value)

    def adjust_value(self, value: Any) -> None:
        self._entry.delete(0, "end")
        self._entry.insert(0, str(value) if value is not None else "")

    def get_value(self) -> float | None:
        try:
            return self._entry.get_value()
        except (ValueError, TypeError):
            return None

    def get_state(self) -> FormState:
        return self._entry.get_state()

    def on_change(self, callback: Callable[[Any], None]) -> None:
        self._callback = callback


# ---------------------------------------------------------------------------
# Sub-picker: FILE_PATH  (selector de archivo)
# ---------------------------------------------------------------------------


class FileParamPanel(BaseParamPanel):
    stands_for = ParamType.FILE_PATH

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)

        # Fila 0: ruta + botón
        self._path_label = ctk.CTkLabel(
            self,
            text="Sin archivo seleccionado",
            font=self.font_regular,
            text_color=_COLORS["subtext"],
            fg_color=_COLORS["bg"],
            anchor="w",
            wraplength=260,
        )
        self._path_label.grid(row=0, column=0, sticky="w", padx=(0, 12))

        self._browse_btn = ctk.CTkButton(
            self,
            text="Buscar archivo",
            font=self.font_regular,
            height=_BUTTON_HEIGHT,
            corner_radius=_RADIUS,
            command=self._on_browse,
        )
        self._browse_btn.grid(row=0, column=1, padx=(0, 10))

        self._error_label = ctk.CTkLabel(
            self,
            text="",
            font=self.font_regular,
            text_color=_COLORS["error"],
            fg_color=_COLORS["bg"],
            anchor="w",
        )
        self._error_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=(0, 12))

        self._value: str | None = None
        self._state = FormState(is_valid=False, error_message="Sin archivo")

    def _on_browse(self) -> None:
        path = pick_file()

        if path:
            self.adjust_value(path)

        if self._callback:
            self._callback(path)

    def adjust_value(self, value: str | None) -> None:
        self._value = value

        if value is None:
            self._path_label.configure(
                text="Sin archivo seleccionado", text_color=_COLORS["subtext"]
            )
            self._state = FormState(
                is_valid=False, error_message="No se ha elegido el archivo"
            )
            self._error_label.configure(text="")
            return

        ok = is_valid_file(value)
        self._state = FormState(
            is_valid=ok,
            error_message=None if ok else "El archivo no fue encontrado",
        )
        self._path_label.configure(
            text=shorten_middle(value, _PATH_MAX_LEN),
            text_color=_COLORS["text"] if ok else _COLORS["error"],
        )
        self._error_label.configure(
            text="" if ok else (self._state.error_message or "")
        )

    def on_change(self, callback: Callable[[Any], None]) -> None:
        self._callback = callback

    def get_value(self) -> str | None:
        return self._value

    def get_state(self) -> FormState:
        return self._state


# ---------------------------------------------------------------------------
# Sub-picker: FOLDER_PATH  (selector de carpeta)
# ---------------------------------------------------------------------------


class FolderParamPanel(BaseParamPanel):
    stands_for = ParamType.FOLDER_PATH

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)

        self._path_label = ctk.CTkLabel(
            self,
            text="Sin carpeta seleccionada",
            font=self.font_regular,
            text_color=_COLORS["subtext"],
            fg_color=_COLORS["bg"],
            anchor="w",
            wraplength=260,
        )
        self._path_label.grid(row=0, column=0, sticky="w", padx=(0, 12))

        self._browse_btn = ctk.CTkButton(
            self,
            text="Buscar carpeta",
            font=self.font_regular,
            height=_BUTTON_HEIGHT,
            corner_radius=_RADIUS,
            command=self._on_browse,
        )
        self._browse_btn.grid(row=0, column=1, padx=(0, 10))

        self._error_label = ctk.CTkLabel(
            self,
            text="",
            font=self.font_regular,
            text_color=_COLORS["error"],
            fg_color=_COLORS["bg"],
            anchor="w",
        )
        self._error_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=(0, 12))

        self._value: str | None = None
        self._state = FormState(is_valid=False, error_message="Sin carpeta")

    def _on_browse(self) -> None:
        path = pick_folder()

        if path:
            self.adjust_value(path)

        if self._callback:
            self._callback(path)

    def adjust_value(self, value: str | None) -> None:
        self._value = value

        if value is None:
            self._path_label.configure(
                text="Sin carpeta seleccionada", text_color=_COLORS["subtext"]
            )
            self._state = FormState(
                is_valid=False, error_message="No se ha proporcionado ninguna carpeta"
            )
            self._error_label.configure(text="")
            return

        ok = is_valid_path(value)
        self._state = FormState(
            is_valid=ok,
            error_message=None if ok else "La carpeta no fue encontrada",
        )
        self._path_label.configure(
            text=shorten_middle(value, _PATH_MAX_LEN),
            text_color=_COLORS["text"] if ok else _COLORS["error"],
        )
        self._error_label.configure(
            text="" if ok else (self._state.error_message or "")
        )

    def on_change(self, callback: Callable[[Any], None]) -> None:
        self._callback = callback

    def get_value(self) -> str | None:
        return self._value

    def get_state(self) -> FormState:
        return self._state


# ---------------------------------------------------------------------------
# Orquestador: ParamPicker
# ---------------------------------------------------------------------------


class ParamPicker(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        paramtype: ParamType | None = ParamType.NUMERIC,
        initial_value: Any = None,
        on_change: Callable[[Any], None] | None = None,
    ) -> None:
        super().__init__(master, fg_color=_COLORS["bg"])

        self._callback = on_change
        self._panels: dict[ParamType, BaseParamPanel] = {}
        self._active_type: ParamType | None = None

        self._register_panels()
        self.set_param_type(paramtype, initial_value)

    # -- Registro de paneles ------------------------------------------------

    def _register_panels(self) -> None:
        """
        Instancia y registra todos los sub-pickers disponibles.
        Para añadir uno nuevo, agrégalo aquí.
        """
        panel_classes: list[type[BaseParamPanel]] = [
            BinaryParamPanel,
            NumericParamPanel,
            FileParamPanel,
            FolderParamPanel,
        ]

        for cls in panel_classes:
            panel = cls(self)

            if self._callback:
                panel.on_change(self._callback)

            self._panels[cls.stands_for] = panel

    # -- API pública --------------------------------------------------------

    def set_param_type(
        self, paramtype: ParamType | None, initial_value: Any = None
    ) -> None:
        self._active_type = paramtype

        for _, panel in self._panels.items():
            panel.pack_forget()

        if paramtype is None:
            return

        active_panel = self._panels.get(paramtype)

        if active_panel is None:
            raise KeyError(f"No hay panel registrado para ParamType.{paramtype}")

        active_panel.adjust_value(initial_value)
        active_panel.pack(fill="both", expand=True)

    def get_value(self) -> Any:
        """Devuelve el valor del panel activo, o None si no hay ninguno."""
        if self._active_type is None:
            return None
        return self._panels[self._active_type].get_value()

    def get_state(self) -> FormState:
        """Devuelve el FormState del panel activo."""
        if self._active_type is None:
            return FormState(
                is_valid=True,
                error_message=None,
            )
        return self._panels[self._active_type].get_state()
