import os
import sys
from typing import List, Literal

ALLOWED_OS_PREFIXES = ("win",)


def verify_os() -> None:
    if not sys.platform.startswith(ALLOWED_OS_PREFIXES):
        exit("Operating system not supported")


name_max_len = 14


def shorten_gesture_name(name: str) -> str:
    return name[:name_max_len] + "..." if len(name) > name_max_len else name


# Verificar que el path exista
# y que no sea un programa sino una carpeta
def is_valid_path(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)


WIFI_INTERFACE_NAME = "Wi-Fi"


# Pendiente de implementacion
# Util para mostrarle al usuario
# que la opcion de ejecutar el gesto para
# lo que tiene que ver con el wifi esta desabilitado
def has_wifi_adapter() -> bool:
    return True


# Hay que implementar bien esto
def wifi_command_generator(action: Literal["enable", "disable"]) -> List[str]:
    action_lowered = action.lower()

    if action_lowered not in ["enable", "desable"]:
        raise Exception("Invalid action for wifi command")

    command = []

    return command
