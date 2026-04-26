# AQUÍ SE PONDRÁN TODAS LAS FUNCIONES BÁSICAS QUE LOS GESTOS USAN PARA EJECUTARSE
# DE MOMENTO SE IMPLEMENTARÁN ESTAS, SE PUEDE AÑADIR MÁS IDEAS SE SE DESEA.

# Aqui no se valida el path sino que asumimos que es correcto
# el path se valida cuando el usuario lo introduce a la hora de
# configurar el gesto
# Hay que tener en cuenta que el usuario podrá introducir el path
# escribiendolo manualmente, copiandolo o con un botón para navegar de la UI
# por el sistema de archivos hasta que llegue a la carpeta deseada

import os
import subprocess
import asyncio

from pycaw.pycaw import AudioUtilities
from PIL import ImageGrab
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


def set_volume(level: int|float) -> None:
    if(isinstance(level, int)):
        level = max(0, min(level, 100))/100
    elif(isinstance(level, float)):
        level = max(0.0, min(level, 1.0))
    else:
        raise TypeError("Volume can be set to int (0 - 100) or float (0.0 - 1.0)")

    device = AudioUtilities.GetSpeakers()           # Buscar el dispositivo
    volume = device.EndpointVolume                  # Obtener la interfaz 
    volume.SetMasterVolumeLevelScalar(level, None)  # Ajustar el volumen


def set_wifi(state: bool) -> None:
    # import asyncio
    # from winrt.windows.devices.radios import Radio, RadioKind, RadioState

    state = (RadioState.ON if state else RadioState.OFF)

    async def async_set_wifi() -> None:
        try:
            radios = await Radio.get_radios_async() # Buscar todos los dispositivos

            wifi_radio = None

            for i in radios:                    # Encontrar el primer dispositivo Wi-Fi
                if i.kind == RadioKind.WI_FI:
                    wifi_radio = i
                    break

            if wifi_radio is None:
                print("No Wi-Fi was found")         # Mensaje provisional

            if wifi_radio.state != state:           # Actualizar el estado
                print("Toggling Wi-Fi")             # Mensaje provisional
                result = await wifi_radio.set_state_async(state)

        except Exception as e:
            print(f"ERROR - {e}")       # Captura provisional

    asyncio.run(async_set_wifi())

    print(f"WiFi turned {"on" if state == RadioState.ON else "off"}")    # Mensaje provisional


def take_screenshot(name="Test.png", path="Screenshots") -> None:
    # import os

    try:
        screenshot = ImageGrab.grab()                       # Captura de pantalla
        if(not os.path.exists(path)): os.makedirs(path)     # Crear la carpeta si no existe
        screenshot.save(path + "/" + name)                  # Guardar la captura
        print(f"Screenshot saved at {path}/{name}")         # Mensaje provisional
    except Exception as e:
        print(f"ERROR - {e}")       # Captura provisional

# set_volume(0)
# set_volume(0.5)
# set_volume(100)
# take_screenshot()
# set_wifi(True)
# set_wifi(False)