import copy
import time
from typing import Any, Callable, List, Literal, cast

import customtkinter as ctk
import cv2
from customtkinter import CTkFrame
from PIL import Image

from actions import get_actions_parameter_type
from gesture import Gesture, GestureData, GestureRecognition, HandProfile
from loader import AssetRegistry
from parampicker import ParamPicker
from services import add_gesture, fetch_gestures, remove_gesture, update_gesture
from uiclasses import MessageType, MouseEventsImagesPack, View
from utilityclasses import Action, Finger, FormState, ParamType
from utils import (
    confirm,
    get_action_from_repr,
    get_hand_profile_from_repr,
    get_or_default,
    get_repr_for_action,
    get_repr_for_hand_profile,
    messagebox_error,
    messagebox_info,
    shorten_gesture_name,
)


class GestureItem(ctk.CTkFrame):
    """
    Fila de la lista de gestos del Sidebar.

    Contiene el icono de la accion, el nombre del gesto y su descripcion.
    El metodo highlight() hace parpadear el fondo dos veces entre
    _HIGHLIGHT_COLOR y "transparent".
    """

    _HIGHLIGHT_COLOR = "#262624"
    _PULSE_MS = 250  # duracion de cada semiciclo (encendido / apagado)
    _PULSES = 2  # numero de parpadeos completos

    def __init__(
        self,
        master,
        gesture,
        icon,
        icon_bg_color: str,
        description: str,
    ):
        super().__init__(master, fg_color="transparent")

        self._is_animating = False

        self._build(gesture, icon, icon_bg_color, description)

    # ------------------------------------------------------------------ #
    # Construccion de widgets                                              #
    # ------------------------------------------------------------------ #

    def _build(self, gesture, icon, icon_bg_color: str, description: str) -> None:
        icon_box = ctk.CTkFrame(self, fg_color=icon_bg_color, corner_radius=10)

        description_frame = ctk.CTkFrame(self, fg_color="transparent")
        description_frame.rowconfigure((0, 1), weight=1)

        name_label = ctk.CTkLabel(
            description_frame,
            text=shorten_gesture_name(gesture.name),
            font=AssetRegistry.fonts(16)["regular"],
            height=10,
        )
        name_label.grid(row=0, column=1, sticky="wns", pady=(2, 0))

        desc_label = ctk.CTkLabel(
            description_frame,
            text=description,
            font=AssetRegistry.fonts(13)["regular"],
            text_color="#999",
            height=10,
        )
        desc_label.grid(row=1, column=1, sticky="wns", pady=4)

        icon_label = ctk.CTkLabel(icon_box, text="", image=icon, height=36)  # type: ignore
        icon_label.grid(row=0, column=0, padx=8, sticky="ns")

        icon_box.grid(row=0, column=0, padx=7, pady=4, rowspan=2)
        description_frame.grid(row=0, column=1, sticky="we", padx=7, pady=4)

    # ------------------------------------------------------------------ #
    # Animacion de parpadeo                                                #
    # ------------------------------------------------------------------ #

    def highlight(self) -> None:
        """Parpadea el fondo del item dos veces y vuelve a transparent."""
        if self._is_animating:
            return

        self._is_animating = True
        self._run_pulse(remaining=self._PULSES * 2)

    def _run_pulse(self, remaining: int) -> None:
        if remaining <= 0:
            self.configure(fg_color="transparent")
            self._is_animating = False
            return

        # semiciclos pares → encendido, impares → apagado
        color = self._HIGHLIGHT_COLOR if remaining % 2 == 0 else "transparent"
        self.configure(fg_color=color)
        self.after(self._PULSE_MS, lambda: self._run_pulse(remaining - 1))


