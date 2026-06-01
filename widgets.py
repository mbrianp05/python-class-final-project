import copy
import time
from typing import Any, Callable, List, Literal, cast

import customtkinter as ctk
import cv2
import tksvg
from customtkinter import CTkFrame
from PIL import Image

from actions import get_actions_parameter_type
from gesture import Gesture, GestureData, GestureRecognition, HandProfile
from loader import AssetRegistry
from notifier import Notifier
from parampicker import ParamPicker
from services import add_gesture, fetch_gestures, remove_gesture, update_gesture
from uiclasses import MouseEventsImagesPack, View
from universe import BaseResponder, Universe
from utilityclasses import (
    Action,
    Finger,
    FormState,
    Modification,
    ModificationType,
    ParamType,
)
from utils import (
    confirm,
    get_action_from_repr,
    get_color_palette,
    get_hand_profile_from_repr,
    get_or_default,
    get_repr_for_action,
    get_repr_for_hand_profile,
    shorten_gesture_name,
)


class GestureItem(ctk.CTkFrame):
    _HIGHLIGHT_COLOR = "#262624"
    _PULSE_MS = 250  # duracion de cada semiciclo (encendido / apagado)
    _PULSES = 2  # numero de parpadeos completos

    def __init__(
        self,
        master,
        name: str,
        action: Action,
    ):
        super().__init__(master, fg_color="transparent")

        self._name = name
        self._action = action

        self._is_animating = False

        self._build()

    def _get_icon(self, action: Action):
        action_icon_dict = {
            Action.TAKE_SCREENSHOT: AssetRegistry.icons(name="camera"),
            Action.OPEN_FILE: AssetRegistry.icons(name="open_file"),
            Action.OPEN_FOLDER: AssetRegistry.icons(name="open_folder"),
            Action.RUN_PROGRAM: AssetRegistry.icons(name="run_program"),
            Action.SET_WIFI_STATE: AssetRegistry.icons(name="set_wifi"),
            Action.SET_VOLUME: AssetRegistry.icons(name="set_volume"),
        }

        return get_or_default(action_icon_dict, action, None)

    def _get_color(self, action: Action):
        color_dict = {
            Action.SET_WIFI_STATE: "#313e42",
            Action.TAKE_SCREENSHOT: "#28323f",
            Action.OPEN_FOLDER: "#2a3632",
            Action.RUN_PROGRAM: "#43322c",
            Action.SET_VOLUME: "#3a333e",
            Action.OPEN_FILE: "#473d2d",
        }

        return get_or_default(color_dict, action, "transparent")

    def _get_description(self, action: Action):
        color_dict = {
            Action.SET_WIFI_STATE: "Cambiar estado del WIFI",
            Action.TAKE_SCREENSHOT: "Captura de pantalla",
            Action.OPEN_FOLDER: "Abrir carpeta",
            Action.RUN_PROGRAM: "Abrir programa",
            Action.SET_VOLUME: "Cambiar el volumen",
            Action.OPEN_FILE: "Abrir archivo",
        }

        return get_or_default(color_dict, action, "")

    def _build(self) -> None:
        name = self._name
        action = self._action

        self.icon_box = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")

        description_frame = ctk.CTkFrame(self, fg_color="transparent")
        description_frame.rowconfigure((0, 1), weight=1)

        self.name_label = ctk.CTkLabel(
            description_frame,
            text=shorten_gesture_name(name),
            font=AssetRegistry.fonts(16, variant="regular"),
            height=10,
        )
        self.name_label.grid(row=0, column=1, sticky="wns", pady=(2, 0))

        self.desc_label = ctk.CTkLabel(
            description_frame,
            text=self._get_description(action),
            font=AssetRegistry.fonts(13, variant="regular"),
            text_color="#999",
            height=10,
        )
        self.desc_label.grid(row=1, column=1, sticky="wns", pady=4)

        self.icon_label = ctk.CTkLabel(
            self.icon_box,
            text="",
            image=self._get_icon(action),  # type: ignore
            height=40,
            width=40,
            fg_color=self._get_color(action),
            corner_radius=10,
        )
        self.icon_label.grid(row=0, column=0, sticky="ns")

        self.icon_box.grid(row=0, column=0, padx=7, pady=4, rowspan=2)
        description_frame.grid(row=0, column=1, sticky="we", padx=7, pady=4)

    def change_name(self, name: str) -> None:
        self.name_label.configure(text=name)

    def change_description(self, action: Action) -> None:
        self.desc_label.configure(text=self._get_description(action))
        self.icon_label.configure(image=self._get_icon(action))
        self.icon_box.configure(fg_color=self._get_color(action))

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


