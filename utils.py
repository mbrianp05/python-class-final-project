import os
import sys

ALLOWED_OS_PREFIXES = ("win",)


def verify_os() -> None:
    if not sys.platform.startswith(ALLOWED_OS_PREFIXES):
        exit("Operating system not supported")


name_max_len = 17


def shorten_gesture_name(name: str) -> str:
    return name[: name_max_len - 3] + "..." if len(name) > name_max_len else name


# Verificar que el path exista
# y que no sea un programa sino una carpeta
def is_valid_path(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)


# LA PALETA DE COLORES DE LA APP
# CAMBIAR AL GUSTO
def get_color_palette():
    return {
        "primary": "#2563EB",
        "primary_hover": "#3B82F6",
        "primary_muted": "#1E3A8A",
        # Text
        "text_primary": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "text_accent": "#FFFFFF",
        # Border & accent
        "border": "#334155",
        "accent": "#0EA5E9",
    }
