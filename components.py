import time
from typing import Callable, List

import customtkinter as ctk
import cv2
import tksvg
from customtkinter import CTkFrame
from PIL import Image

from gesture import Gesture
from utils import shorten_gesture_name

from .types import MouseEventsImagesPack


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
            text="Tus gestos",
            font=self.header_font,
            fg_color="transparent",
            text_color="white",
            anchor="w",
        )
        self.header_label.grid(row=0, column=0, sticky="we")

        self.gear_icon = tksvg.SvgImage(file="./icons/gear.svg", scaletoheight=26)
        self.gear_icon_darker = tksvg.SvgImage(
            file="./icons/gear_darker.svg", scaletoheight=26
        )

        self.configure_gestures_label = ctk.CTkLabel(
            self.header,
            text="",
            fg_color="transparent",
            text_color="white",
            cursor="hand2",
            image=self.gear_icon,  # type: ignore
        )
        self.configure_gestures_label.grid(row=0, column=1, pady=(5, 0))

        self.configure_gestures_label.bind("<Enter>", self.on_enter)
        self.configure_gestures_label.bind("<Leave>", self.on_leave)

    def on_leave(self, _):
        self.configure_gestures_label.configure(image=self.gear_icon)

    def on_enter(self, _):
        self.configure_gestures_label.configure(image=self.gear_icon_darker)

    def create_scrollbar_panel(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            orientation="vertical",
            fg_color="transparent",
        )
        self.scrollable_frame.grid(row=1, column=0, padx=0, pady=0, sticky="ns")
        self.display_gestures_list()

    def display_gestures_list(self):
        generic_gesture_icon = tksvg.SvgImage(
            file="./icons/generic-gesture.svg", scaletoheight=25
        )

        for i, gesture in enumerate(self.gestures):
            name = shorten_gesture_name(gesture.name)

            item = ctk.CTkLabel(
                self.scrollable_frame,
                height=45,
                text=f"  {name}",  # el espacio es para que el texto no se vea tan pegado al icono
                image=generic_gesture_icon,  # type: ignore
                fg_color="transparent",
                compound="left",
                font=self.bold_font,
                anchor="w",
            )
            item.grid(row=i, column=0, padx=(10, 0), pady=0, sticky="ew")


class Camera(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=0, sticky="nswe")

        self.init_camera()

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

        pass

    def on_closing(self):
        self.cap.release()
        self.destroy()
        pass


# El botón normal de Customtkinter es más limitado
# en cuanto a la personalización por eso hice este
# este componente botones sin color de fondo y con
# iconos que cambian segun los eventos del mouse
class CustomButton(ctk.CTkLabel):
    def __init__(
        self,
        master,
        text,
        images_pack: MouseEventsImagesPack,
        command: Callable[[], None] | None = None,
    ):
        super().__init__(
            master,
            text=text,
            fg_color="transparent",
            text_color="white",
            cursor="hand2",
            image=images_pack.no_event,
        )

        self.command = command
        self.images_pack = images_pack

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_leave(self, _):
        self.configure(image=self.images_pack.mouseLeave)

    def on_enter(self, _):
        self.configure(image=self.images_pack.mouseEnter)
