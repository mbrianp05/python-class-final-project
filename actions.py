# AQUÍ SE PONDRÁN TODAS LAS FUNCIONES BÁSICAS QUE LOS GESTOS USAN PARA EJECUTARSE
# DE MOMENTO SE IMPLEMENTARÁN ESTAS, SE PUEDE AÑADIR MÁS IDEAS SE SE DESEA.

# Aqui no se valida el path sino que asumimos que es correcto
# el path se valida cuando el usuario lo introduce a la hora de
# configurar el gesto
# Hay que tener en cuenta que el usuario podrá introducir el path
# escribiendolo manualmente, copiandolo o con un botón para navegar de la UI
# por el sistema de archivos hasta que llegue a la carpeta deseada

import subprocess


# abrir el explorador en esa carpeta
def open_explorer_at(path: str) -> None:
    subprocess.run(["explorer", path])


# Ejecutar programas solamente (.exe)
# no sirve para abrir archivos como tal
def run_program(path: str) -> None:
    subprocess.run([path])


def open_file_with_default_app(filepath: str) -> None:
    subprocess.run(["start", "", filepath], shell=True, check=True)


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
