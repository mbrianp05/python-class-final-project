import time
from typing import Any, Callable, cast

import customtkinter as ctk
import cv2
import tksvg
from customtkinter import CTkFrame
from PIL import Image

import loader
from gesture import Gesture, GestureRecognition
from services import fetch_gestures
from uiclasses import HighlightTransition, MouseEventsImagesPack, View
from utilityclasses import Finger
from utils import shorten_gesture_name


class Sidebar(CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent", width=230)
        self.gestures = fetch_gestures()

        self.controller = controller

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

        self.configure_gestures_label = IconButton(
            self.header,
            images_pack=images_pack,
            command=lambda: self.controller.show(View.SETTINGS_VIEW),
        )
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

        self.configure(fg_color="transparent")

        self.set_layout()

        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=0, sticky="nswe")

        # self.init_camera()

    def set_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def init_camera(self):
        self.recognizer = GestureRecognition(fetch_gestures())

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
        if getattr(self, "cap", None) is not None:
            self.cap.release()


class SettingsHeader(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.configure(fg_color="transparent")

        self.controller = controller
        self.display_go_back_button()
        self.display_title()

    def display_title(self):
        self.title_label = ctk.CTkLabel(
            self,
            text="Configurar gestos",
            font=loader.get_fonts()["title"],
            fg_color="transparent",
        )
        self.title_label.grid(row=0, column=1, padx=0, pady=10)

    def display_go_back_button(self):
        icons = loader.get_icons(30)

        pack = MouseEventsImagesPack(
            noEvent=icons["arrow_left"], mouseEnter=icons["arrow_left_darker"]
        )
        self.nav_button = IconButton(
            self,
            images_pack=pack,
            command=lambda: self.controller.show(View.DETECTION_VIEW),  # type: ignore
        )
        self.nav_button.grid(row=0, column=0, padx=10, pady=10)


class SettingsForm(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")

        self.gestures = fetch_gestures()
        self.current_gesture: Gesture | None = (
            self.gestures[0] if len(self.gestures) > 0 else None
        )

        self.form_panel = ctk.CTkFrame(self)
        self.form_panel.grid(row=1, column=0, pady=50)

        self.display_current_gesture_selector()
        self.display_active_hands_selector()
        self.display_visible_fingers_selector()
        self.display_save_settings_button()

        self.adjust_current_configuration_display()

    def display_current_gesture_selector(self):
        self.selector = ctk.CTkComboBox(
            self, values=[g.name for g in self.gestures], width=200
        )
        self.selector.grid(row=0, column=0)

    def update_config(self):
        if self.current_gesture is None:
            return

        # self.adjust_current_configuration_display()

    def display_active_hands_selector(self):
        self.left_hand_icon = ctk.CTkLabel(self.form_panel, text="Mano izquierda")
        self.left_hand_icon.grid(row=0, column=0, sticky="w")

        self.right_hand_icon = ctk.CTkLabel(self.form_panel, text="Mano derecha")
        self.right_hand_icon.grid(row=0, column=1, sticky="w")

        self.active_left_hand = ctk.CTkCheckBox(
            self.form_panel,
            text="",
            command=self.update_config,
            onvalue="on",
            offvalue="off",
        )
        self.active_left_hand.grid(row=1, column=0)

        self.active_right_hand = ctk.CTkCheckBox(self.form_panel, text="")
        self.active_right_hand.grid(row=1, column=1)

    def no_settings_status(self):
        self.active_left_hand.deselect()
        self.active_left_hand.deselect()

        for n, ch in self.checkbox_collection_panel.children.items():
            if n.startswith("!ctkcheckbox"):
                cast(ctk.CTkCheckBox, ch).deselect()

    # Configura el formulario de forma que concuerde con la
    # informacion del gesto que se esta configurando
    def adjust_current_configuration_display(self):
        if self.current_gesture is None:
            self.no_settings_status()

            return

        hands_fingers = self.current_gesture.settings.visibleFingers

        # ADJUST HANDS NUMBER

        is_left_active, is_right_active = self.current_gesture.settings.hands

        if is_left_active:
            self.active_left_hand.select()

        if is_right_active:
            self.active_right_hand.select()

        all_checkboxes = [
            ch
            for n, ch in self.checkbox_collection_panel.children.items()
            if n.startswith("!ctkcheckbox")
        ]

        # ADJUST FINGERS
        for idx, ch in enumerate(all_checkboxes):
            # NOTA: AUQUE VISUALMENTE LOS CHECKBOXES DE CADA MANO ESTAN EN DOS COLUMNAS
            # EL .children LOS DEVUELVE EN FILA POR LO QUE SE ALTERNA EL CHECKBOX DE LA MANO
            # IZQUIERDA CON EL DE LA DERECHA POR ESO ES QUE SE CALCULA ASI EL INDICE DE LA MANO
            hand_index = idx % 2
            hand_fingers = hands_fingers[hand_index]

            checkbox_type = cast(ctk.CTkCheckBox, ch)

            if not is_left_active and hand_index == 0:
                checkbox_type.configure(state=ctk.DISABLED)
                continue

            if not is_right_active and hand_index == 1:
                checkbox_type.configure(state=ctk.DISABLED)
                continue

            if hand_fingers.count(getattr(ch, "stands_for")) == 1:
                checkbox_type.select()

    def display_visible_fingers_selector(self):
        fingers_names = ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]
        fingers_repr = [
            Finger.THUMB_FINGER,
            Finger.INDEX_FINGER,
            Finger.MIDDLE_FINGER,
            Finger.RING_FINGER,
            Finger.LITTLE_FINGER,
        ]

        self.checkbox_collection_panel = ctk.CTkFrame(
            self.form_panel, fg_color="transparent"
        )
        self.checkbox_collection_panel.grid(row=2, column=0, pady=40, sticky="we")
        self.columnconfigure((0, 1), weight=1)

        self.left_hand_fingers_selector = []
        self.right_hand_fingers_slector = []

        for idx, name in enumerate(fingers_names):
            for hand_number in range(2):
                checkbox = ctk.CTkCheckBox(self.checkbox_collection_panel, text=name)
                checkbox.grid(row=idx, column=hand_number, pady=10)

                # GUARDAR QUE DEDO REPRESENTA EL CHECKBOX
                setattr(checkbox, "stands_for", fingers_repr[idx])

    def display_save_settings_button(self):
        self.save_button = ctk.CTkButton(self, text="Guardar gesto")
        self.save_button.grid(row=2, column=0, sticky="w")


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
