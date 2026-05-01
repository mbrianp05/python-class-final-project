import time
from typing import Any, Callable, List

import customtkinter as ctk
import cv2
import tksvg
from customtkinter import CTkFrame
from PIL import Image

from gesture import Gesture
from uiclasses import MouseEventsImagesPack
from utils import shorten_gesture_name


class Sidebar(CTkFrame):
    def __init__(self, master, gestures: List[Gesture] = []):
        super().__init__(master, fg_color="transparent", width=200)
        self.rowconfigure(1, weight=1)

        self.gestures = gestures

        self.init_fonts()
        self.create_header()
        self.create_scrollbar_panel()

    def init_fonts(self):
        self.header_font = ctk.CTkFont(family="Proxima Nova Rg", size=25)
        self.bold_font = ctk.CTkFont(family="Proxima Nova Lt", size=17, weight="bold")

    def create_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.columnconfigure(0, weight=1)
        self.header.grid(row=0, column=0, padx=20, sticky="we")

        self.header_label = ctk.CTkLabel(
            self.header,
            height=55,
            text="Gestos",
            font=self.header_font,
            fg_color="transparent",
            text_color="white",
            anchor="w",
        )
        self.header_label.grid(row=0, column=0, sticky="we", padx=(5, 0))

        images_pack = MouseEventsImagesPack(
            noEvent=tksvg.SvgImage(file="./icons/gear.svg", scaletoheight=26),
            mouseEnter=tksvg.SvgImage(file="./icons/gear_darker.svg", scaletoheight=26),
        )

        self.configure_gestures_label = IconButton(self.header, images_pack=images_pack)
        self.configure_gestures_label.grid(row=0, column=1, pady=(5, 0))

    def create_scrollbar_panel(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            orientation="vertical",
            fg_color="transparent",
        )
        self.scrollable_frame.items = {}  # type: ignore # Lista de elementos
        self.scrollable_frame.grid(row=1, column=0, padx=0, pady=0, sticky="ns")
        self.display_gestures_list()

    def display_gestures_list(self):
        generic_gesture_icon = tksvg.SvgImage(
            file="./icons/generic-gesture.svg", scaletoheight=25
        )

        for i, gesture in enumerate(self.gestures):
            name = shorten_gesture_name(gesture.name)

            # CAMBIAR AQUI EL LABEL POR EL COMPONENTE IMPLEMENTADO DE HIGHLIGHTING
            item = ctk.CTkLabel(
                self.scrollable_frame,
                height=45,
                text=f"  {name}",  # el espacio es para que el texto no se vea tan pegado al icono
                image=generic_gesture_icon,  # type: ignore
                fg_color="transparent",
                compound="left",
                font=self.bold_font,
                anchor="w",
                corner_radius=30,
            )

            self.scrollable_frame.items[i] = item  # type: ignore # Guardar referencias a cada elemento
            item.grid(row=i, column=0, padx=(0, 0), pady=0, sticky="ew")

    # . LEER .
    # HAY QUE SACAR ESTO A UN COMPONENTE A PARTE QUE HEREDE DE ctk.CTkLabel
    # QUE SE LLAME HighlightableLabel O ALGO ASI
    # PARA USARLO EN LOS ITEMS DE LA LISTA DE GESTOS

    # ADEMAS TE DEJE UNA CLASE uiclasses.HiglightingTransition PARA CONFIGURAR EL HIGHLIGHTING
    # QUE SE PASARIA DE PARAMETRO AL COMPONENTE

    # POR ULTIMO INTENTA QUE EL HIGHLIGHT SEA UNA ESPECIA DE PARAPEDEO
    # COMO SI FUERA UN LATIDO DE CORAZON QUE TENGA ESE EFECTO DE COMO QUE "SE ACTIVO ALGO"
    # MAS QUE DE EFECTO DE QUE PASO EL MOUSE POR ENCIMA
    def highlight_gesture(self, index: int = 0, duration: int = 500):
        if index < len(self.scrollable_frame.items):  # type: ignore
            item = self.scrollable_frame.items[index]  # type: ignore
            if isinstance(item, ctk.CTkLabel):
                if getattr(item, "highlight", None):
                    item.after_cancel(item.highlight)  # type: ignore

                # Pasar colores de resaltado como parametros (?)
                item.configure(fg_color="#3A8CFF", text_color="#fff")

                # Pasar colores originales/nuevos/finales como parametros (?)
                item.highlight = item.after(  # type: ignore
                    duration,
                    lambda: item.configure(
                        text_color="#DCE4EE", fg_color="transparent"
                    ),
                )

        else:
            raise IndexError(f"Index [{index}] was out of bounds.")


class Camera(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=0, sticky="nswe")

        # self.init_camera()

    def init_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        time.sleep(0.6)

        if not self.cap.isOpened():
            print("ERROR - Not opened")

        self.show_frames()

    def show_frames(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            self.camera_frames.configure(image=ctk.CTkImage(img, size=(600, 600)))

        self.camera_frames.after(20, self.show_frames)

    def on_closing(self):
        self.cap.release()
        self.destroy()


# El botón normal de Customtkinter tiene un aspecto
# que en ciertos casos no queremos como el boton de configurar gestos
# que no tiene color de fondo sino un icono que cambia segun los eventos
# del raton
# Como esta configuracion se usara mas veces entonces hice un componente para
# reutilizarlo
class CustomButton(ctk.CTkLabel):
    def __init__(
        self,
        master,
        text,
        images_pack: MouseEventsImagesPack,
        command: Callable[[], Any] | None = None,
    ):
        super().__init__(
            master,
            text=text,
            fg_color="transparent",
            text_color="white",
            cursor="hand2",
        )

        self.command = command
        self.images_pack = images_pack

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Down>", self.on_click)

        self.configure(image=self.images_pack.noEvent)

    # Hay que implementar el click cuando se presione el boton
    # usando la propiedad command
    def on_click(self, _):
        pass

    def on_leave(self, _):
        self.configure(image=self.images_pack.noEvent)

    def on_enter(self, _):
        self.configure(image=self.images_pack.mouseEnter)


# Boton con la imagen sin texto
class IconButton(CustomButton):
    def __init__(
        self,
        master,
        images_pack: MouseEventsImagesPack,
        command: Callable[[], Any] | None = None,
    ):
        super().__init__(master, "", images_pack, command)
