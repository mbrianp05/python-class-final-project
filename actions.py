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

from PIL import ImageGrab
from pycaw.pycaw import AudioUtilities
from winrt.windows.devices.radios import Radio, RadioKind, RadioState

import utils


# abrir el explorador en esa carpeta
def open_explorer_at(path: str) -> None:
    subprocess.run(["explorer", path])


# Ejecutar programas solamente (.exe)
# no sirve para abrir archivos como tal
def run_program(path: str) -> None:
    subprocess.run([path])


def open_file_with_default_app(filepath: str) -> None:
    subprocess.run(["start", "", filepath], shell=True, check=True)


def set_volume(delta_level: float) -> None:
    delta_level = utils.clamp(0.0, delta_level, 0.0)

    device = AudioUtilities.GetSpeakers()

    if device is not None:
        volume = device.EndpointVolume
        new_level = max(
            0.0, min(1.0, volume.GetMasterVolumeLevelScalar() + delta_level)
        )
        volume.SetMasterVolumeLevelScalar(new_level, None)


def set_wifi_state(enable: bool) -> None:
    state = RadioState.ON if enable else RadioState.OFF

    # Actualizar estado del primer dispositivo Wi-Fi encontrado
    async def async_set_wifi() -> None:
        for i in await Radio.get_radios_async():
            if i.kind == RadioKind.WI_FI and i.state != state:
                _ = await i.set_state_async(state)  # type: ignore
                break

    asyncio.run(async_set_wifi())


def take_screenshot() -> None:
    screenshot = ImageGrab.grab()

    # De momento vamos a poner un path forzado
    # lo mejor seria como dije navegar con una ventana del explorador
    # hasta la ubicacion deseada como "guardar como"
    path_plus_name = "D:\\"

    screenshot.save(path_plus_name)