class Sidebar(CTkFrame):
    _BG_COLOR = "#30302e"
    _WIDTH = 260

    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent", width=self._WIDTH)
        self.grid_propagate(False)
        self.gestures = fetch_gestures()

        self.controller = controller
        self._items: List[GestureItem] = []

        self.icons = AssetRegistry.icons()
        fonts = AssetRegistry.fonts()

        self.header_font = fonts["title"]
        self.bold_font = fonts["bold"]

        self.set_layout()
        self.create_header()
        self.create_scrollbar_panel()

    def set_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def create_header(self):
        self.header = ctk.CTkFrame(self, corner_radius=0, fg_color=self._BG_COLOR)
        self.header.grid(row=0, column=0, padx=0, sticky="we")

        self.header_label = ctk.CTkLabel(
            self.header,
            height=50,
            text="Gestos",
            font=self.header_font,
            fg_color="transparent",
            anchor="w",
        )
        self.header_label.grid(row=0, column=1, pady=(0, 1), sticky="wens", padx=15)

        icons = self.icons  # ya en caché

        images_pack = MouseEventsImagesPack(
            noEvent=icons["gear"],
            mouseEnter=icons["gear_darker"],
        )

        self.configure_gestures_label = CustomButton(
            self.header,
            images_pack=images_pack,
            command=lambda: self.controller.show(View.SETTINGS_VIEW),
        )
        self.configure_gestures_label.grid(row=0, column=0, sticky="wsn")

    def create_scrollbar_panel(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, orientation="vertical", corner_radius=0, fg_color=self._BG_COLOR
        )
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.grid(row=1, column=0, pady=(1, 0), sticky="nsew")

    def _get_icon(self, gesture: Gesture):
        action_icon_dict = {
            Action.TAKE_SCREENSHOT: self.icons["screenshot"],
            Action.OPEN_FILE: self.icons["open_file"],
            Action.OPEN_FOLDER: self.icons["open_folder"],
            Action.RUN_PROGRAM: self.icons["run_program"],
            Action.SET_WIFI_STATE: self.icons["set_wifi"],
            Action.SET_VOLUME: self.icons["set_volume"],
        }

        return get_or_default(action_icon_dict, gesture.effect, None)

    def _get_color(self, gesture: Gesture):
        color_dict = {
            Action.SET_WIFI_STATE: "#313e42",
            Action.TAKE_SCREENSHOT: "#28323f",
            Action.OPEN_FOLDER: "#2a3632",
            Action.RUN_PROGRAM: "#43322c",
            Action.SET_VOLUME: "#3a333e",
            Action.OPEN_FILE: "#473d2d",
        }

        return get_or_default(color_dict, gesture.effect, "transparent")

    def _get_description(self, gesture: Gesture):
        color_dict = {
            Action.SET_WIFI_STATE: "Cambiar estado del WIFI",
            Action.TAKE_SCREENSHOT: "Captura de pantalla",
            Action.OPEN_FOLDER: "Abrir carpeta",
            Action.RUN_PROGRAM: "Abrir programa",
            Action.SET_VOLUME: "Cambiar el volumen",
            Action.OPEN_FILE: "Abrir archivo",
        }

        return get_or_default(color_dict, gesture.effect, "")

    def display_gestures_list(self):
        if len(self._items) > 0:
            return

        for i, gesture in enumerate(self.gestures):
            item = GestureItem(
                self.scrollable_frame,
                gesture=gesture,
                icon=self._get_icon(gesture),
                icon_bg_color=self._get_color(gesture),
                description=self._get_description(gesture),
            )
            item.grid(row=i, column=0, pady=(7, 0), padx=6, sticky="we")
            self._items.append(item)

    def highlight_gesture(self, index: int = 0):
        if index < len(self._items):
            self._items[index].highlight()

    def update(self):
        self.display_gestures_list()

        for item in self._items:
            item.destroy()
            del item

        self._items = []

        self.gestures = fetch_gestures()
        self.display_gestures_list()