class Sidebar(CTkFrame, BaseResponder):
    _BG_COLOR = "#30302e"
    _WIDTH = 260

    def __init__(self, master):
        super().__init__(master, fg_color="transparent", width=self._WIDTH)
        self.grid_propagate(False)

        self._gestures = fetch_gestures()

        self._items: List[GestureItem] = []

        self.header_font = AssetRegistry.fonts(variant="title")
        self.bold_font = AssetRegistry.fonts(variant="bold")

        self._set_layout()
        self._create_header()
        self._create_scrollbar_panel()

    def _set_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _create_header(self):
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

        self.configure_gestures_label = NavigationButton(
            self.header,
            image=AssetRegistry.icons("gear"),
            command=lambda: Universe.rise().navigate(View.SETTINGS_VIEW),
        )
        self.configure_gestures_label.grid(row=0, column=0, sticky="wsn")

    def _create_scrollbar_panel(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, orientation="vertical", corner_radius=0, fg_color=self._BG_COLOR
        )
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.grid(row=1, column=0, pady=(1, 0), sticky="nsew")

        self.no_gestures_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No hay ningun gesto",
            font=AssetRegistry.fonts(18, variant="regular"),
            text_color="#999",
        )

        self._display_gestures_list()

    def _no_gestures(self) -> None:
        self.no_gestures_label.grid(row=0, column=0, padx=6, pady=20, sticky="we")

    def _display_gestures_list(self):
        if len(self._gestures) == 0:
            self._no_gestures()

        for i, gesture in enumerate(self._gestures):
            item = GestureItem(
                self.scrollable_frame, name=gesture.name, action=gesture.effect
            )
            item.grid(row=i, column=0, pady=(7, 0), padx=6, sticky="we")
            self._items.append(item)

    def highlight_gesture(self, index: int = 0):
        if index < len(self._items):
            self._items[index].highlight()

    def respond(self, modification: Modification[Gesture]) -> None:
        gesture = modification.data
        matches = [
            idx for idx, local in enumerate(self._gestures) if local.id == gesture.id
        ]

        if modification.type == ModificationType.UPDATE:
            if len(matches) == 0:
                return

            idx = matches[0]
            data = self._gestures[idx]
            item = self._items[idx]

            if data.name != gesture.name:
                item.change_name(gesture.name)

            if data.effect != gesture.effect:
                item.change_description(gesture.effect)

        if modification.type == ModificationType.DELETE:
            if len(matches) == 0:
                return

            idx = matches[0]
            item = self._items[idx]
            self._items.remove(item)

            if len(self._items) == 0:
                self._no_gestures()

            # Esto es importante para darle tiempo a la app
            # a borrar el elemento
            item.after(200, lambda: item.destroy())

        if modification.type == ModificationType.CREATE:
            self.no_gestures_label.grid_forget()

            item = GestureItem(
                self.scrollable_frame, name=gesture.name, action=gesture.effect
            )
            item.grid(row=len(self._items), column=0, pady=(7, 0), padx=6, sticky="we")
            self._items.append(item)

        self._gestures = fetch_gestures()


