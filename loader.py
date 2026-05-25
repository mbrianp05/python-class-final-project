"""
loader.py – Carga de assets con patrón Singleton.

Uso:
    from loader import AssetRegistry

    # Obtener fuentes e iconos (se instancian solo la primera vez)
    fonts = AssetRegistry.fonts()
    icons = AssetRegistry.icons()
    icons_large = AssetRegistry.icons(scale=260)

    # Cargar las fuentes al inicio de la app (llamar una sola vez en main.py)
    AssetRegistry.load_fonts()
"""

from __future__ import annotations

from typing import Dict

import customtkinter as ctk
import tksvg

# ---------------------------------------------------------------------------
# Tipos de alias
# ---------------------------------------------------------------------------

FontMap = Dict[str, ctk.CTkFont]
IconMap = Dict[str, tksvg.SvgImage]


# ---------------------------------------------------------------------------
# Singleton de assets
# ---------------------------------------------------------------------------


class AssetRegistry:
    """
    Registro centralizado de fuentes e iconos.

    • Las fuentes se almacenan por tamaño: _fonts_cache[size] → FontMap
    • Los iconos se almacenan por escala:  _icons_cache[scale] → IconMap
    • Ningún objeto se crea más de una vez por parámetro.
    """

    _fonts_cache: Dict[int | None, FontMap] = {}
    _icons_cache: Dict[int, IconMap] = {}

    # ------------------------------------------------------------------
    # Inicialización (llamar una sola vez en main.py)
    # ------------------------------------------------------------------

    @classmethod
    def load_fonts(cls) -> None:
        """Registra el archivo de fuente en CustomTkinter."""
        ctk.FontManager.load_font("fonts/InterVariable.ttf")

    # ------------------------------------------------------------------
    # Fuentes
    # ------------------------------------------------------------------

    @classmethod
    def fonts(cls, size: int | None = None) -> FontMap:
        """
        Devuelve el mapa de fuentes para *size*.
        Si ya fue creado para ese tamaño, devuelve la instancia cacheada.

        Claves devueltas: "title", "bold", "regular"
        """
        if size not in cls._fonts_cache:
            cls._fonts_cache[size] = {
                "title": ctk.CTkFont(
                    family="Inter Variable",
                    size=25 if size is None else size,
                ),
                "bold": ctk.CTkFont(
                    family="Inter Variable",
                    size=15 if size is None else size,
                    weight="bold",
                ),
                "regular": ctk.CTkFont(
                    family="Inter Variable",
                    size=15 if size is None else size,
                    weight="normal",
                ),
            }
        return cls._fonts_cache[size]

    # ------------------------------------------------------------------
    # Iconos
    # ------------------------------------------------------------------

    _ICON_DEFINITIONS: Dict[str, str] = {
        "gear": "./icons/gear.svg",
        "gear_darker": "./icons/gear-darker.svg",
        "generic-gesture": "./icons/generic-gesture.svg",
        "arrow_left": "./icons/arrow-left.svg",
        "arrow_left_darker": "./icons/arrow-left-darker.svg",
        "hand-1": "./icons/hand-1.svg",
        "hand-2": "./icons/hand-2.svg",
        "hand-1-darker": "./icons/hand-1-darker.svg",
        "hand-2-darker": "./icons/hand-2-darker.svg",
        "screenshot": "./icons/screenshot.svg",
        "open_file": "./icons/open-file.svg",
        "open_folder": "./icons/open-folder.svg",
        "run_program": "./icons/run-program.svg",
        "set_volume": "./icons/set-volume.svg",
        "set_wifi": "./icons/set-wifi.svg",
    }

    @classmethod
    def icons(cls, scale: int = 25) -> IconMap:
        """
        Devuelve el mapa de iconos para *scale*.
        Si ya fue creado para esa escala, devuelve la instancia cacheada.
        """
        if scale not in cls._icons_cache:
            cls._icons_cache[scale] = {
                name: tksvg.SvgImage(file=path, scaletoheight=scale)
                for name, path in cls._ICON_DEFINITIONS.items()
            }
        return cls._icons_cache[scale]

    # ------------------------------------------------------------------
    # Utilidad: invalidar caché (útil en tests o recargas en caliente)
    # ------------------------------------------------------------------

    @classmethod
    def clear_cache(cls) -> None:
        """Elimina todos los objetos cacheados. Úsalo con cuidado."""
        cls._fonts_cache.clear()
        cls._icons_cache.clear()


# ---------------------------------------------------------------------------
# API de compatibilidad hacia atrás
# Permite que el código antiguo que llama a load_fonts_files() / get_fonts()
# / get_icons() siga funcionando sin cambios mientras se migra gradualmente.
# ---------------------------------------------------------------------------


def load_fonts_files() -> None:
    """Compatibilidad: delega en AssetRegistry.load_fonts()."""
    AssetRegistry.load_fonts()


def get_fonts(size: int | None = None) -> FontMap:
    """Compatibilidad: delega en AssetRegistry.fonts(size)."""
    return AssetRegistry.fonts(size)


def get_icons(scale: int = 25) -> IconMap:
    """Compatibilidad: delega en AssetRegistry.icons(scale)."""
    return AssetRegistry.icons(scale)