class Camera(ctk.CTkFrame):
    # Colores del badge de bloqueo
    _BADGE_BLOCKED_BG = "#391010"
    _BADGE_BLOCKED_TEXT = "#ff6b6b"
    _BADGE_OK_BG = "#0f2e1e"
    _BADGE_OK_TEXT = "#4caf93"

    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")

        self.set_layout()

        self.camera_frames = ctk.CTkLabel(self, text="")
        self.camera_frames.grid(row=0, column=0, sticky="nswe")

        self._build_detection_badge()

        # self.init_camera()

    def set_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _build_detection_badge(self) -> None:
        """Crea el badge superpuesto que indica el estado de la detección."""
        fonts = AssetRegistry.fonts(14)
        icons = AssetRegistry.icons()

        self.detection_badge = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color=self._BADGE_OK_BG,
            border_width=1,
            border_color=self._BADGE_OK_TEXT,
        )

        self._badge_icon = ctk.CTkLabel(
            self.detection_badge,
            text="",
            image=icons["generic-gesture"],  # type: ignore
            fg_color="transparent",
        )
        self._badge_icon.grid(row=0, column=0, padx=(10, 4), pady=4)

        self._badge_label = ctk.CTkLabel(
            self.detection_badge,
            text="Detección activa",
            font=fonts["regular"],
            text_color=self._BADGE_OK_TEXT,
            fg_color="transparent",
        )
        self._badge_label.grid(row=0, column=1, padx=(0, 12), pady=4)

        self.detection_badge.place(relx=1.0, rely=0.0, anchor="ne", x=-12, y=12)

    def _update_detection_badge(self) -> None:
        """Sincroniza el badge con can_do_gesture del recognizer en cada frame."""
        blocked = not self.recognizer.can_do_gesture

        bg = self._BADGE_BLOCKED_BG if blocked else self._BADGE_OK_BG
        fg = self._BADGE_BLOCKED_TEXT if blocked else self._BADGE_OK_TEXT
        text = "Detección bloqueada" if blocked else "Detección activa"

        self.detection_badge.configure(fg_color=bg, border_color=fg)
        self._badge_label.configure(text=text, text_color=fg)

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
            self.camera_frames.configure(
                image=ctk.CTkImage(img, size=(600, 600)), compound="top", pady=5
            )

        self.recognizer.exec_on_detection(frame, self.master.sidebar.highlight_gesture)
        self._update_detection_badge()
        self.camera_frames.after(200, self.load_frames)

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
            font=AssetRegistry.fonts()["title"],
            fg_color="transparent",
            height=50,
        )
        self.title_label.grid(row=0, column=1, padx=15)

    def display_go_back_button(self):
        icons = AssetRegistry.icons(30)

        pack = MouseEventsImagesPack(
            noEvent=icons["arrow_left"], mouseEnter=icons["arrow_left_darker"]
        )
        self.nav_button = CustomButton(
            self,
            images_pack=pack,
            command=lambda: self.controller.show(View.DETECTION_VIEW),  # type: ignore
        )
        self.nav_button.grid(row=0, column=0, sticky="wsn")


