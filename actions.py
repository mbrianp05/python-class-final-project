# AQUÍ SE PONDRÁN TODAS LAS FUNCIONES BÁSICAS QUE LOS GESTOS USAN PARA EJECUTARSE
# DE MOMENTO SE IMPLEMENTARÁN ESTAS, SE PUEDE AÑADIR MÁS IDEAS SE SE DESEA.

import os


# Validar que el path sea correcto y si lo es
# abrir el explorador en esa carpeta
def open_explorer_at(path: str) -> None:
    os.startfile(path)


# Validar el path y abrir el programa
def run_program(path: str) -> None:
    pass


def volume_up(rate: int) -> None:
    pass


def volume_down(rate: int) -> None:
    pass


def wifi_on() -> None:
    pass


def wifi_off() -> None:
    pass


def take_screenshot() -> None:
    pass