class Camera(ctk.CTkFrame):
    _BADGE_BLOCKED_BG = get_color_palette()["red_bg"]
    _BADGE_BLOCKED_TEXT = get_color_palette()["red_text"]
    _BADGE_OK_BG = "#28323f"
    _BADGE_OK_TEXT = "#3A8CFF"

    def __init__(self, master, highlighter):
        super().__init__(master)
        self._highlighter = highlighter

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
            image=AssetRegistry.icons(name="camera"),  # type: ignore
            fg_color="transparent",
        )
        self._badge_icon.grid(row=0, column=0, padx=(10, 4), pady=4)

        self._badge_label = ctk.CTkLabel(
            self.detection_badge,
            text="Detección activa",
            font=AssetRegistry.fonts(size=14, variant="regular"),
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

        self.recognizer.exec_on_detection(frame, self._highlighter.highlight_gesture)
        self._update_detection_badge()
        self.camera_frames.after(200, self.load_frames)

    def on_closing(self):
        if getattr(self, "cap", None) is not None:
            self.cap.release()


class SettingsHeader(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")

        self.display_go_back_button()
        self.display_title()

    def display_title(self):
        self.title_label = ctk.CTkLabel(
            self,
            text="Configurar gestos",
            font=AssetRegistry.fonts(variant="title"),
            fg_color="transparent",
            height=50,
        )
        self.title_label.grid(row=0, column=1, padx=15)

    def display_go_back_button(self):
        self.nav_button = NavigationButton(
            self,
            image=AssetRegistry.icons("arrow_left", 30),
            command=lambda: Universe.rise().navigate(View.DETECTION_VIEW),  # type: ignore
        )
        self.nav_button.grid(row=0, column=0, sticky="wsn")


class SettingsForm(ctk.CTkScrollableFrame):
    _HAND_ICON_SCALE = 260

    def __init__(self, master):
        super().__init__(master, orientation="vertical", fg_color="transparent")

        self._gestures = fetch_gestures()

        self._is_new = False

        self._default_gesture()

        self._set_layout()

        self._left_col = ctk.CTkFrame(self, fg_color="transparent")
        self._left_col.rowconfigure(0, weight=1)
        self._left_col.rowconfigure(1, weight=0)
        self._left_col.columnconfigure(0, weight=1)
        self._left_col.grid(row=0, column=0, sticky="nswe", padx=40, pady=(40, 40))

        self._gesture_info_panel = ctk.CTkFrame(
            self._left_col, fg_color="transparent", width=440
        )
        self._gesture_info_panel.grid_propagate(False)

        self._gesture_info_panel.rowconfigure((3, 4), pad=50)
        self._gesture_info_panel.rowconfigure((0, 1, 2), pad=10)

        self._gesture_info_panel.columnconfigure(0, weight=1)
        self._gesture_info_panel.grid(row=0, column=0, sticky="nswe")

        self._form_panel = ctk.CTkFrame(self, fg_color="transparent", width=600)
        self._form_panel.columnconfigure((0, 1), weight=1, pad=30)
        self._form_panel.grid(row=0, column=1, padx=40, pady=(40, 0))

        # form_buttons en _left_col row=1 → siempre al fondo de la columna izquierda
        self._form_buttons = ctk.CTkFrame(
            self._left_col, fg_color="transparent", border_width=0
        )
        self._form_buttons.columnconfigure(0, weight=1)
        self._form_buttons.grid(row=1, column=0, sticky="we", pady=(10, 0))

        self._display_current_gesture_selector()
        self._display_name_field()
        self._display_active_hands_selector()
        self._display_visible_fingers_selector()
        self._display_action_selector()
        self._display_save_settings_button()

        self._notifier = Notifier(self)
        self._adjust_current_configuration_display()

    def _empty_gesture(self):
        default_action = Action.OPEN_FOLDER
        default_settings = GestureData(
            hands=(False, False),
            visibleFingers=([], []),
            profile=(None, None),
        )
        self._current_gesture = Gesture(
            id=-1,
            name="Nuevo gesto",
            settings=default_settings,
            effect=default_action,
            param=None,
        )
        self._original_gesture = copy.deepcopy(self._current_gesture)

    def _default_gesture(self):
        if len(self._gestures) == 0:
            self._empty_gesture()
            self._is_new = True

            return

        self._current_gesture = copy.deepcopy(self._gestures[0])
        self._original_gesture = self._gestures[0]

    def _set_layout(self):
        self.columnconfigure((1), weight=1)

    def _display_action_selector(self):
        values = self._get_action_values()

        self.action_selector = ctk.CTkComboBox(
            self._gesture_info_panel,
            values=values,
            width=10,  # mínimo; sticky="we" + columnconfigure weight=1 lo expande
            height=32,
            state="readonly",
            font=AssetRegistry.fonts(),
            command=lambda _: self._change_action(),
        )
        self.action_selector.grid(row=3, column=0, sticky="we")

        self._adjust_current_gesture_effect()
        paramtype = self._get_paramtype_for_current_action()

        self.param_picker = ParamPicker(
            self._gesture_info_panel,
            paramtype=paramtype,
            initial_value=self._get_current_param_value(),
            on_change=lambda _: self._determine_save_button_state(),
        )
        self.param_picker.grid(row=4, column=0, sticky="we")

    def _change_action(self):
        self._update_config()
        selected_action = self._get_selected_action()
        original_action = None

        if self._original_gesture is not None:
            original_action = self._original_gesture.effect

        self._change_param_type_form(change_value=selected_action == original_action)

    def _get_current_param_value(self) -> float | int | str | bool | None:
        return self._current_gesture.param

    def _get_paramtype_for_current_action(self) -> ParamType | None:
        action = get_action_from_repr(self.action_selector.get())

        return get_actions_parameter_type()[action]

    def _change_param_type_form(self, change_value=True):
        required_param_type = get_actions_parameter_type()[self._get_selected_action()]
        value = self._get_current_param_value() if change_value else None

        self.param_picker.set_param_type(required_param_type, value)

    def _display_name_field(self):
        self.name_field_box = ctk.CTkFrame(self._gesture_info_panel)
        self.name_field_box.columnconfigure(1, weight=1)

        text = self._current_gesture.name
        self.name_field = ctk.CTkEntry(
            self.name_field_box,
            height=31,
            font=AssetRegistry.fonts(),
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
            font=AssetRegistry.fonts(17, variant="regular"),
            image=AssetRegistry.icons("mark", 33),  # type: ignore
        )
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_field_box.grid(row=2, column=0, sticky="we")

    def _get_name_validity(self) -> FormState:
        state = None

        if self._current_gesture.name == "":
            state = FormState(False, "El nombre del gesto no ha sido porporcionado")
        else:
            state = FormState(True, None)

        return state

    def _update_name(self):
        self._current_gesture.name = self.name_field.get().strip(" \n\r")
        self._determine_save_button_state()

    def _display_current_gesture_selector(self):
        self.gesture_selector = GestureBadgeSelector(
            self._gesture_info_panel,
            gestures=self._gestures,
            on_select=lambda id: self._on_badge_selected(id),
            selected_id=self._current_gesture.id if self._current_gesture else -1,
        )
        self.gesture_selector.grid(row=0, column=0, sticky="we", pady=(0, 8))

        _btn_row = ctk.CTkFrame(self._gesture_info_panel, fg_color="transparent")
        _btn_row.grid(row=1, column=0, sticky="w", pady=(0, 16))

        _size = 36

        self.delete_button = ctk.CTkButton(
            _btn_row,
            width=_size,
            height=_size,
            text="",
            fg_color="#391010",
            hover_color="#4d1515",
            corner_radius=_size // 2,
            image=AssetRegistry.icons(name="trash"),
            command=self._delete_current_gesture,
            state=ctk.NORMAL if not self._is_new else ctk.DISABLED,
        )
        self.delete_button.grid(row=0, column=0)

        self.reset_button = ctk.CTkButton(
            _btn_row,
            width=_size,
            height=_size,
            text="",
            fg_color="#1e1e1c",
            hover_color="#2d2d2b",
            corner_radius=_size // 2,
            image=AssetRegistry.icons(name="reset"),
            command=self._reset_form,
            state=ctk.DISABLED,
        )
        self.reset_button.grid(row=0, column=1, padx=(8, 0))

    def _on_badge_selected(self, id: int) -> None:
        if id == -1:
            self._new_gesture()

        matches = [g for g in self._gestures if g.id == id]

        if self.delete_button._state != ctk.NORMAL and id != -1:
            self.delete_button.configure(state=ctk.NORMAL)

        if not matches:
            return

        self._current_gesture = copy.deepcopy(matches[0])
        self._original_gesture = copy.deepcopy(matches[0])

        self._adjust_current_configuration_display()
        self._change_param_type_form()

        if self.save_button._state != ctk.DISABLED:
            self.save_button.configure(state=ctk.DISABLED)

        if self.reset_button._state != ctk.DISABLED:
            self.reset_button.configure(state=ctk.DISABLED)

    def _set_current_gesture_selector(self, modification: Modification | None = None):
        if modification is None:
            self.gesture_selector.set_selected(self._current_gesture.id)

            return

        if modification.type == ModificationType.CREATE:
            self.gesture_selector.insert_badge(
                self._current_gesture.name, self._current_gesture.id
            )
            self.gesture_selector.after(
                300, lambda: self.gesture_selector._parent_canvas.xview_moveto(1.0)
            )

            return

        if modification.type == ModificationType.DELETE:
            self.gesture_selector.remove_badge(self._current_gesture.id)

            return

        if modification.type == ModificationType.UPDATE:
            self.gesture_selector.update_badge(
                self._current_gesture.name, self._current_gesture.id
            )

            return

    def _get_selected_action(self) -> Action:
        selected_action = self.action_selector.get()
        return get_action_from_repr(selected_action)

    # LEE TODOS LOS WIDGETS DEL FORMULARIO Y CAMBIA EL GESTURE DATA
    # DE ACUERDO A LA NUEVA CONFIGURACION
    def _update_config(self):
        settings = self._current_gesture.settings

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
        all_checkboxes = self._get_fingers_selector_checkboxes()
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
        self._current_gesture.effect = self._get_selected_action()

        self._adjust_current_configuration_display()

    def _get_hand_profile_values(self):
        profiles = [
            None,
            HandProfile.PALM,
            HandProfile.FRONT,
        ]

        return [get_repr_for_hand_profile(p) for p in profiles]

    def _get_action_values(self):
        actions = [
            Action.OPEN_FILE,
            Action.OPEN_FOLDER,
            Action.TAKE_SCREENSHOT,
            Action.RUN_PROGRAM,
            Action.SET_VOLUME,
            Action.SET_WIFI_STATE,
        ]

        return [get_repr_for_action(p) for p in actions]

    def _display_active_hands_selector(self):
        # ── Cajas de mano ────────────────────────────────────────────────
        self.left_hand_activator = HandToggleBox(
            self._form_panel,
            icon=AssetRegistry.icons("hand-1", self._HAND_ICON_SCALE),
            icon_active=AssetRegistry.icons("hand-1-darker", self._HAND_ICON_SCALE),
            label="Mano izquierda",
            is_active=False,
            on_toggle=lambda _: self._update_config(),
        )
        self.left_hand_activator.grid(
            row=0, column=0, padx=(0, 8), pady=(0, 16), sticky="we"
        )

        self.right_hand_activator = HandToggleBox(
            self._form_panel,
            icon=AssetRegistry.icons("hand-2", self._HAND_ICON_SCALE),
            icon_active=AssetRegistry.icons("hand-2-darker", self._HAND_ICON_SCALE),
            label="Mano derecha",
            is_active=False,
            on_toggle=lambda _: self._update_config(),
        )
        self.right_hand_activator.grid(
            row=0, column=1, padx=(8, 0), pady=(0, 16), sticky="we"
        )

        # Mantener referencia de icono para compatibilidad con _adjust_current_configuration_display
        self.left_hand_icon = self.left_hand_activator
        self.right_hand_icon = self.right_hand_activator

        # ── Perfil de manos ──────────────────────────────────────────────
        self.profile_label = ctk.CTkLabel(
            self._form_panel,
            text="PERFIL DE LAS MANOS",
            font=AssetRegistry.fonts(17, variant="regular"),
            anchor="w",
        )
        self.profile_label.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 8))

        values = self._get_hand_profile_values()

        self.left_hand_profile_selector = ctk.CTkComboBox(
            self._form_panel,
            width=10,
            height=34,
            state="readonly",
            values=values,
            command=lambda _: self._update_config(),
            font=AssetRegistry.fonts(),
        )
        self.left_hand_profile_selector.set(values[0])
        self.left_hand_profile_selector.grid(row=2, column=0, padx=(0, 8), sticky="we")

        self.right_hand_profile_selector = ctk.CTkComboBox(
            self._form_panel,
            width=10,
            height=34,
            state="readonly",
            values=values,
            command=lambda _: self._update_config(),
            font=AssetRegistry.fonts(),
        )
        self.right_hand_profile_selector.set(values[0])
        self.right_hand_profile_selector.grid(row=2, column=1, padx=(8, 0), sticky="we")

    def _get_fingers_selector_checkboxes(self) -> List[ctk.CTkCheckBox]:
        return [
            cast(ctk.CTkCheckBox, ch)
            for n, ch in self.checkbox_collection_panel.children.items()
            if n.startswith("!ctkcheckbox")
        ]

    def _get_hands_validity(self) -> FormState:
        is_left_active, is_right_active = self._current_gesture.settings.hands
        state = None

        if not is_left_active and not is_right_active:
            state = FormState(
                False, "Al menos una de las dos manos debe ser visible en el gesto"
            )
        else:
            state = FormState(True, None)

        return state

    # Configura el formulario de forma que concuerde con la
    # informacion del gesto que se esta configurando
    def _adjust_current_configuration_display(self):
        hands_fingers = self._current_gesture.settings.visibleFingers

        # ADJUST GESTURE NAME
        self.name_field.delete(0, "end")
        self.name_field.insert(0, self._current_gesture.name)

        # ADJUST HANDS NUMBER AND HAND PROFILE
        is_left_active, is_right_active = self._current_gesture.settings.hands
        set_profile_left, set_profile_right = self._current_gesture.settings.profile

        form_fields = {
            "hand_activator": (self.left_hand_activator, self.right_hand_activator),
            "hand_profile_selector": (
                self.left_hand_profile_selector,
                self.right_hand_profile_selector,
            ),
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
                False: [self._get_hand_profile_values()[0]] * 2,
            },
            "state": {True: "readonly", False: ctk.DISABLED},
        }

        for idx, is_active in enumerate([is_left_active, is_right_active]):
            getattr(
                form_fields["hand_activator"][idx], values["activator"][is_active]
            )()
            form_fields["hand_profile_selector"][idx].set(
                values["profile"][is_active][idx]
            )
            form_fields["hand_profile_selector"][idx].configure(
                state=values["state"][is_active]
            )

        all_checkboxes = self._get_fingers_selector_checkboxes()
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
                else:
                    ch.deselect()

                ch.configure(state=ctk.NORMAL)

        # ADJUST ACTION
        self._adjust_current_gesture_effect()
        self._determine_save_button_state()

    def _adjust_current_gesture_effect(self):
        self.action_selector.set(get_repr_for_action(self._current_gesture.effect))

    def _display_visible_fingers_selector(self):
        fingers_names = ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]
        fingers_repr = [
            Finger.THUMB_FINGER,
            Finger.INDEX_FINGER,
            Finger.MIDDLE_FINGER,
            Finger.RING_FINGER,
            Finger.LITTLE_FINGER,
        ]

        self.checkbox_collection_panel = ctk.CTkFrame(
            self._form_panel, fg_color="transparent"
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
                    command=self._update_config,
                    font=AssetRegistry.fonts(),
                )
                checkbox.grid(row=idx, column=hand_number, pady=10)

                # GUARDAR QUE DEDO REPRESENTA EL CHECKBOX
                setattr(checkbox, "stands_for", fingers_repr[idx])

    def _index_of_local_gesture(self) -> int:
        idx = -1

        for i, g in enumerate(self._gestures):
            if g.id == self._current_gesture.id:
                idx = i

        return idx

    def _update_local_gesture(self):
        idx = self._index_of_local_gesture()

        if idx == -1:
            self._gestures.append(self._current_gesture)
        else:
            self._gestures[idx] = self._current_gesture

        self._original_gesture = self._current_gesture
        type = ModificationType.CREATE if idx == -1 else ModificationType.UPDATE
        self._set_current_gesture_selector(
            Modification(type, data=self._current_gesture)
        )

    def _get_state(self) -> FormState:
        form_state = self._get_name_validity()

        if form_state.is_valid is True:
            form_state = self._get_hands_validity()

        if form_state.is_valid is True:
            form_state = self.param_picker.get_state()

        return form_state

    def _save_new_config(self):
        form_state = self._get_state()

        if form_state.is_valid:
            self.delete_button.configure(state=ctk.NORMAL)

            self._current_gesture.param = self.param_picker.get_value()
            modification_type = ModificationType.UPDATE

            if self._current_gesture.id != -1:
                update_gesture(self._current_gesture)
            else:
                modification_type = ModificationType.CREATE
                gesture_width_id = add_gesture(self._current_gesture)

                if gesture_width_id is not None:
                    self._current_gesture = gesture_width_id

            if self.reset_button._state != ctk.DISABLED:
                self.reset_button.configure(state=ctk.DISABLED)

            if self.save_button._state != ctk.DISABLED:
                self.save_button.configure(state=ctk.DISABLED)

            if self.delete_button._state != ctk.NORMAL:
                self.delete_button.configure(state=ctk.NORMAL)

            Universe.rise().signal(
                Sidebar, Modification(modification_type, self._current_gesture)
            )

            self._update_local_gesture()

        self._feedback_state_or_create_success()

    def _feedback_state_or_create_success(self):
        state = self._get_state()
        is_valid = state.is_valid

        if not is_valid:
            self._notifier.error(message=state.error_message or "")

            return

        self._notifier.success("✨ Gesto guardado exitosamente ✨")

    def _display_save_settings_button(self):
        self.save_button = ctk.CTkButton(
            self._form_buttons,
            height=40,
            text="Guardar cambios",
            text_color="#d4cfff",
            hover_color="#3d3480",
            fg_color="#2d2060",
            corner_radius=10,
            font=AssetRegistry.fonts(15, "bold"),
            image=AssetRegistry.icons(name="save"),
            command=self._save_new_config,
            state=ctk.DISABLED,
        )
        self.save_button.grid(row=0, column=0, sticky="we", padx=0, pady=0)

    def _remove_local_gesture(self):
        self._gestures = [
            gesture
            for gesture in self._gestures
            if gesture.id != self._current_gesture.id
        ]

    def _feedback_remove_gesture(self, is_valid: bool = True):
        notify = self._notifier.success if is_valid else self._notifier.error
        message = "Gesto eliminado 💫" if is_valid else "No se pudo eliminar el gesto"

        notify(message)

    def _delete_current_gesture(self):
        if self._current_gesture.id == -1:
            return

        result = True

        if confirm("¿Deseas realmente eliminar este gesto?"):
            self._remove_local_gesture()
            result = remove_gesture(self._current_gesture)
        else:
            return

        if result:
            Universe.rise().signal(
                Sidebar, Modification(ModificationType.DELETE, self._current_gesture)
            )

            if len(self._gestures) > 0:
                # Eliminar el gesture del gesture selector
                self._set_current_gesture_selector(
                    Modification(ModificationType.DELETE, data=self._current_gesture)
                )
                self._default_gesture()
                # Cambiar al gesture actual
                self._set_current_gesture_selector()

                self._adjust_current_configuration_display()
                self._change_param_type_form()

                self.gesture_selector._parent_canvas.xview_moveto(0.0)
            else:
                self._new_gesture()

            if self.reset_button._state != ctk.DISABLED:
                self.reset_button.configure(state=ctk.DISABLED)

        self._feedback_remove_gesture(result)

    def _determine_save_button_state(self) -> None:
        has_changes = (
            self.name_field.get() != self._original_gesture.name
            or self._current_gesture.effect != self._original_gesture.effect
            or self._original_gesture.param != self.param_picker.get_value()
            or self._current_gesture.settings != self._original_gesture.settings
        )

        state = ctk.NORMAL if has_changes else ctk.DISABLED

        if self.save_button._state != state:
            self.save_button.configure(state=state)

        if self.reset_button._state != state:
            self.reset_button.configure(state=state)

    def _reset_form(self) -> None:
        self._current_gesture = copy.deepcopy(self._original_gesture)
        self._adjust_current_configuration_display()
        self._change_param_type_form()

        self.save_button.configure(state=ctk.DISABLED)
        self.reset_button.configure(state=ctk.DISABLED)

    def _new_gesture(self) -> None:
        self._empty_gesture()

        if self.save_button._state != ctk.DISABLED:
            self.save_button.configure(state=ctk.DISABLED)

        if self.delete_button._state != ctk.DISABLED:
            self.delete_button.configure(state=ctk.DISABLED)

        if self.reset_button._state != ctk.DISABLED:
            self.reset_button.configure(state=ctk.DISABLED)

        ptype = get_actions_parameter_type()[self._current_gesture.effect]

        self.param_picker.set_param_type(ptype, None)
        self._set_current_gesture_selector()
        self._adjust_current_configuration_display()