class SettingsForm(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, orientation="vertical")

        self.configure(fg_color="transparent")
        self.gestures = fetch_gestures()

        self._is_new = False
        self._inner_state = FormState(is_valid=True)
        self._default_gesture()

        self.set_layout()

        # Columna izquierda: envuelve gesture_info_panel + form_buttons
        # rowconfigure con weight=1 en row=1 empuja form_buttons al fondo
        self._left_col = ctk.CTkFrame(self, fg_color="transparent")
        self._left_col.rowconfigure(0, weight=1)  # info panel se estira
        self._left_col.rowconfigure(1, weight=0)  # botones al fondo
        self._left_col.columnconfigure(0, weight=1)
        self._left_col.grid(row=0, column=0, sticky="nswe", padx=40, pady=(40, 40))

        self.gesture_info_panel = ctk.CTkFrame(
            self._left_col, fg_color="transparent", width=340
        )
        self.gesture_info_panel.rowconfigure((0, 1, 2, 3), pad=50)
        # weight=1 en columna 0 hace que todos los widgets con sticky="we" ocupen el mismo ancho
        self.gesture_info_panel.columnconfigure(0, weight=1)
        self.gesture_info_panel.grid(row=0, column=0, sticky="nswe")

        self.form_panel = ctk.CTkFrame(self, fg_color="transparent", width=600)
        self.form_panel.columnconfigure((0, 1), weight=1, pad=30)
        self.form_panel.grid(row=0, column=1, padx=40, pady=(40, 0))

        # form_buttons en _left_col row=1 → siempre al fondo de la columna izquierda
        self.form_buttons = ctk.CTkFrame(
            self._left_col, border_color="#262624", border_width=2
        )
        self.form_buttons.columnconfigure((0, 1, 2), weight=1)
        self.form_buttons.grid(row=1, column=0, sticky="we", pady=(10, 0))

        self.display_current_gesture_selector()
        self.display_name_field()
        self.display_active_hands_selector()
        self.display_visible_fingers_selector()
        self.display_action_selector()
        self.display_save_settings_button()
        self.display_delete_button()
        self.display_add_new_button()

        self._adjust_current_configuration_display()

    def _empty_gesture(self):
        default_action = Action.OPEN_FOLDER
        default_settings = GestureData(
            hands=(False, False),
            visibleFingers=([], []),
            profile=(None, None),
        )
        self.current_gesture = Gesture(
            id=-1,
            name="Nuevo gesto",
            settings=default_settings,
            effect=default_action,
            param=None,
        )

    def _default_gesture(self):
        if len(self.gestures) == 0:
            self._empty_gesture()
            self._is_new = True

            return

        self.current_gesture = copy.deepcopy(self.gestures[0])

    def set_layout(self):
        self.columnconfigure((1), weight=1)

    def display_action_selector(self):
        values = self.get_action_values()

        self.action_selector = ctk.CTkComboBox(
            self.gesture_info_panel,
            values=values,
            width=10,  # mínimo; sticky="we" + columnconfigure weight=1 lo expande
            height=32,
            state="readonly",
            font=AssetRegistry.fonts()["regular"],
            command=lambda _: self.change_action(),
        )
        self.action_selector.grid(row=2, column=0, sticky="we")

        self._adjust_current_gesture_effect()
        paramtype = self.get_paramtype_for_current_action()

        self.param_picker = ParamPicker(
            self.gesture_info_panel,
            paramtype=paramtype,
            initial_value=self.get_current_param_value(),
        )
        self.param_picker.grid(row=3, column=0, sticky="we")

    def change_action(self):
        self.update_config()
        self._change_param_type_form(change_value=False)

    def get_current_param_value(self) -> float | int | str | bool | None:
        return self.current_gesture.param

    def get_paramtype_for_current_action(self) -> ParamType | None:
        action = get_action_from_repr(self.action_selector.get())

        return get_actions_parameter_type()[action]

    def _change_param_type_form(self, change_value=True):
        required_param_type = get_actions_parameter_type()[self.get_selected_action()]
        value = self.get_current_param_value()

        self.param_picker.set_param_type(required_param_type, value)

    def display_name_field(self):
        self.name_field_box = ctk.CTkFrame(self.gesture_info_panel)
        self.name_field_box.columnconfigure(1, weight=1)

        text = self.current_gesture.name
        self.name_field = ctk.CTkEntry(
            self.name_field_box,
            height=31,
            font=AssetRegistry.fonts()["regular"],
            border_color="#181818",
            fg_color="#181818",
        )
        self.name_field.insert(0, text)
        self.name_field.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="we")
        self.name_field.bind("<KeyRelease>", lambda _: self._update_name())

        self.name_label = ctk.CTkLabel(
            self.name_field_box,
            text="Nombre",
            compound="left",
            font=AssetRegistry.fonts(17)["regular"],
            image=AssetRegistry.icons(33)["mark"],  # type: ignore
        )
        self.name_label.grid(row=0, column=0, padx=10, pady=10)

        self.name_field_box.grid(row=1, column=0, sticky="we")

    def check_name(self):
        if self.current_gesture.name == "":
            self._inner_state = FormState(
                False, "El nombre del gesto no ha sido porporcionado"
            )
        else:
            self._inner_state = FormState(True, None)

    def _update_name(self):
        self.current_gesture.name = self.name_field.get().strip(" \n\r")
        self.check_name()

    # SETEA EL GESTO QUE SE ESTÁ CONFIGURANDO A PARTIR DEL VALOR
    # SELECCIONADO EN EL COMBOBOX DE LOS GESTOS
    def set_current_gesture(self):
        gesture_name = self.gesture_selector.get()
        matches = [g for g in self.gestures if g.name == gesture_name]

        # SINGNIFICA QUE EL GESTO ES NUEVO
        if len(matches) == 0:
            return

        self.add_new_button.configure(state=ctk.NORMAL)
        self.delete_button.configure(state=ctk.NORMAL)

        self.current_gesture = copy.deepcopy(matches[0])
        self._set_current_gesture_selector()
        self._adjust_current_configuration_display()
        self._change_param_type_form()

    def display_current_gesture_selector(self):
        self.gesture_selector = ctk.CTkComboBox(
            self.gesture_info_panel,
            height=31,
            width=10,
            command=lambda _: self.set_current_gesture(),
            state="readonly",
            font=AssetRegistry.fonts()["regular"],
        )

        self._set_current_gesture_selector()

        self.gesture_selector.grid(
            row=0,
            column=0,
            padx=(0, 0),
            sticky="we",
        )

    def _set_current_gesture_selector(self):
        values = [g.name for g in self.gestures]
        is_new = self.current_gesture.id == -1

        if is_new:
            values.append("")

        self.gesture_selector.configure(values=values)

        if is_new:
            self.gesture_selector.set("")
            return

        self.gesture_selector.set(self.current_gesture.name)

    def get_selected_action(self) -> Action:
        selected_action = self.action_selector.get()
        return get_action_from_repr(selected_action)

    # LEE TODOS LOS WIDGETS DEL FORMULARIO Y CAMBIA EL GESTURE DATA
    # DE ACUERDO A LA NUEVA CONFIGURACION
    def update_config(self):
        settings = self.current_gesture.settings

        # ACTUALIZAR LAS MANOS
        is_left_hand_active = bool(self.left_hand_activator.get())
        is_right_hand_active = bool(self.right_hand_activator.get())

        settings.hands = (is_left_hand_active, is_right_hand_active)

        # ACTUALIZAR EL PROFILE
        left_hand_profile = get_hand_profile_from_repr(
            self.left_hand_profile_selector.get()
        )
        right_hand_profile = get_hand_profile_from_repr(
            self.right_hand_profile_selector.get()
        )

        settings.profile = (left_hand_profile, right_hand_profile)

        # ACTUALIZAR LOS DEDOS VISIBLES MARCADOS
        all_checkboxes = self.get_fingers_selector_checkboxes()
        hands_fingers = settings.visibleFingers

        for idx, ch in enumerate(all_checkboxes):
            hand_index = idx % 2
            hand_fingers = hands_fingers[hand_index]
            finger_reptr = getattr(ch, "stands_for")

            if bool(ch.get()) and finger_reptr not in hand_fingers:
                hand_fingers.append(finger_reptr)

            if not bool(ch.get()) and finger_reptr in hand_fingers:
                hand_fingers.remove(finger_reptr)

        # SI UNA DE LAS MANOS SE DESACTIVAN QUITAR LOS DEDOS VISIBLES
        # DE ESA MANO
        left_hand_visible_fingers, right_hand_visible_fingers = settings.visibleFingers
        new_visible_fingers = {
            "left": left_hand_visible_fingers,
            "right": right_hand_visible_fingers,
        }

        if not is_left_hand_active:
            new_visible_fingers["left"] = []

        if not is_right_hand_active:
            new_visible_fingers["right"] = []

        settings.visibleFingers = (
            new_visible_fingers["left"],
            new_visible_fingers["right"],
        )

        #  ACTUALIZAR EL ACTION
        self.current_gesture.effect = self.get_selected_action()

        self._adjust_current_configuration_display()

    def get_hand_profile_values(self):
        profiles = [
            None,
            HandProfile.PALM,
            HandProfile.FRONT,
        ]

        return [get_repr_for_hand_profile(p) for p in profiles]

    def get_action_values(self):
        actions = [
            Action.OPEN_FILE,
            Action.OPEN_FOLDER,
            Action.TAKE_SCREENSHOT,
            Action.RUN_PROGRAM,
            Action.SET_VOLUME,
            Action.SET_WIFI_STATE,
        ]

        return [get_repr_for_action(p) for p in actions]

    def display_active_hands_selector(self):
        icons = AssetRegistry.icons(scale=260)
        left_images_pack = MouseEventsImagesPack(
            noEvent=icons["hand-1"], mouseEnter=icons["hand-1-darker"]
        )
        right_images_pack = MouseEventsImagesPack(
            noEvent=icons["hand-2"], mouseEnter=icons["hand-2-darker"]
        )

        self.left_hand_icon = ImagesEffectLabel(
            self.form_panel, text="", images_pack=left_images_pack
        )
        self.left_hand_icon.grid(row=0, column=0, sticky="w")

        self.right_hand_icon = ImagesEffectLabel(
            self.form_panel, text="", images_pack=right_images_pack
        )
        self.right_hand_icon.grid(row=0, column=1, sticky="e")

        checkboxes = []

        for i in range(2):
            ch = ctk.CTkCheckBox(
                self.form_panel,
                text="",
                command=self.update_config,
                font=AssetRegistry.fonts()["regular"],
            )
            ch.grid(row=1, column=i, pady=10)
            checkboxes.append(ch)

        (self.left_hand_activator, self.right_hand_activator, *_) = checkboxes

        # HANDS PROFILE CONFIGURATION
        self.profile_label = RegularLabel(
            self.form_panel, text="PERFIL DE LAS MANOS", size=21, variant="bold"
        )
        self.profile_label.grid(row=2, column=0, pady=20, columnspan=2)

        values = self.get_hand_profile_values()

        self.left_hand_profile_selector = ctk.CTkComboBox(
            self.form_panel,
            width=250,
            height=31,
            state="readonly",
            values=values,
            command=lambda _: self.update_config(),
            font=AssetRegistry.fonts()["regular"],
        )
        self.left_hand_profile_selector.set(values[0])
        self.left_hand_profile_selector.grid(row=3, column=0)

        self.right_hand_profile_selector = ctk.CTkComboBox(
            self.form_panel,
            width=250,
            height=31,
            state="readonly",
            values=values,
            command=lambda _: self.update_config(),
            font=AssetRegistry.fonts()["regular"],
        )
        self.right_hand_profile_selector.set(values[0])
        self.right_hand_profile_selector.grid(row=3, column=1)

    def get_fingers_selector_checkboxes(self) -> List[ctk.CTkCheckBox]:
        return [
            cast(ctk.CTkCheckBox, ch)
            for n, ch in self.checkbox_collection_panel.children.items()
            if n.startswith("!ctkcheckbox")
        ]

    # Configura el formulario de forma que concuerde con la
    # informacion del gesto que se esta configurando
    def _adjust_current_configuration_display(self):
        hands_fingers = self.current_gesture.settings.visibleFingers

        # ADJUST GESTURE NAME
        self.name_field.delete(0, "end")
        self.name_field.insert(0, self.current_gesture.name)

        self.check_name()

        # ADJUST HANDS NUMBER AND HAND PROFILE
        is_left_active, is_right_active = self.current_gesture.settings.hands
        set_profile_left, set_profile_right = self.current_gesture.settings.profile

        if not is_left_active and not is_right_active:
            self._inner_state = FormState(
                False, "Al menos una de las dos manos debe ser visible en el gesto"
            )
        else:
            # Resetear el state
            self._inner_state = FormState(True, None)

        form_fields = {
            "hand_activator": (self.left_hand_activator, self.right_hand_activator),
            "hand_profile_selector": (
                self.left_hand_profile_selector,
                self.right_hand_profile_selector,
            ),
            "hand_icon": (self.left_hand_icon, self.right_hand_icon),
            "setted_profile": (set_profile_left, set_profile_right),
        }

        values = {
            "activator": {
                True: "select",
                False: "deselect",
            },
            "profile": {
                True: [
                    get_repr_for_hand_profile(set_profile_left),
                    get_repr_for_hand_profile(set_profile_right),
                ],
                False: [self.get_hand_profile_values()[0]] * 2,
            },
            "image": {
                True: "noEvent",
                False: "mouseEnter",
            },
            "state": {True: "readonly", False: ctk.DISABLED},
        }

        for idx, is_active in enumerate([is_left_active, is_right_active]):
            getattr(
                form_fields["hand_activator"][idx],
                values["activator"][is_active],
            )()
            form_fields["hand_profile_selector"][idx].set(
                values["profile"][is_active][idx]
            )
            form_fields["hand_icon"][idx].activate_image(values["image"][is_active])
            form_fields["hand_profile_selector"][idx].configure(
                state=values["state"][is_active]
            )

        all_checkboxes = self.get_fingers_selector_checkboxes()
        is_hand_active = [is_left_active, is_right_active]

        # ADJUST FINGERS
        for idx, ch in enumerate(all_checkboxes):
            # NOTA: AUQUE VISUALMENTE LOS CHECKBOXES DE CADA MANO ESTAN EN DOS COLUMNAS
            # EL .children LOS DEVUELVE EN FILA POR LO QUE SE ALTERNA EL CHECKBOX DE LA MANO
            # IZQUIERDA CON EL DE LA DERECHA POR ESO ES QUE SE CALCULA ASI EL INDICE DE LA MANO
            hand_index = idx % 2
            hand_fingers = hands_fingers[hand_index]

            if not is_hand_active[hand_index]:
                ch.deselect()
                ch.configure(state=ctk.DISABLED)
            else:
                if hand_fingers.count(getattr(ch, "stands_for")) == 1:
                    ch.select()

                ch.configure(state=ctk.NORMAL)

        # ADJUST ACTION
        self._adjust_current_gesture_effect()

    def _adjust_current_gesture_effect(self):
        self.action_selector.set(get_repr_for_action(self.current_gesture.effect))

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
        self.checkbox_collection_panel.grid(
            row=4, column=0, pady=40, sticky="we", columnspan=2
        )
        self.checkbox_collection_panel.columnconfigure((0, 1), weight=1)

        self.left_hand_fingers_selector = []
        self.right_hand_fingers_slector = []

        for idx, name in enumerate(fingers_names):
            for hand_number in range(2):
                checkbox = ctk.CTkCheckBox(
                    self.checkbox_collection_panel,
                    text=name,
                    command=self.update_config,
                    font=AssetRegistry.fonts()["regular"],
                )
                checkbox.grid(row=idx, column=hand_number, pady=10)

                # GUARDAR QUE DEDO REPRESENTA EL CHECKBOX
                setattr(checkbox, "stands_for", fingers_repr[idx])

    def index_of_local_gesture(self) -> int:
        idx = -1

        for i, g in enumerate(self.gestures):
            if g.id == self.current_gesture.id:
                idx = i

        return idx

    def update_local_gesture(self):
        idx = self.index_of_local_gesture()

        if idx == -1:
            self.gestures.append(self.current_gesture)
        else:
            self.gestures[idx] = self.current_gesture

        self._set_current_gesture_selector()

    def save_new_config(self):
        inner_state = self._inner_state
        outer_state = self.param_picker.get_state()

        if inner_state.is_valid and outer_state.is_valid:
            self.delete_button.configure(state=ctk.NORMAL)
            self.add_new_button.configure(state=ctk.NORMAL)

            self.current_gesture.param = self.param_picker.get_value()

            if self.current_gesture.id != -1:
                update_gesture(self.current_gesture)
            else:
                tmp = add_gesture(self.current_gesture)

                if tmp is not None:
                    self.current_gesture = tmp

            self.update_local_gesture()

        self.feedback()

    # PENDIENTE DE IMPLEMENTACIÓN
    def feedback(self):
        outer_state = self.param_picker.get_state()

        state = self._inner_state.is_valid and outer_state.is_valid
        type = MessageType.SUCCESS if state else MessageType.ERROR

        msg = "Gesto guardado correctamente"

        if not self._inner_state.is_valid:
            msg = self._inner_state.error_message
        elif not outer_state.is_valid:
            msg = outer_state.error_message

        if type == MessageType.SUCCESS:
            messagebox_info("Éxito", "Gesto guardado exitosamente")
        else:
            messagebox_error("Error", msg or "")

    def display_save_settings_button(self):
        self.save_button = ctk.CTkButton(
            self.form_buttons,
            height=31,
            width=120,
            text="Guardar",
            text_color="#4caf93",
            hover_color="#2a3632",
            fg_color="#0f2e1e",
            font=AssetRegistry.fonts()["regular"],
            image=AssetRegistry.icons()["save"],
            command=self.save_new_config,
        )
        self.save_button.grid(row=0, column=0, sticky="we", padx=8, pady=10)

    def _remove_local_gesture(self):
        self.gestures = [
            gesture
            for gesture in self.gestures
            if gesture.id != self.current_gesture.id
        ]

    def _delete_current_gesture(self):
        if self.current_gesture.id == -1:
            return

        result = True

        if confirm("¿Deseas realmente eliminar este gesto?"):
            self._remove_local_gesture()
            result = remove_gesture(self.current_gesture)
        else:
            return

        if result:
            if len(self.gestures) > 0:
                self._default_gesture()

                self._set_current_gesture_selector()
                self._adjust_current_configuration_display()
                self._change_param_type_form()
            else:
                self._new_gesture()
                self.delete_button.configure(state=ctk.DISABLED)
                self.add_new_button.configure(state=ctk.DISABLED)
        else:
            messagebox_error("Error", "No se pudo eliminar el gesto")

    def display_delete_button(self):
        self.delete_button = ctk.CTkButton(
            self.form_buttons,
            height=31,
            width=120,
            text="Eliminar",
            fg_color="#391010",
            text_color="#ff6b6b",
            hover_color="#4d1515",
            font=AssetRegistry.fonts()["regular"],
            image=AssetRegistry.icons()["trash"],
            command=self._delete_current_gesture,
            state=ctk.NORMAL if not self._is_new else ctk.DISABLED,
        )
        self.delete_button.grid(row=0, column=1, sticky="we", padx=8, pady=10)

    def _new_gesture(self) -> None:
        self._empty_gesture()

        self.delete_button.configure(state=ctk.DISABLED)
        self.add_new_button.configure(state=ctk.DISABLED)

        ptype = get_actions_parameter_type()[self.current_gesture.effect]

        self.param_picker.set_param_type(ptype, None)
        self._set_current_gesture_selector()
        self._adjust_current_configuration_display()

    def display_add_new_button(self):
        self.add_new_button = ctk.CTkButton(
            self.form_buttons,
            height=31,
            text="Nuevo gesto",
            font=AssetRegistry.fonts()["regular"],
            command=self._new_gesture,
            image=AssetRegistry.icons()["add"],
            state=ctk.NORMAL if not self._is_new else ctk.DISABLED,
        )
        self.add_new_button.grid(row=0, column=2, sticky="we", padx=8, pady=10)


