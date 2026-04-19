from typing import List

import customtkinter as ctk
import tksvg
from customtkinter import CTkFrame

from gesture import Gesture
from utils import shorten_gesture_name


class Sidebar(CTkFrame):
    def __init__(self, master, gestures: List[Gesture] = []):
        super().__init__(master, fg_color="transparent", width=200)
        self.rowconfigure(1, weight=1)

        self.gestures = gestures

        self.init_fonts()
        self.create_header_label()
        self.create_scrollbar_panel()
        self.create_add_button()

    def init_fonts(self):
        self.header_font = ctk.CTkFont(family="Proxima Nova Rg", size=25)
        self.bold_font = ctk.CTkFont(family="Proxima Nova Lt", size=16, weight="bold")

    def create_header_label(self):
        self.header_label = ctk.CTkLabel(
            self,
            height=55,
            text="Tus gestos",
            font=self.header_font,
            fg_color="transparent",
            text_color="white",
            anchor="w",
        )
        self.header_label.grid(row=0, column=0, padx=(20, 0), sticky="we")

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

    def create_add_button(self):
        add_icon = tksvg.SvgImage(file="./icons/add.svg", scaletoheight=35)

        plus = ctk.CTkButton(
            self,
            font=self.bold_font,
            text="Añadir gesto",
            image=add_icon,
            width=40,
            height=40,
            corner_radius=20,
            border_spacing=0,
            cursor="hand2",
        )
        plus.grid(column=0, row=2, padx=5, pady=13)


# DESCOMENTAR LOS TROZOS DE CODIGO PARA QUE LA CAMARAA FUNCIONE
class Camera(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.init_camera()

    def init_camera(self):
        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=0, sticky="nswe")

        # self.cap = cv2.VideoCapture(0, cv2.CAP_ANY)
        # time.sleep(0.6)

        # if not self.cap.isOpened():
        #     print("ERROR - Not opened")

        # self.show_frames()

    def show_frames(self):
        # ret, frame = self.cap.read()
        # if ret:
        #     cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     img = Image.fromarray(cv2image)
        #     self.camera_frames.configure(image=ctk.CTkImage(img, size=(500, 500)))

        # self.camera_frames.after(20, self.show_frames)

        pass

    def on_closing(self):
        # self.cap.release()
        # self.destroy()
        pass
