from dataclasses import dataclass
from enum import Enum

import tksvg

# ARCHIVO QUE SE UTILIZARA PARA CLASES DE CONFIGURACION
# DE ELEMENTOS DE LA INTERFAZ DE USUARIO


class View(Enum):
    DETECTION_VIEW = "main"
    SETTINGS_VIEW = "settings"


class MessageType(Enum):
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"


@dataclass
class MouseEventsImagesPack:
    noEvent: tksvg.SvgImage
    mouseEnter: tksvg.SvgImage | None = None
    mouseClick: tksvg.SvgImage | None = None
