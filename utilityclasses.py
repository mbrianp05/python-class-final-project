from enum import StrEnum

# AQUI IRAN TODAS LAS CLASES RELACIONADAS CON LA LOGICA


class Finger(StrEnum):
    THUMB_FINGER = "thumb"
    INDEX_FINGER = "index_finger"
    MIDDLE_FINGER = "middle_finger"
    RING_FINGER = "ring_finger"
    LITTLE_FINGER = "little_finger"


# Para saber la "orientación" de la mano
# Empezaremos por estas pero se puede incrementar
# para detectar gestos con la parte lateral de la mano
# o con el puño orientado a la camara, etc.
class HandProfile(StrEnum):
    PALM = "palm"
    FRONT = "front"
