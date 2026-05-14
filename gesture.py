import os
import urllib.request
from dataclasses import dataclass
from typing import Callable, List, Literal, Tuple

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from utilityclasses import Finger, HandProfile


# En esta clase se guarda toda la data
# relevante que vamos a utilizar para los gestos
# como el numero de manos que aparecen,
# la cantidad de dedos levantados, etc.
@dataclass(frozen=True)
class GestureData:
    hands: Literal[0, 1, 2] = 0
    visibleFingers: Tuple[List[Finger], List[Finger]] = ([], [])
    profile: Tuple[HandProfile, HandProfile] | None = None


# Cuando el usuario configura un gesto como por ejemplo
# abrir carpeta debe pasar indicar el path de la carpeta como un string
# por ende se crea una instancia de Gesture[str] con "param" con el valor del "path"
@dataclass(frozen=True)
class Gesture:
    name: str
    trigger: Callable[[str | None], None]
    settings: GestureData
    param: str | None = None


# Esta clase se encargara de manejar la logica detectar un gesto
# de forma generica, luego se comparara la data del gesto que el usuario hace
# con la data de los gestos configurados
class GestureRecognition:
    def __init__(self, gestures: List[Gesture]):
        # Data para comparar si hay cambios y entonces ejecutar un nuevo gesto
        self.last_data: GestureData | None = None
        self.current_data: GestureData | None = None

        self.can_do_gesture: bool = True
        self.gestures = gestures

        self.init_model()

    def download_if_not_exists(self, model_path):
        if not os.path.exists(model_path):
            print("Descargando modelo...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)

    def init_model(self, model_path="hand_landmarker.task"):
        self.download_if_not_exists(model_path)
        base_options = python.BaseOptions(model_asset_path=model_path)

        self.options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.detector = vision.HandLandmarker.create_from_options(self.options)

        self.finger_tip_indices = [
            4,
            8,
            12,
            16,
            20,
        ]  # Pulgar, índice, medio, anular, meñique
        self.finger_pip_indices = [3, 6, 10, 14, 18]  # Articulaciones inferiores
        # self.finger_names = ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]
        self.finger_names = [i.value for i in Finger]

    # Condición necesaria para habilitar
    # la ejecucion de gestos tras un gesto hecho
    # Se analiza el frame y si cunple cierta condicion se
    # vuelve True la prop can_do_gesture
    def _check_to_enable_gestures(self, frame):
        self.can_do_gesture = True

    # PRUEBA ESTA FUNCION Y DEBUGGEA LO QUE DEVUELVE
    # Develve la info del frame actual
    # Devuelve None si ninguna de las manos aparecen en la camara
    def _retrieve_gesture_data(self, frame) -> GestureData | None:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        detection_result = self.detector.detect(mp_image)

        hands_info = []
        h, w, _ = frame.shape
        temp = 0

        if detection_result.hand_landmarks:
            for idx, (hand_landmarks, handedness) in enumerate(
                zip(detection_result.hand_landmarks, detection_result.handedness)
            ):
                # Obtener tipo de mano
                hand_type = handedness[0].category_name

                # Convertir landmarks a coordenadas
                landmarks = []
                for lm in hand_landmarks:
                    landmarks.append((lm.x * w, lm.y * h))

                # Contar dedos levantados
                fingers_binary = self._count_fingers_up(landmarks, hand_type)
                temp = sum(fingers_binary)

                # Obtener nombres de dedos levantados
                fingers_up_names = [
                    self.finger_names[i]
                    for i, is_up in enumerate(fingers_binary)
                    if is_up == 1
                ]

                hands_info.append(
                    {
                        "type": hand_type,
                        "fingers": fingers_up_names,
                        # "fingers_count": sum(fingers_binary),
                        # "fingers_binary": fingers_binary,
                    }
                )

        if len(hands_info) + temp != 0:
            print({"num_hands": len(hands_info), "hands": hands_info})

        return None

    def _count_fingers_up(self, landmarks, hand_type):
        """
        Determina qué dedos están levantados
        Returns: lista de 5 enteros (1=levantado, 0=doblado)
        """
        fingers_up = []

        # Pulgar (comparación en X según la mano)
        if hand_type == "Right":
            fingers_up.append(1 if landmarks[4][0] > landmarks[3][0] else 0)
        else:  # Left
            fingers_up.append(1 if landmarks[4][0] < landmarks[3][0] else 0)

        # Otros 4 dedos (comparación en Y)
        for tip_idx, pip_idx in zip(
            self.finger_tip_indices[1:], self.finger_pip_indices[1:]
        ):
            fingers_up.append(1 if landmarks[tip_idx][1] < landmarks[pip_idx][1] else 0)

        return fingers_up

    # Método principal, se encarga de manejar la lógica de ejecución
    # de los gestos
    def exec_on_detection(self, frame):
        # Llamar a __check_to_enable_gestures si la prop can_do_gesture es True entonces ->
        # Obtener el GestureData info del frame actual con el metood __retrieve_gesture_data
        # Si es diferente a la anterior
        # Buscar en la lista de gestos cual data coincide y ejecutar el primero
        # que encuentre

        # cambiar self.can_do_gesture a False hasta que la condicion necesaria se cumpla
        self._retrieve_gesture_data(frame)
