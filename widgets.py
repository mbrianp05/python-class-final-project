import copy
import time
from typing import Any, Callable, List, Literal, cast

import customtkinter as ctk
import cv2
import tksvg
from customtkinter import CTkFrame
from PIL import Image

from actions import get_actions_parameter_type
from gesture import Gesture, GestureRecognition, HandProfile
from loader import AssetRegistry
from parampicker import ParamPicker
from services import fetch_gestures, remove_gesture, update_gesture
from uiclasses import HighlightTransition, MessageType, MouseEventsImagesPack, View
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


class Sidebar(CTkFrame):
    _BG_COLOR = "#30302e"

    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent", width=500)
        self.gestures = fetch_gestures()

        self.controller = controller

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
        self.display_gestures_list()

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

    def display_gestures_list(self):
        for i, gesture in enumerate(self.gestures):
            item = ActivationFeedbackLabel(
                self.scrollable_frame,
                text=shorten_gesture_name(gesture.name),
                font=AssetRegistry.fonts(18)["regular"],
                image=self._get_icon(gesture),
                transition=HighlightTransition(
                    fg_color="#3A8CFF", text_color="#fff", duration=500, pulses=2
                ),
            )

            item.grid(row=i, column=0, sticky="we", padx=10)

    def highlight_gesture(self, index: int = 0):
        labels = list(self.scrollable_frame.children.values())

        if index < len(labels):
            cast(ActivationFeedbackLabel, labels[index]).highlight()

    def update(self):
        labels = list(self.scrollable_frame.children.values())

        for label in labels:
            del label

        self.gestures = fetch_gestures()
        self.display_gestures_list()


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

        self._inner_state = FormState(is_valid=True)
        self._default_gesture()

        self.set_layout()

        self.gesture_info_panel = ctk.CTkFrame(self, fg_color="transparent", width=340)
        self.gesture_info_panel.rowconfigure((0, 1, 2), pad=50)
        self.gesture_info_panel.rowconfigure((3), weight=1)
        self.gesture_info_panel.grid(
            row=0, column=0, sticky="wns", padx=40, pady=(40, 0)
        )

        self.form_panel = ctk.CTkFrame(self, fg_color="transparent", width=600)
        self.form_panel.columnconfigure((0, 1), weight=1, pad=30)
        self.form_panel.grid(row=0, column=1, padx=40, pady=(40, 0))

        self.display_current_gesture_selector()
        self.display_name_field()
        self.display_active_hands_selector()
        self.display_visible_fingers_selector()
        self.display_action_selector()
        self.display_save_settings_button()
        self.display_delete_button()

        self._adjust_current_configuration_display()

    def _default_gesture(self):
        self.current_gesture: Gesture | None = copy.deepcopy(
            self.gestures[0] if len(self.gestures) > 0 else None
        )

    def set_layout(self):
        self.columnconfigure((1), weight=1)

    def display_action_selector(self):
        values = self.get_action_values()

        self.action_selector = ctk.CTkComboBox(
            self.gesture_info_panel,
            values=values,
            width=360,
            height=32,
            state="readonly",
            font=AssetRegistry.fonts()["regular"],
            command=lambda _: self.change_action(),
        )
        self.action_selector.grid(row=1, column=0, columnspan=2, sticky="we")

        self._adjust_current_gesture_effect()
        paramtype = self.get_paramtype_for_current_action()

        self.param_picker = ParamPicker(
            self.gesture_info_panel,
            paramtype=paramtype,
            initial_value=self.get_current_param_value(),
        )
        self.param_picker.grid(row=2, column=0, sticky="w", columnspan=2)

    def change_action(self):
        if self.current_gesture is None:
            return

        self.update_config()
        self._change_param_type_form(change_value=False)

    def get_current_param_value(self) -> float | int | str | bool | None:
        value = None

        if self.current_gesture is not None:
            value = self.current_gesture.param

        return value

    def get_paramtype_for_current_action(self) -> ParamType | None:
        action = get_action_from_repr(self.action_selector.get())

        return get_actions_parameter_type()[action]

    def _change_param_type_form(self, change_value=True):
        required_param_type = get_actions_parameter_type()[self.get_selected_action()]

        value = None

        if self.current_gesture is not None and change_value:
            value = self.get_current_param_value()

        self.param_picker.set_param_type(required_param_type, value)

    def display_name_field(self):
        # APLICAR MAX LENGTH !!!!
        text = "" if self.current_gesture is None else self.current_gesture.name
        self.name_field = ctk.CTkEntry(
            self.gesture_info_panel,
            height=31,
            width=220,
            font=AssetRegistry.fonts()["regular"],
        )
        self.name_field.insert(0, text)
        self.name_field.grid(row=0, column=1, sticky="we")
        self.name_field.bind("<KeyRelease>", lambda _: self._update_name())

    def check_name(self):
        if self.current_gesture is None:
            return

        if self.current_gesture.name == "":
            self._inner_state = FormState(
                False, "El nombre del gesto no ha sido porporcionado"
            )

    def _update_name(self):
        if self.current_gesture is None:
            return

        self.current_gesture.name = self.name_field.get().strip(" \n\r")
        self.check_name()

    # SETEA EL GESTO QUE SE ESTÁ CONFIGURANDO A PARTIR DEL VALOR
    # SELECCIONADO EN EL COMBOBOX DE LOS GESTOS
    def set_current_gesture(self):
        gesture_name = self.gesture_selector.get()
        f = list(filter(lambda g: g.name == gesture_name, self.gestures))

        if len(f) == 0:
            self.current_gesture = None
            return

        self.current_gesture = copy.deepcopy(f[0])
        self._adjust_current_configuration_display()
        self._change_param_type_form()

    def display_current_gesture_selector(self):
        self.gesture_selector = ctk.CTkComboBox(
            self.gesture_info_panel,
            height=31,
            width=220,
            command=lambda _: self.set_current_gesture(),
            state="readonly",
            font=AssetRegistry.fonts()["regular"],
        )

        self._set_current_gesture_selector()

        self.gesture_selector.grid(
            row=0,
            column=0,
            padx=(0, 15),
            sticky="we",
        )

    def _set_current_gesture_selector(self):
        self.gesture_selector.configure(values=[g.name for g in self.gestures])

        if self.current_gesture is not None:
            self.gesture_selector.set(self.current_gesture.name)

    def get_selected_action(self) -> Action:
        selected_action = self.action_selector.get()
        return get_action_from_repr(selected_action)

    # LEE TODOS LOS WIDGETS DEL FORMULARIO Y CAMBIA EL GESTURE DATA
    # DE ACUERDO A LA NUEVA CONFIGURACION
    def update_config(self):
        if self.current_gesture is None:
            return

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

    def no_settings_status(self):
        self.left_hand_activator.deselect()
        self.left_hand_activator.deselect()

        for n, ch in self.checkbox_collection_panel.children.items():
            if n.startswith("!ctkcheckbox"):
                cast(ctk.CTkCheckBox, ch).deselect()

    def get_fingers_selector_checkboxes(self) -> List[ctk.CTkCheckBox]:
        return [
            cast(ctk.CTkCheckBox, ch)
            for n, ch in self.checkbox_collection_panel.children.items()
            if n.startswith("!ctkcheckbox")
        ]

    # Configura el formulario de forma que concuerde con la
    # informacion del gesto que se esta configurando
    def _adjust_current_configuration_display(self):
        if self.current_gesture is None:
            self.no_settings_status()

            return

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
        if self.current_gesture is None:
            return

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
        if self.current_gesture is None:
            return -1

        idx = -1

        for i, g in enumerate(self.gestures):
            if g.id == self.current_gesture.id:
                idx = i

        return idx

    def update_local_gesture(self):
        if self.current_gesture is None:
            return

        idx = self.index_of_local_gesture()

        if idx == -1:
            return

        self.gestures[idx] = self.current_gesture
        self._set_current_gesture_selector()

    def save_new_config(self):
        if self.current_gesture is not None:
            inner_state = self._inner_state
            outer_state = self.param_picker.get_state()

            if inner_state.is_valid and outer_state.is_valid:
                self.current_gesture.param = self.param_picker.get_value()

                update_gesture(self.current_gesture)
                # GUARDAR LA REFERENCIA DEL NUEVO GESTO EN LA LISTA DE GESTOS
                # SE PODIA TAMBEIEN HACER EL fetch_gestures PERO ESO LEE EL JSON
                # POR LO QUE ES MAS CARO A NIVEL DE RENDIMIENTO
                self.update_local_gesture()

        # AQUI LA LOGICA PARA CREAR UN NUEVO GESTO
        # self.display_current_gesture_selector()
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

        # Notifier.get().notify(type, msg or "Hello")

    def display_save_settings_button(self):
        self.save_button = ctk.CTkButton(
            self.gesture_info_panel,
            height=31,
            text="Guardar",
            font=AssetRegistry.fonts()["regular"],
            command=self.save_new_config,
        )
        self.save_button.grid(row=3, column=0, sticky="ws")

    def _remove_local_gesture(self):
        if self.current_gesture is None:
            return

        self.gestures = list(
            filter(lambda g: g.id != self.current_gesture.id, self.gestures)  # type: ignore
        )

    def _delete_current_gesture(self):
        if self.current_gesture is None:
            return

        if self.current_gesture.id == -1:
            return

        result = True

        if confirm("¿Deseas realmente eliminar este gesto?"):
            self._remove_local_gesture()
            result = remove_gesture(self.current_gesture)
        else:
            return

        if result:
            self._default_gesture()
            self._set_current_gesture_selector()
            self._adjust_current_configuration_display()
            self._change_param_type_form()
        else:
            messagebox_error("Error", "No se pudo eliminar el gesto")

    def display_delete_button(self):
        self.delete_button = ctk.CTkButton(
            self.gesture_info_panel,
            height=31,
            text="Eliminar",
            font=AssetRegistry.fonts()["regular"],
            command=self._delete_current_gesture,
        )
        self.delete_button.grid(row=3, column=1, sticky="ws")


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
        self.configure(cursor="hand2", fg_color="#333", width=46)

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
        self.configure(fg_color="#333")

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


