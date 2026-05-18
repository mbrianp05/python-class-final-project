import customtkinter as ctk
import tksvg


def load_fonts_files():
    ctk.FontManager.load_font("fonts/InterVariable.ttf")


def get_fonts(size=None):
    return {
        "title": ctk.CTkFont(
            family="Inter Variable", size=25 if size is None else size
        ),
        "bold": ctk.CTkFont(
            family="Inter Variable", size=15 if size is None else size, weight="bold"
        ),
        "regular": ctk.CTkFont(
            family="Inter Variable", size=15 if size is None else size, weight="normal"
        ),
    }


def get_icons(scale: int = 25):
    return {
        "gear": tksvg.SvgImage(file="./icons/gear.svg", scaletoheight=scale),
        "gear_darker": tksvg.SvgImage(
            file="./icons/gear-darker.svg", scaletoheight=scale
        ),
        "generic-gesture": tksvg.SvgImage(
            file="./icons/generic-gesture.svg", scaletoheight=scale
        ),
        "arrow_left": tksvg.SvgImage(
            file="./icons/arrow-left.svg", scaletoheight=scale
        ),
        "arrow_left_darker": tksvg.SvgImage(
            file="./icons/arrow-left-darker.svg", scaletoheight=scale
        ),
        "hand-1": tksvg.SvgImage(file="./icons/hand-1.svg", scaletoheight=scale),
        "hand-2": tksvg.SvgImage(file="./icons/hand-2.svg", scaletoheight=scale),
        "hand-1-darker": tksvg.SvgImage(
            file="./icons/hand-1-darker.svg", scaletoheight=scale
        ),
        "hand-2-darker": tksvg.SvgImage(
            file="./icons/hand-2-darker.svg", scaletoheight=scale
        ),
    }
