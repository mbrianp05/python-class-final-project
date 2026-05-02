# AQUÍ SE PONDRÁN TODAS LAS FUNCIONES BÁSICAS QUE LOS GESTOS USAN PARA EJECUTARSE
# DE MOMENTO SE IMPLEMENTARÁN ESTAS, SE PUEDE AÑADIR MÁS IDEAS SE SE DESEA.

# Aqui no se valida el path sino que asumimos que es correcto
# el path se valida cuando el usuario lo introduce a la hora de
# configurar el gesto
# Hay que tener en cuenta que el usuario podrá introducir el path
# escribiendolo manualmente, copiandolo o con un botón para navegar de la UI
# por el sistema de archivos hasta que llegue a la carpeta deseada

import subprocess
import asyncio

from PIL import ImageGrab
from pycaw.pycaw import AudioUtilities
from winrt.windows.devices.radios import Radio, RadioKind, RadioState


# abrir el explorador en esa carpeta
def open_explorer_at(path: str) -> None:
    subprocess.run(["explorer", path])


# Ejecutar programas solamente (.exe)
# no sirve para abrir archivos como tal
def run_program(path: str) -> None:
    subprocess.run([path])


def open_file_with_default_app(filepath: str) -> None:
    subprocess.run(["start", "", filepath], shell=True, check=True)


def set_volume(level: float) -> None:
    level = max(0.0, min(level, 1.0))

    device = AudioUtilities.GetSpeakers()
    volume = device.EndpointVolume  # type: ignore
    volume.SetMasterVolumeLevelScalar(level, None)


def set_wifi(state: bool) -> None:
    state = RadioState.ON if state else RadioState.OFF
    
    # Actualizar estado del primer dispositivo Wi-Fi encontrado
    async def async_set_wifi() -> None:
        for i in await Radio.get_radios_async():
            if i.kind == RadioKind.WI_FI and i.state != state:
                _ = await i.set_state_async(state)  # type: ignore
                break

    asyncio.run(async_set_wifi())


def take_screenshot(path_plus_name: str) -> None:
    screenshot = ImageGrab.grab()
    screenshot.save(path_plus_name)
