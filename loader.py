from typing import Dict, Literal

import customtkinter as ctk
import tksvg

from utils import get_or_default

FontMap = Dict[str, ctk.CTkFont]
IconMap = Dict[str, tksvg.SvgImage]


class AssetRegistry:
    _fonts_cache: FontMap = {}
    _icons_cache: IconMap = {}

    _SIZES = {
        "title": 25,
        "regular": 15,
        "bold": 15,
    }

    @classmethod
    def load_fonts(cls) -> None:
        ctk.FontManager.load_font("fonts/InterVariable.ttf")

    @classmethod
    def fonts(
        cls,
        size: int | None = None,
        variant: Literal["title", "bold", "regular"] = "regular",
    ) -> ctk.CTkFont:
        hash = str(size) + variant

        if hash not in cls._fonts_cache:
            cls._fonts_cache[hash] = ctk.CTkFont(
                family="Inter Variable",
                size=size or cls._SIZES[variant],
                weight="bold" if variant == "bold" or variant == "title" else "normal",
            )

        return cls._fonts_cache[hash]

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
        "add": "./icons/add.svg",
        "save": "./icons/save.svg",
        "trash": "./icons/trash.svg",
        "mark": "./icons/mark.svg",
    }

    @classmethod
    def icons(cls, name: str, scale: int = 25) -> tksvg.SvgImage:
        hash = str(scale) + name
        path = get_or_default(cls._ICON_DEFINITIONS, name, None)

        if path is None:
            raise ValueError(f"Icon {name} does not exists")

        if hash not in cls._icons_cache:
            cls._icons_cache[hash] = tksvg.SvgImage(file=path, scaletoheight=scale)

        return cls._icons_cache[hash]


def load_fonts_files() -> None:
    AssetRegistry.load_fonts()


def get_fonts(
    size: int | None = None, variant: Literal["title", "bold", "regular"] = "regular"
) -> ctk.CTkFont:
    return AssetRegistry.fonts(size, variant)


def get_icons(name: str, scale: int = 25) -> tksvg.SvgImage:
    return AssetRegistry.icons(name, scale)