class HandToggleBox(ctk.CTkFrame):
    _ACTIVE_BG = "#1e1a3a"
    _ACTIVE_BORDER = "#5b50d6"
    _ACTIVE_LABEL = "#9b93ff"

    _INACTIVE_BG = "#1e1e1c"
    _INACTIVE_BORDER = "#2d2d2b"
    _INACTIVE_LABEL = "#555550"

    def __init__(
        self,
        master,
        icon: tksvg.SvgImage,
        icon_active: tksvg.SvgImage,
        label: str,
        is_active: bool = False,
        on_toggle: "Callable[[bool], None] | None" = None,
    ):
        super().__init__(
            master,
            corner_radius=14,
            border_width=2,
            cursor="hand2",
        )

        self._is_active = is_active
        self._on_toggle = on_toggle
        self._icon = icon
        self._icon_active = icon_active

        self.columnconfigure(0, weight=1)

        self._icon_label = ctk.CTkLabel(
            self,
            text="",
            image=icon,  # type: ignore
            fg_color="transparent",
        )
        self._icon_label.grid(row=0, column=0, padx=20, pady=(16, 6))

        self._text_label = ctk.CTkLabel(
            self,
            text=label,
            font=AssetRegistry.fonts(17, variant="regular"),
            fg_color="transparent",
        )
        self._text_label.grid(row=1, column=0, padx=20, pady=(0, 14))

        # Capturar clic en el frame y en sus hijos
        for widget in (self, self._icon_label, self._text_label):
            widget.bind("<ButtonRelease-1>", self._handle_click)

        self._apply_style()

    # ── API pública ───────────────────────────────────────────────────────

    def get(self) -> bool:
        return self._is_active

    def set(self, value: bool) -> None:
        if self._is_active != value:
            self._is_active = value
            self._apply_style()

    def select(self) -> None:
        self.set(True)

    def deselect(self) -> None:
        self.set(False)

    # ── Internos ─────────────────────────────────────────────────────────

    def _handle_click(self, _) -> None:
        self._is_active = not self._is_active
        self._apply_style()
        if self._on_toggle:
            self._on_toggle(self._is_active)

    def _apply_style(self) -> None:
        if self._is_active:
            self.configure(
                fg_color=self._ACTIVE_BG,
                border_color=self._ACTIVE_BORDER,
            )
            self._text_label.configure(text_color=self._ACTIVE_LABEL)
            self._icon_label.configure(image=self._icon_active)
        else:
            self.configure(
                fg_color=self._INACTIVE_BG,
                border_color=self._INACTIVE_BORDER,
            )
            self._text_label.configure(text_color=self._INACTIVE_LABEL)
            self._icon_label.configure(image=self._icon)


