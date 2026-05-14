import os
import sys
import warnings
from datetime import datetime
from tkinter import filedialog

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


def supress_warnings():
    warnings.filterwarnings(
        "ignore", message=".*Image can not be scaled on HighDPI displays*."
    )


def get_save_path() -> str:
    now = datetime.now()
    sample_name = now.strftime("%Y-%m-%d %H:%M:%S") + ".png"

    file_path = filedialog.asksaveasfilename(
        initialdir="/",
        title="Secciona la ubicación de la captura de pantalla",
        defaultextension=".png",
        filetypes=[
            ("Archivo PNG", "*.png"),
            ("Archivo JPEG", "*.jpg;*.jpeg"),
            ("Archivo BMP", "*.bmp"),
            ("Todos los archivos", "*.*"),
        ],
        initialfile=sample_name,
    )

    return file_path


def clamp(min, value, max):
    if value < min:
        return min

    if value > max:
        return max

    return value
