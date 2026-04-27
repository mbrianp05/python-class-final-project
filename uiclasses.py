from dataclasses import dataclass

import tksvg

# ARCHIVO QUE SE UTILIZARA PARA CLASES DE CONFIGURACION\
# DE ELEMENTOS DE LA INTERFAZ DE USUARIO


@dataclass
class MouseEventsImagesPack:
    noEvent: tksvg.SvgImage
    mouseEnter: tksvg.SvgImage | None = None
    mouseClick: tksvg.SvgImage | None = None
