import time
from typing import Any, Callable

import customtkinter as ctk
import cv2
import tksvg
from customtkinter import CTkFrame
from PIL import Image

import loader
from gesture import GestureRecognition
from services import fetch_gestures
from uiclasses import HighlightTransition, MouseEventsImagesPack
from utils import shorten_gesture_name


class Sidebar(CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", width=200)
        self.gestures = fetch_gestures()

        self.set_layout()
        self.init_fonts()
        self.create_header()
        self.create_scrollbar_panel()

    def set_layout(self):
        self.rowconfigure(1, weight=1)

    def init_fonts(self):
        fonts = loader.get_fonts()

        self.header_font = fonts["title"]
        self.bold_font = fonts["bold"]

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
        self.header_label.grid(row=0, column=0, sticky="we", padx=(10, 0))

        icons = loader.get_icons()

        images_pack = MouseEventsImagesPack(
            noEvent=icons["gear"],
            mouseEnter=icons["gear_darker"],
        )

        self.configure_gestures_label = IconButton(self.header, images_pack=images_pack)
        self.configure_gestures_label.grid(row=0, column=1, pady=(5, 0))

    def create_scrollbar_panel(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            orientation="vertical",
            fg_color="transparent",
        )
        self.scrollable_frame.grid(row=1, column=0, padx=0, pady=0, sticky="ns")
        self.display_gestures_list()

    def display_gestures_list(self):
        for i, gesture in enumerate(self.gestures):
            item = ActivationFeedbackLabel(
                self.scrollable_frame,
                text=shorten_gesture_name(gesture.name),
                font=loader.get_fonts()["bold"],
                image=loader.get_icons()["generic-gesture"],
                transition=HighlightTransition(
                    fg_color="#3A8CFF", text_color="#fff", duration=500, pulses=2
                ),
            )

            item.grid(row=i, column=0, padx=(0, 0), pady=0, sticky="ew")

    def highlight_gesture(self, index: int = 0):
        labels = list(self.scrollable_frame.children.values())

        if index < len(labels):  # type: ignore
            labels[index].highlight()  # type: ignore
        else:
            raise IndexError(f"Index [{index}] out of bounds.")


class Camera(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.recognizer = GestureRecognition(fetch_gestures())
        self.configure(fg_color="transparent")

        self.set_layout()

        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=0, sticky="nswe")

        # self.init_camera()

    def set_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def init_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        time.sleep(0.6)

        if not self.cap.isOpened():
            raise Exception("App cannot launch without a camera")

        self.load_frames()

    def load_frames(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            self.camera_frames.configure(image=ctk.CTkImage(img, size=(600, 600)))

        self.recognizer.exec_on_detection(
            frame
        )  # Llamar cada vez que el frame se actualiza por eso se ejecuta en esta funcion
        self.camera_frames.after(20, self.load_frames)

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
        self.bind("<ButtonRelease-1>", self.on_click)

        self.configure(image=self.images_pack.noEvent)

    # Hay que implementar el click cuando se presione el boton
    # usando la propiedad command
    def on_click(self, _):
        if self.command is not None:
            self.command()

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


# Label con resaltado para lista de gestos
class ActivationFeedbackLabel(ctk.CTkLabel):
    def __init__(
        self,
        master,
        text: str,
        transition: HighlightTransition,
        font: ctk.CTkFont | None = None,
        image: tksvg.SvgImage | None = None,
    ):
        super().__init__(
            master,
            text=f"  {text}",  # el espacio es para que el texto no se vea tan pegado al icono
            font=font,
            image=image,  # type: ignore
            height=45,
            fg_color="transparent",
            compound="left",
            anchor="w",
            corner_radius=30,
        )
        self.transition = transition

    def normalize(self):
        self.configure(text_color="#DCE4EE", fg_color="transparent")

    def glow(self):
        self.configure(
            fg_color=self.transition.fg_color, text_color=self.transition.text_color
        )

    def highlight(self):
        if not self.transition.is_running:
            self.transition.is_running = True
            timer = int(self.transition.duration / self.transition.pulses)
            for i in range(self.transition.pulses):
                self.after((2 * i) * timer, lambda: self.glow())

                self.after((2 * i + 1) * timer, lambda: self.normalize())

            self.after(
                (2 * self.transition.pulses) * timer,
                lambda: setattr(
                    self.transition, "is_running", not self.transition.is_running
                ),
            )