class GestureBadgeSelector(ctk.CTkScrollableFrame):
    _BADGE_NORMAL_BG = "#252523"
    _BADGE_NORMAL_BORDER = "#3a3a38"
    _BADGE_NORMAL_TEXT = "#b0ada8"

    _BADGE_ACTIVE_BG = "#1e1a3a"
    _BADGE_ACTIVE_BORDER = "#5b50d6"
    _BADGE_ACTIVE_TEXT = "#c4bfff"

    def __init__(
        self,
        master,
        selected_id: int,
        gestures: List[Gesture],
        on_select: Callable[[int], None] | None = None,
        **kwargs,
    ):
        super().__init__(
            master,
            orientation="horizontal",
            fg_color="transparent",
            height=52,
            **kwargs,
        )
        self._on_select = on_select
        self._selected = selected_id
        self._badges: dict[int, ctk.CTkFrame] = {}

        self.refresh(gestures, selected_id)

    # ── API pública ───────────────────────────────────────────────────────

    def set_selected(self, id: int) -> bool:
        """Marca el badge con un id determinado devuelve si era diferente al ya marcado"""
        old = self._selected

        if old == id:
            return False

        self._selected = id

        if old in self._badges:
            self._style_badge(self._badges[old], active=False)
        if id in self._badges:
            self._style_badge(self._badges[id], active=True)

        return True

    def get(self) -> int:
        return self._selected

    def refresh(self, gestures: List[Gesture], selected_id: int) -> None:
        """Destruye todos los badges y los recrea con la nueva lista."""
        for w in list(self._badges.values()):
            w.destroy()

        self._badges.clear()

        """Añadir badge para crear gesto"""
        self._add_badge("Nuevo", -1)

        for gesture in gestures:
            self._add_badge(gesture.name, gesture.id)

        if selected_id:
            self.set_selected(selected_id)

    def insert_badge(self, name: str, id: int) -> None:
        self._add_badge(name, id)
        self.set_selected(id)

    def update_badge(self, name: str, id: int) -> None:
        badge = self._badges[id]
        label = badge.winfo_children()[0] if badge.winfo_children() else None

        if label is None:
            return

        label.configure(text=name)

    def remove_badge(self, id: int) -> None:
        self._badges[id].after(400, self._badges[id].destroy)
        self._badges.pop(id)

    # ── Internos ─────────────────────────────────────────────────────────

    def _add_badge(self, name: str, id: int) -> None:
        is_new = id == -1

        badge = ctk.CTkFrame(
            self,
            corner_radius=20,
            border_width=1,
            cursor="hand2",
        )
        label = ctk.CTkLabel(
            badge,
            text=name if not is_new else f" {name}",
            font=AssetRegistry.fonts(16, "regular"),
            image=AssetRegistry.icons("add", 23) if is_new else None,  # type: ignore
            compound="left",
            fg_color="transparent",
        )
        label.grid(row=0, column=0, padx=14, pady=6)

        self._style_badge(badge, active=(id == self._selected))

        for widget in (badge, label):
            widget.bind("<ButtonRelease-1>", lambda _, n=id: self._handle_click(n))

        badge.pack(side="left", padx=(0, 6), pady=4)
        self._badges[id] = badge

    def _style_badge(
        self,
        badge: ctk.CTkFrame,
        active: bool,
    ) -> None:
        label = badge.winfo_children()[0] if badge.winfo_children() else None

        if active:
            badge.configure(
                fg_color=self._BADGE_ACTIVE_BG, border_color=self._BADGE_ACTIVE_BORDER
            )
            if label:
                label.configure(
                    text_color=self._BADGE_ACTIVE_TEXT,
                )
        else:
            badge.configure(
                fg_color=self._BADGE_NORMAL_BG, border_color=self._BADGE_NORMAL_BORDER
            )
            if label:
                label.configure(
                    text_color=self._BADGE_NORMAL_TEXT,
                )

    def _handle_click(self, id: int) -> None:
        changed = self.set_selected(id)

        if self._on_select and changed:
            self._on_select(id)


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


class NavigationButton(ctk.CTkFrame):
    _NORMAL_COLOR = "#404040"
    _HOVER_COLOR = "#2d2d2b"

    def __init__(
        self,
        master,
        image: tksvg.SvgImage,
        command: Callable[[], Any] | None = None,
    ):
        super().__init__(
            master,
            cursor="hand2",
            fg_color=self._NORMAL_COLOR,
            width=46,
            height=46,
            corner_radius=0,
        )
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._image_label = ctk.CTkLabel(self, text="", image=image)  # type: ignore
        self._image_label.grid(row=0, column=0, sticky="nswe")

        self.command = command

        self._image_label.bind("<Enter>", self.on_enter)
        self._image_label.bind("<Leave>", self.on_leave)
        self._image_label.bind("<ButtonRelease-1>", self.on_click)

    def on_click(self, _):
        if self.command is not None:
            self.command()

    def on_leave(self, _):
        self.configure(fg_color=self._NORMAL_COLOR)

    def on_enter(self, _):
        self.configure(fg_color=self._HOVER_COLOR)
