# AQUI IRAN TODAS LAS CLASES RELACIONADAS CON LA LOGICA
from dataclasses import dataclass
from enum import StrEnum


class ModificationType(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class Modification[T]:
    type: ModificationType
    data: T


class Action(StrEnum):
    SET_VOLUME = "set_volume"
    SET_WIFI_STATE = "set_wifi_state"
    TAKE_SCREENSHOT = "take_screenshot"
    OPEN_FILE = "open_file"
    OPEN_FOLDER = "open_folder"
    RUN_PROGRAM = "run_program"


class ParamType(StrEnum):
    NUMERIC = "numeric"
    BINARY = "binary"
    FILE_PATH = "file_path"
    FOLDER_PATH = "folder_path"


class Finger(StrEnum):
    THUMB_FINGER = "thumb"
    INDEX_FINGER = "index_finger"
    MIDDLE_FINGER = "middle_finger"
    RING_FINGER = "ring_finger"
    LITTLE_FINGER = "little_finger"


@dataclass
class FormState:
    is_valid: bool = True
    error_message: str | None = None


# Para saber la "orientación" de la mano
# Empezaremos por estas pero se puede incrementar
# para detectar gestos con la parte lateral de la mano
# o con el puño orientado a la camara, etc.
class HandProfile(StrEnum):
    PALM = "palm"
    FRONT = "front"