# HAY QUE MEJORAR ESTO XD
class FloatingFeedbackLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            text="",
            corner_radius=10,
            padx=20,
            pady=12,
            font=AssetRegistry.fonts()["bold"],
            **kwargs,
        )

        self._after_id = None
        self.master = master

        self._variants = {
            MessageType.ERROR: {
                "bg": "#E53935",
                "fg": "#FFFFFF",
            },
            MessageType.SUCCESS: {
                "bg": "#43A047",
                "fg": "#FFFFFF",
            },
            MessageType.INFO: {
                "bg": "#1E88E5",
                "fg": "#FFFFFF",
            },
        }

        # Configuración inicial
        self.configure(
            fg_color=self._variants[MessageType.INFO]["bg"],
            text_color=self._variants[MessageType.INFO]["fg"],
            justify="left",
        )

    def show_variant(self, message_type: MessageType, text: str, duration: int = 4000):
        self.configure(text=text, fg_color=self._variants[message_type]["bg"])
        self.pack(anchor="nw")

        self._after_id = self.after(duration, self.hide)

    def hide(self):
        self.place_forget()
        self.pack_forget()

        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None


# Label con resaltado para lista de gestos
class ActivationFeedbackLabel(ctk.CTkLabel):
    def __init__(
        self,
        master,
        text: str,
        transition: HighlightTransition,
        font: ctk.CTkFont | None = None,
        image: tksvg.SvgImage | None = None,
        **kwargs,
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
            **kwargs,
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
