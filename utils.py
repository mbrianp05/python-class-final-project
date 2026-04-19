name_max_len = 14


def shorten_gesture_name(name: str) -> str:
    return name[:name_max_len] + "..." if len(name) > name_max_len else name
