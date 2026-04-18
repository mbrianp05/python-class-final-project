from typing import List

import customtkinter as ctk
import tksvg
from customtkinter import CTkFrame

from gesture import Gesture


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
        self.header_font = ctk.CTkFont(size=22, weight="bold")
        self.bold_font = ctk.CTkFont(weight="bold", size=17)

    def create_header_label(self):
        self.header_label = ctk.CTkLabel(
            self,
            height=60,
            text="Lista de Gestos",
            font=self.header_font,
            fg_color="transparent",
        )
        self.header_label.grid(row=0, column=0, sticky="we")

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

        for i in range(10):
            item = ctk.CTkLabel(
                self.scrollable_frame,
                height=50,
                text="  Gesto " + str(i + 1),
                image=generic_gesture_icon,  # type: ignore
                fg_color="transparent",
                corner_radius=50,
                compound="left",
                font=self.bold_font,
            )
            item.grid(row=i, column=0, padx=0, pady=0, sticky="ew")

    def create_add_button(self):
        # Para crear nuevos gestos
        plus = ctk.CTkButton(
            self,
            font=self.bold_font,
            height=30,
            text="+",
            corner_radius=15,
        )
        plus.grid(column=0, row=2, padx=5, sticky="we", pady=5)
