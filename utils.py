import json
import os
import sys
import warnings
from datetime import datetime
from tkinter import filedialog, messagebox
from typing import Any, Dict

from gesture import Gesture, GestureData, HandProfile
from utilityclasses import Action, Finger

ALLOWED_OS_PREFIXES = ("win",)


def verify_os() -> None:
    if not sys.platform.startswith(ALLOWED_OS_PREFIXES):
        exit("Operating system not supported")


name_max_len = 22


def shorten_middle(str: str, max: int) -> str:
    if len(str) <= max:
        return str

    ends = int(max / 2)

    return str[:ends] + "..." + str[-ends - max % 2 :]


def shorten(str: str, max: int) -> str:
    return str[: max - 3] + "..." if len(str) > max else str


def shorten_gesture_name(name: str) -> str:
    return shorten(name, name_max_len)


def get_or_default(sequence, index, default=None):
    try:
        return sequence[index]
    except (ValueError, IndexError, KeyError):
        return default


# Verificar que el path exista
# y que no sea un programa sino una carpeta
def is_valid_path(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)


def is_valid_file(filepath: str) -> bool:
    return os.path.exists(filepath) and not os.path.isdir(filepath)


def confirm(message: str) -> bool:
    return messagebox.askokcancel("Confirma tu decisión", message=message)


# LA PALETA DE COLORES DE LA APP
# CAMBIAR AL GUSTO
def get_color_palette():
    return {
        "bg": "transparent",
        "green_bg": "#0f2e1e",
        "green_text": "#4caf93",
        "red_bg": "#391010",
        "red_text": "#ff6b6b",
    }


def supress_warnings():
    warnings.filterwarnings(
        "ignore", message=".*Image can not be scaled on HighDPI displays*."
    )


def pick_file(filetypes=[("Todos los archivos", "*.*")]) -> str:
    return filedialog.askopenfilename(
        initialdir="/", title="Selecciona un archivo", filetypes=filetypes
    )


def pick_folder() -> str:
    file_path = filedialog.askdirectory(
        initialdir="/",
        title="Secciona la ubicación de la carpeta",
    )

    return file_path


def save_photo_path() -> str:
    default_extension = ".png"

    now = datetime.now()
    sample_name = now.strftime("%Y%m%d_%H%M%S") + default_extension

    file_path = filedialog.asksaveasfilename(
        initialdir="/",
        title="Secciona la ubicación de la captura de pantalla",
        defaultextension=default_extension,
        filetypes=[
            ("Archivo PNG", "*.png"),
            ("Archivo JPEG", "*.jpg;*.jpeg"),
            ("Archivo BMP", "*.bmp"),
            ("Todos los archivos", "*.*"),
        ],
        initialfile=sample_name,
    )

    return file_path


CONFIG_FILE_NAME = "data.json"


def create_config_file_if_not_exists(filename=CONFIG_FILE_NAME):
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump([], file)


def turn_dict_into_gesture(data: Dict[Any, Any]) -> Gesture:
    hands = tuple(data["settings"]["hands"])
    fingers = (
        [Finger(f) for f in data["settings"]["visibleFingers"][0]],
        [Finger(f) for f in data["settings"]["visibleFingers"][1]],
    )

    profile = (None, None)
    profiles = data["settings"]["profile"]

    if profiles is not None:
        left_hand_profile = (
            HandProfile(profiles[0]) if profiles[0] is not None else None
        )

        right_hand_profile = (
            HandProfile(profiles[1]) if profiles[1] is not None else None
        )

        profile = (left_hand_profile, right_hand_profile)

    settings = GestureData(hands=hands, visibleFingers=fingers, profile=profile)

    gesture = Gesture(
        id=data["id"],
        name=data["name"],
        settings=settings,
        effect=Action(data["effect"]),
        param=data["param"],
    )

    return gesture


def turn_gesture_into_dict(gesture: Gesture) -> Dict[Any, Any]:
    profile = []

    if gesture.settings.profile is not None:
        profile = [
            profile.value if profile is not None else None
            for profile in gesture.settings.profile
        ]

    if len(profile) == 0:
        profile = None

    return {
        "id": gesture.id,
        "name": gesture.name,
        "effect": gesture.effect.value,
        "settings": {
            "hands": gesture.settings.hands,
            "visibleFingers": gesture.settings.visibleFingers,
            "profile": profile,
        },
        "param": gesture.param,
    }


action_repr_dic = {
    Action.SET_VOLUME: "Ajustar el volumen",
    Action.SET_WIFI_STATE: "Cambiar el estado del Wi-Fi",
    Action.TAKE_SCREENSHOT: "Tomar captura de pantalla",
    Action.OPEN_FILE: "Abrir un archivo con el programa por defecto",
    Action.OPEN_FOLDER: "Abrir una carpeta en el explorador de archivos",
    Action.RUN_PROGRAM: "Correr un programa",
}


def get_repr_for_action(action: Action) -> str:
    return action_repr_dic[action]


def get_action_from_repr(repr: str) -> Action:
    dict = {value: key for key, value in action_repr_dic.items()}
    return get_or_default(dict, repr, Action.OPEN_FOLDER)


hand_profile_repr_dic = {
    HandProfile.PALM: "Palma de la mano",
    HandProfile.FRONT: "Parte frontal",
    None: "Ninguna",
}


def get_repr_for_hand_profile(profile: HandProfile | None) -> str:
    return hand_profile_repr_dic[profile]


def get_hand_profile_from_repr(repr: str) -> HandProfile | None:
    dict = {value: key for key, value in hand_profile_repr_dic.items()}
    return dict[repr]


def clamp(min, value, max):
    if value < min:
        return min

    if value > max:
        return max

    return value
