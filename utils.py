import os

name_max_len = 14


def shorten_gesture_name(name: str) -> str:
    return name[:name_max_len] + "..." if len(name) > name_max_len else name


# Verificar que el path exista
# y que no sea un programa sino una carpeta
def is_valid_path(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)
