# AQUÍ SE PONDRÁN TODAS LAS FUNCIONES BÁSICAS QUE LOS GESTOS USAN PARA EJECUTARSE
# DE MOMENTO SE IMPLEMENTARÁN ESTAS, SE PUEDE AÑADIR MÁS IDEAS SE SE DESEA.

# Aqui no se valida el path sino que asumimos que es correcto
# el path se valida cuando el usuario lo introduce a la hora de
# configurar el gesto
# Hay que tener en cuenta que el usuario podrá introducir el path
# escribiendolo manualmente, copiandolo o con un botón para navegar de la UI
# por el sistema de archivos hasta que llegue a la carpeta deseada

import asyncio
import subprocess
from typing import Any, Callable, Dict

from PIL import ImageGrab
from pycaw.pycaw import AudioUtilities
from winrt.windows.devices.radios import Radio, RadioKind, RadioState

import utils
from universe import Universe
from utilityclasses import Action, ParamType


def get_actions_param_requirements(action: Action) -> Dict[str, Any]:
    actions_requirements = {
        Action.RUN_PROGRAM: {"filetypes": [("Archivo EXE", "*.exe")]},
        Action.SET_VOLUME: {"min": -1, "max": 1},
    }

    return utils.get_or_default(actions_requirements, action, None) or {}


def get_actions_parameter_type() -> Dict[Action, ParamType | None]:
    return {
        Action.TAKE_SCREENSHOT: None,
        Action.OPEN_FILE: ParamType.FILE_PATH,
        Action.OPEN_FOLDER: ParamType.FOLDER_PATH,
        Action.SET_VOLUME: ParamType.NUMERIC,
        Action.SET_WIFI_STATE: ParamType.BINARY,
        Action.RUN_PROGRAM: ParamType.FILE_PATH,
    }


def effects_functions() -> Dict[Action, Callable]:
    return {
        Action.TAKE_SCREENSHOT: take_screenshot,
        Action.OPEN_FILE: open_file_with_default_app,
        Action.OPEN_FOLDER: open_explorer_at,
        Action.SET_VOLUME: set_volume,
        Action.SET_WIFI_STATE: set_wifi_state,
        Action.RUN_PROGRAM: run_program,
    }


# abrir el explorador en esa carpeta
def open_explorer_at(path: str) -> None:
    if not utils.is_valid_path(path):
        Universe.rise().notifier(0).error("La carpeta que se desea abrir no existe")
        return

    subprocess.run(["explorer", path])


# Ejecutar programas solamente (.exe)
# no sirve para abrir archivos como tal
def run_program(path_and_name: str) -> None:
    if not utils.is_valid_file(path_and_name):
        Universe.rise().notifier(0).error("El programa que se desea ejecutar no existe")
        return

    subprocess.run([path_and_name])


def open_file_with_default_app(filepath: str) -> None:
    if not utils.is_valid_file(filepath):
        Universe.rise().notifier(0).error("El archivo que se desea abrir no existe")
        return

    subprocess.run(["start", "", filepath], shell=True, check=True)


def set_volume(delta_level: float) -> None:
    device = AudioUtilities.GetSpeakers()

    if device is None:
        Universe.rise().notifier(0).error(
            "No existe un dispositivo de audio disponible"
        )
        return

    volume = device.EndpointVolume
    level = utils.clamp(0.0, volume.GetMasterVolumeLevelScalar() + delta_level, 1.0)
    volume.SetMasterVolumeLevelScalar(level, None)


def set_wifi_state(enable: bool) -> None:
    state = RadioState.ON if enable else RadioState.OFF

    async def async_set_wifi() -> None:
        has_device = False

        for i in await Radio.get_radios_async():
            if i.kind == RadioKind.WI_FI and i.state != state:
                await i.set_state_async(state)
                has_device = True

                break

        if not has_device:
            Universe.rise().notifier(0).error(
                "No se encnotró ningún adpatador WIFI disponible"
            )

    asyncio.run(async_set_wifi())


def take_screenshot() -> None:
    screenshot = ImageGrab.grab()
    path_plus_name = utils.save_photo_path()

    if path_plus_name:
        screenshot.save(path_plus_name)