class ImagesEffectLabel(ctk.CTkLabel):
    def __init__(
        self,
        master,
        images_pack: MouseEventsImagesPack,
        text="",
    ):
        super().__init__(
            master,
            fg_color="transparent",
            text_color="white",
            text=text,
        )
        self.images_pack = images_pack
        self.activate_image("noEvent")

    def activate_image(self, image: Literal["noEvent", "mouseEnter", "mouseClick"]):
        self.configure(image=getattr(self.images_pack, image, None))


# El botón normal de Customtkinter tiene un aspecto
# que en ciertos casos no queremos como el boton de configurar gestos
# que no tiene color de fondo sino un icono que cambia segun los eventos
# del raton
# Como esta configuracion se usara mas veces entonces hice un componente para
# reutilizarlo
class CustomButton(ImagesEffectLabel):
    def __init__(
        self,
        master,
        images_pack: MouseEventsImagesPack,
        text="",
        command: Callable[[], Any] | None = None,
    ):
        super().__init__(master, text=text, images_pack=images_pack)
        self.configure(cursor="hand2", fg_color="#2c2b28", width=46)

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
        self.activate_image("noEvent")
        self.configure(fg_color="#2c2b28")

    def on_enter(self, _):
        self.activate_image("mouseEnter")
        self.configure(fg_color="transparent")


class RegularLabel(ctk.CTkLabel):
    def __init__(
        self,
        master,
        text,
        text_color="#DCE4EE",
        size: int | None = None,
        variant: Literal["regular", "bold"] = "regular",
    ):
        super().__init__(
            master,
            text=text,
            fg_color="transparent",
            text_color=text_color,
            font=AssetRegistry.fonts(size)[variant],
            compound="center",
        )
